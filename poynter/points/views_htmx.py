from collections import defaultdict

from django.core.cache import cache
from django.shortcuts import get_object_or_404, render

from poynter.points.models import Space, Ticket

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


def display_active_ticket(request, space_name: str):
    """HTMX view displays linked ticket currently being voted on."""

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


def display_moderator_tools(request, space_name: str):
    """HTMX view displays various controls to the moderator,
    which must be sensitive to the current state.
    """

    space = get_object_or_404(Space, slug=space_name)

    return render(
        request,
        "points/htmx/display_moderator_tools.html",
        {
            "space": space,
        },
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


def get_votes_for_space(space_name: str) -> dict:
    """
    Get all votes for current workspace with computed averages appended.
    Average may not fit an existing Fibonacci number - up to moderator
    to assign final average from returned value. Ticket db IDs are keys in
    this dict.

    # TODO: MOve to ops?

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

    append averages as a final dict:
    {
        "averages": {
            8: 2.5,
            17: 5.5
        }
    }

    """

    avgs = {}
    data = cache.get(space_name, defaultdict(dict))
    for key in data.keys():
        vals = data[key].values()
        avg = sum(vals) / len(vals)
        avgs[key] = avg

    data["averages"] = avgs

    # default_dict is unhashable - cast back
    return dict(data)
