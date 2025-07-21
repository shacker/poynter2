from collections import defaultdict

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from poynter.points.models import Space, Ticket


def rt_send_message(request):
    """Receive a message via POST and broadcast via WebSockets to all clients."""
    if request.method == "POST":
        message_text = request.POST.get("message", "").strip()
        # TODO replace room_name with space_name everywhere
        room_name = request.POST.get("room_name", "general")

        if message_text:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"broadcast_{room_name}", {"type": "broadcast_message", "message": message_text}
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


def display_ticket_table(request, space_name: str):
    "HTMX view returns appropriate ticket list for given user in this space."
    "Updates in real time as moderator makes changes."
    space = get_object_or_404(Space, slug=space_name)
    current_tickets = space.ticket_set.filter(archived=False)
    ctx = {"space": space, "current_tickets": current_tickets}

    return render(request, "points/_display_ticket_table.html", ctx)


def display_ticket_control(request, space_name: str):
    "Display ticket table control links for moderator only."
    "These controls rendered in a separate table to avoid complex "
    "content filtering (permissions) over async broadcast."
    space = get_object_or_404(Space, slug=space_name)
    current_tickets = space.ticket_set.filter(archived=False)
    ctx = {"space": space, "current_tickets": current_tickets}

    return render(request, "points/_display_ticket_control.html", ctx)


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
    """HTMX view displays voting buttons. Should not be displayed
    when there is no active ticket.
    """

    space = get_object_or_404(Space, slug=space_name)
    try:
        active_ticket = space.ticket_set.get(active=True)
    except Ticket.DoesNotExist:
        active_ticket = None

    return render(request, "points/htmx/display_voting_row.html", {"active_ticket": active_ticket})


def refresh_widgets(request, ticket):
    """Helper, not a view. When moderator actives or opens/closes a ticket,
    redraw affected multiple widgets."""

    channel_layer = get_channel_layer()

    # Refresh active ticket display
    async_to_sync(channel_layer.group_send)(
        f"broadcast_{ticket.space.slug}",
        {
            "type": "broadcast_html_update",
            "html_content": display_active_ticket(request, ticket.space.slug).content.decode(
                "utf-8"
            ),
            "target_element": "display_active_ticket",
        },
    )

    # Refresh ticket_table
    async_to_sync(channel_layer.group_send)(
        f"broadcast_{ticket.space.slug}",
        {
            "type": "broadcast_html_update",
            "html_content": display_ticket_table(request, ticket.space.slug).content.decode(
                "utf-8"
            ),
            "target_element": "display_ticket_table",
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
    refresh_widgets(request, ticket)

    return HttpResponse(status=204)


def open_close_ticket(request, ticket_id: int):
    "Allow moderator to open or close a ticket in a space. Simple toggle."

    ticket = get_object_or_404(Ticket, id=ticket_id)
    ticket.closed = not ticket.closed

    # Prevent logical impossibility:
    if ticket.closed:
        ticket.active = False

    ticket.save()
    refresh_widgets(request, ticket)

    return HttpResponse(status=204)
