from django.shortcuts import get_object_or_404, render

from poynter.points.models import Space, Ticket
from poynter.points.ops import get_votes_for_space

""" These are HTMX "partial views" that just render HTML for one portion of a view.
These are triggered for re/generation on page load or when calling ops.refresh_widgets().
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


def display_moderator_tools(request, space_name: str):
    """HTMX view displays various controls to the moderator,
    which must be sensitive to the current state.
    """

    space = get_object_or_404(Space, slug=space_name)
    try:
        active_ticket = space.ticket_set.get(active=True)
    except Ticket.DoesNotExist:
        active_ticket = None

    return render(
        request,
        "points/htmx/display_moderator_tools.html",
        {
            "space": space,
            "active_ticket": active_ticket,
        },
    )


def display_members(request, space_name: str):
    """HTMX view displays list of currently active space members
    (and their votes, once voting is closed). Tallies are stored in cache
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
    if active_ticket:
        for member in space.members.all():
            member_vote = None
            if member.username in tallies.get(active_ticket.id, {}).keys():
                member_vote = tallies[active_ticket.id][member.username]
            members[member] = member_vote
    else:
        # Still need to show members list when no active ticket
        for member in space.members.all():
            members[member] = None

    return render(
        request,
        "points/htmx/display_members.html",
        {
            "active_ticket": active_ticket,
            "space": space,
            "members": members,
        },
    )
