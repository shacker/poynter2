from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect, render, reverse

from poynter.points.forms import AddTicketForm
from poynter.points.models import Project, Space, Ticket
from poynter.points.ops import refresh_unicast_widgets


def home(request):
    "List spaces - projects and their pointing moderators"
    projects = Project.objects.all()
    return render(request, "points/home.html", {"projects": projects})


def space(request, space_name: str):
    "Detail view for a voting space has permanent URL for a moderator and project."
    space = get_object_or_404(Space, slug=space_name)

    # Can we remove this?
    try:
        active_ticket = space.ticket_set.get(active=True)
    except Ticket.DoesNotExist:
        active_ticket = None

    # current_tickets = space.ticket_set.filter(archived=False)

    return render(
        request,
        "points/space.html",
        {
            "active_ticket": active_ticket,
            # "current_tickets": current_tickets,
            "space": space,
            "host": request.get_host(),
        },
    )


def archive_tickets(request, space_name: str):
    """When next week's voting comes, we need to get old tickets out of the way.
    Set those to archived=True (different from closed). Archived tickets cannot be active.
    """

    space = get_object_or_404(Space, slug=space_name)
    tickets = Ticket.objects.filter(space=space, archived=False)
    tickets.update(archived=True, active=False)

    return redirect(reverse("points:space", kwargs={"space_name": space.slug}))


def clear_space_cache(request, space_name: str):
    "Allow moderator to refresh a space cache."

    cache.delete(space_name)

    return redirect(reverse("points:space", kwargs={"space_name": space_name}))


def add_ticket(request, space_name: str):
    "Allow moderator to add a ticket to a space"

    if request.method == "POST":
        space = get_object_or_404(Space, slug=space_name)
        form = AddTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.space = space
            ticket.save()

            # Update everyone else's display
            refresh_unicast_widgets(space_name, ["display_ticket_table"])

            return redirect(reverse("points:space", kwargs={"space_name": space_name}))

    else:
        form = AddTicketForm()

    return render(request, "points/add_ticket.html", {"form": form, "space_name": space_name})
