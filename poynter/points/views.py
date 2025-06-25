from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.timezone import datetime

from poynter.points.forms import VoteForm
from poynter.points.models import Project, Space, Ticket, Vote


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


def votes(request):
    "Filtered list of votes"
    votes = Vote.objects.all()
    return render(request, "points/votes.html", {"votes": votes})
