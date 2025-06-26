from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.contrib.auth.models import User
from poynter.points.models import Project, Space, Ticket


def home(request):
    "List spaces - projects and their pointing moderators"
    projects = Project.objects.all()
    open_spaces = Space.objects.filter(is_open=True)
    return render(request, "points/home.html", {"projects": projects, "open_spaces": open_spaces})


def about(request):
    return render(request, "points/about.html")


def space(request, slug: str):
    "Detail view for a voting space has permanent URL for a moderator and project."
    space = get_object_or_404(Space, slug=slug)
    numbers = [(1, "One"), (2, "Two"), (3, "Three"), (5, "Five"), (8, "Eight"), (13, "Thirteen")]

    try:
        active_ticket = space.ticket_set.get(active=True)
    except Ticket.DoesNotExist:
        active_ticket = None

    return render(
        request,
        "points/space.html",
        {"space": space, "active_ticket": active_ticket, "numbers": numbers},
    )


def join_leave_space(request, slug: str):
    "Allow member to join or leave a space. Simple toggle."

    space = get_object_or_404(Space, slug=slug)
    if request.user in space.members.all():
        space.members.remove(request.user)
    else:
        space.members.add(request.user)

    return redirect(reverse("points:space", kwargs={"slug": space.slug}))


def open_close_ticket(request, slug: str, ticket_id: int):
    "Allow moderator to open or close a ticket in a space. Simple toggle."

    space = get_object_or_404(Space, slug=slug)
    ticket = get_object_or_404(Ticket, id=ticket_id)
    ticket.voted = not ticket.voted
    ticket.save()

    return redirect(reverse("points:space", kwargs={"slug": space.slug}))


def activate_ticket(request, slug: str, ticket_id: int):
    """Allow moderator to make a ticket active in a space. Simple toggle.
    Must set other active tickets to null first.
    """

    space = get_object_or_404(Space, slug=slug)
    ticket = get_object_or_404(Ticket, id=ticket_id)
    space.ticket_set.all().update(active=None)
    ticket.active = True
    ticket.voted = False
    ticket.save()

    return redirect(reverse("points:space", kwargs={"slug": space.slug}))


def open_close_space(request, slug: str):
    "Allow moderator to open or close a space for voting. Simple toggle."

    space = get_object_or_404(Space, slug=slug)
    space.is_open = False if space.is_open else True
    space.save()

    return redirect(reverse("points:space", kwargs={"slug": space.slug}))


def boot_users(request, slug: str):
    "Allow moderator to remove users from a space."

    space = get_object_or_404(Space, slug=slug)
    usernames = request.GET.getlist("usernames")
    for username in usernames:
        user = User.objects.get(username=username)
        space.members.remove(user)

    return redirect(reverse("points:space", kwargs={"slug": space.slug}))
