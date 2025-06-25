from django.shortcuts import get_object_or_404, redirect, render, reverse

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


def open_close_ticket(request, slug: str, ticket_id):
    "Allow moderator to open or close a ticket in a space. Simple toggle."

    space = get_object_or_404(Space, slug=slug)
    ticket = get_object_or_404(Ticket, id=ticket_id)
    ticket.voted = not ticket.voted
    ticket.save()

    return redirect(reverse("points:space", kwargs={"slug": space.slug}))


def activate_ticket(request, slug: str, ticket_id):
    """Allow moderator to make a ticket active or inactive in a space. Simple toggle.
    Must set other active tickets to null first.
    """

    space = get_object_or_404(Space, slug=slug)
    ticket = get_object_or_404(Ticket, id=ticket_id)
    space.ticket_set.all().update(active=None)
    ticket.active = not ticket.active
    ticket.save()

    return redirect(reverse("points:space", kwargs={"slug": space.slug}))
