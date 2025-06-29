from django.contrib.auth.models import User
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect, render, reverse

from poynter.points.models import Project, Space, Ticket
from poynter.points.ops import get_votes_for_space


def home(request):
    "List spaces - projects and their pointing moderators"
    projects = Project.objects.all()
    open_spaces = Space.objects.filter(is_open=True)
    return render(request, "points/home.html", {"projects": projects, "open_spaces": open_spaces})


def about(request):
    return render(request, "points/about.html")


def space(request, space_name: str):
    "Detail view for a voting space has permanent URL for a moderator and project."
    space = get_object_or_404(Space, slug=space_name)
    numbers = [(1, "One"), (2, "Two"), (3, "Three"), (5, "Five"), (8, "Eight"), (13, "Thirteen")]

    try:
        active_ticket = space.ticket_set.get(active=True)
    except Ticket.DoesNotExist:
        active_ticket = None

    tallies = get_votes_for_space(space_name)

    # Space members and their voting status
    # {"joe": 13, "erin": 5}
    members = {}
    num_voted = 0
    if active_ticket:
        for member in space.members.all():
            member_vote = None
            # Member has voted on this ticket
            if member.username in tallies.get(active_ticket.id, {}).keys():
                member_vote = tallies[active_ticket.id][member.username]
                num_voted += 1
            members[member] = member_vote

    all_voted = num_voted == space.members.count()

    return render(
        request,
        "points/space.html",
        {
            "space": space,
            "active_ticket": active_ticket,
            "numbers": numbers,
            "tallies": tallies,
            "members": members,
            "all_voted": all_voted,
        },
    )


def join_leave_space(request, space_name: str):
    "Allow member to join or leave a space. Simple toggle."

    space = get_object_or_404(Space, slug=space_name)
    if request.user in space.members.all():
        space.members.remove(request.user)
    else:
        space.members.add(request.user)

    return redirect(reverse("points:space", kwargs={"space_name": space.slug}))


def open_close_ticket(request, ticket_id: int):
    "Allow moderator to open or close a ticket in a space. Simple toggle."

    ticket = get_object_or_404(Ticket, id=ticket_id)
    space = ticket.space
    ticket.voted = not ticket.voted
    ticket.save()

    # Try to find next active ticket automatically
    space.ticket_set.all().update(active=None)
    next_active = space.ticket_set.filter(voted=False).first()
    if next_active:
        next_active.active = True
        next_active.save()

    return redirect(reverse("points:space", kwargs={"space_name": space.slug}))


def activate_ticket(request, space_name: str, ticket_id: int):
    """Allow moderator to make a ticket active in a space. Simple toggle.
    Must set other active tickets to null first.
    """

    space = get_object_or_404(Space, slug=space_name)
    ticket = get_object_or_404(Ticket, id=ticket_id)
    space.ticket_set.all().update(active=None)
    ticket.active = True
    ticket.voted = False
    ticket.save()

    return redirect(reverse("points:space", kwargs={"space_name": space.slug}))


def open_close_space(request, space_name: str):
    "Allow moderator to open or close a space for voting. Simple toggle."

    space = get_object_or_404(Space, slug=space_name)
    space.is_open = False if space.is_open else True
    space.save()

    return redirect(reverse("points:space", kwargs={"space_name": space.slug}))


def boot_users(request, space_name: str):
    "Allow moderator to remove users from a space."

    space = get_object_or_404(Space, slug=space_name)
    usernames = request.GET.getlist("usernames")
    for username in usernames:
        user = User.objects.get(username=username)
        space.members.remove(user)

    return redirect(reverse("points:space", kwargs={"space_name": space.slug}))


def clear_space_cache(request, space_name: str):
    "Allow moderator to refresh a space cache."

    cache.delete(space_name)

    return redirect(reverse("points:space", kwargs={"space_name": space_name}))
