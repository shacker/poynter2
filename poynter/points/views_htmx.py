from collections import defaultdict

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from poynter.points.models import Snapshot, Space, Ticket
from poynter.points.ops import get_votes_for_space

"""Two kinds of functions in this module:
- Standard HTMX "partial views" that just render HTML for one part of a view.
    In this case, a "view" is really a partial. All of these use `return render(...)`
- Helper functions that don't render a partial, but execute some logic and then
    call another helper to reach out and redraw all affected widgets.
    All of these use `return HttpResponse(status=204)` (do nothing for HTTP)
    These could really be moved to `operations` since they're not technically views.
"""


def display_ticket_table(request, space_name: str):
    "HTMX view returns appropriate ticket list for given user in this space."
    "Updates in real time as moderator makes changes."
    space = get_object_or_404(Space, slug=space_name)
    current_tickets = space.ticket_set.filter(archived=False)
    ctx = {"space": space, "current_tickets": current_tickets}

    return render(request, "points/htmx/display_ticket_table.html", ctx)


def display_ticket_control(request, space_name: str):
    "Display ticket table control links for moderator only."
    "These controls rendered in a separate table to avoid complex "
    "content filtering (permissions) over async broadcast."
    space = get_object_or_404(Space, slug=space_name)
    current_tickets = space.ticket_set.filter(archived=False)
    ctx = {"space": space, "current_tickets": current_tickets}

    return render(request, "points/htmx/display_ticket_control.html", ctx)


def display_active_ticket(request, space_name: str):
    """HTMX view displays linked ticket currently being voted on.
    Dynamic since it needs to be updated independently when
    moderator changes what's active on the board.
    """

    space = get_object_or_404(Space, slug=space_name)
    try:
        active_ticket = space.ticket_set.get(active=True)
    except Ticket.DoesNotExist:
        active_ticket = None

    return render(
        request, "points/htmx/display_active_ticket.html", {"active_ticket": active_ticket}
    )


def display_voting_row(request, space_name: str):
    """HTMX view displays voting buttons to voting members
    when space is open and an active ticket exists.
    """

    space = get_object_or_404(Space, slug=space_name)
    numbers = [(1, "One"), (2, "Two"), (3, "Three"), (5, "Five"), (8, "Eight"), (13, "Thirteen")]

    try:
        active_ticket = space.ticket_set.get(active=True)
    except Ticket.DoesNotExist:
        active_ticket = None

    return render(
        request,
        "points/htmx/display_voting_row.html",
        {"active_ticket": active_ticket, "space": space, "numbers": numbers},
    )


def display_members(request, space_name: str):
    """HTMX view displays list of currently active space members
    (and their votes to participants). tallies are stored in redis_cache
    until voting is closed, then copied to Snapshot.
    """

    space = get_object_or_404(Space, slug=space_name)

    try:
        active_ticket = space.ticket_set.get(active=True)
    except Ticket.DoesNotExist:
        active_ticket = None

    # Space members and their voting status
    # {"joe": 13, "erin": 5}
    tallies = get_votes_for_space(space_name)
    members = {}
    num_voted = 0
    if active_ticket:
        for member in space.members.all():
            member_vote = None
            if member.username in tallies.get(active_ticket.id, {}).keys():
                member_vote = tallies[active_ticket.id][member.username]
                num_voted += 1
            members[member] = member_vote
    else:
        # Still need to show members list when no active ticket
        for member in space.members.all():
            members[member] = None

    all_voted = num_voted == space.members.count()

    return render(
        request,
        "points/htmx/display_members.html",
        {
            "active_ticket": active_ticket,
            "space": space,
            "members": members,
            "all_voted": all_voted,
        },
    )


def activate_ticket(request, space_name: str, ticket_id: int):
    """Allow moderator to make a ticket active/inactive in a space.
    Must set other active tickets to null first. After db is updated,
    also update active ticket display for all other members in this space,
    AND update the ticket_table, which is a separate HTML element.
    """

    space = get_object_or_404(Space, slug=space_name)
    ticket = get_object_or_404(Ticket, id=ticket_id)
    space.ticket_set.all().update(active=None)
    ticket.active = not ticket.active

    # Prevent logical impossibility
    if ticket.active:
        ticket.closed = False

    ticket.save()
    refresh_widgets(request, space_name)

    return HttpResponse(status=204)


def open_close_ticket(request, ticket_id: int):
    "Allow moderator to open or close a ticket in a space. Simple toggle."

    ticket = get_object_or_404(Ticket, id=ticket_id)
    ticket.closed = not ticket.closed

    # Prevent logical impossibility:
    if ticket.closed:
        ticket.active = False

    ticket.save()
    refresh_widgets(request, ticket.space.slug)

    return HttpResponse(status=204)


def open_close_space(request, space_name: str):
    """Allow moderator to open or close a space for voting. Simple toggle.
    Closing a space also auto-saves a snapshot of vote state for posterity.
    """

    space = get_object_or_404(Space, slug=space_name)
    space.is_open = False if space.is_open else True
    space.save()

    if not space.is_open:
        # Get voting state (with averages) from cache
        votes_data = get_votes_for_space(space_name)
        Snapshot.objects.create(space=space, snapshot=votes_data)

    refresh_widgets(request, space_name)

    return HttpResponse(status=204)


def join_leave_space(request, space_name: str):
    "Allow member to join or leave a space. Simple toggle."

    space = get_object_or_404(Space, slug=space_name)
    if request.user in space.members.all():
        space.members.remove(request.user)
    else:
        space.members.add(request.user)

    refresh_widgets(request, space_name)

    return HttpResponse(status=204)


def rt_send_message(request):
    """Receive a message via POST and broadcast via WebSockets to all clients."""
    if request.method == "POST":
        message_text = request.POST.get("message", "").strip()
        space_name = request.POST.get("space_name", "general")

        if message_text:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"broadcast_{space_name}", {"type": "broadcast_message", "message": message_text}
            )

    # Return empty response for HTMX
    return HttpResponse(status=204)  # Do nothing


def tally_single(request):
    """HTMX view receives POST from a voting space, and logs
    the space name, username, and vote. All votes in a given space
    are entered into the same shared object in redis - one per space, not
    one per vote or one per user.

    Space structure in cache is like:

    {
        8: {
            "rob": 3,
            "joe": 2,
        },
        17: {
            "rob": 8,
            "erin": 3,
        }
    }

    Where 8 and 17 are ticket IDs, and within those we have usernames and
    those users' votes.

    """
    if request.method == "POST":
        vote = request.POST

        space_name = vote.get("space")  # same as cache key
        username = vote.get("username")
        ticket = int(vote.get("ticket"))
        choice = int(vote.get("number"))  # Cast numeric choice to int for mathing

        # If cache for space is expired or non-existent, default to empty dict
        # Use defaultdict as fallback so we can nest keys/vals without checking.
        # To allow user to override their vote, we write every time.
        # Keep space cache for one hour unless reset by moderator
        data = cache.get(space_name, defaultdict(dict))
        data[ticket][username] = choice
        cache.set(space_name, data, 3600)

    return HttpResponse(status=204)  # Do nothing


def refresh_widgets(request, space_name: str):
    """Helper, not a view. When moderator activates or opens/closes a ticket,
    the redraw must affect multiple widgets, in a mix of broadcast and unicast.

    Call the broadcast widgets in prescribed order, then issue a single refresh
    request to all unicast widgets (currently only one).

    Note that target elements have names that match the functions that control them,
    i.e.  <div id="display_ticket_table"> is refreshed by `views.display_ticket_table()`

    TODO: We currently update all widgets when any of them change. Optimize by
    having this function only update a list of requested widgets - all won't scale.
    """

    channel_layer = get_channel_layer()
    channel_name = f"broadcast_{space_name}"

    update_elems = {
        "display_active_ticket": display_active_ticket,
        "display_ticket_table": display_ticket_table,
        "display_members": display_members,
    }

    # Call updates in sequence
    for elem_name, handler in update_elems.items():
        html_content = handler(request, space_name)
        async_to_sync(channel_layer.group_send)(
            channel_name,
            {
                "type": "broadcast_html_update",
                "html_content": html_content.content.decode("utf-8"),
                "target_element": elem_name,
            },
        )

    # Do not send html content or element for unicast updates -
    # all will retrieve on their own with this single call
    async_to_sync(channel_layer.group_send)(
        channel_name,
        {
            "type": "unicast_html_update",
        },
    )
