from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse

from poynter.points.forms import AddTicketForm
from poynter.points.models import Project, Snapshot, Space, Ticket
from poynter.points.ops import get_votes_for_space


def home(request):
    "List spaces - projects and their pointing moderators"
    projects = Project.objects.all()
    open_spaces = Space.objects.filter(is_open=True)
    return render(request, "points/home.html", {"projects": projects, "open_spaces": open_spaces})


def space(request, space_name: str):
    "Detail view for a voting space has permanent URL for a moderator and project."
    space = get_object_or_404(Space, slug=space_name)
    numbers = [(1, "One"), (2, "Two"), (3, "Three"), (5, "Five"), (8, "Eight"), (13, "Thirteen")]
    room_name = space.slug

    try:
        active_ticket = space.ticket_set.get(active=True)
    except Ticket.DoesNotExist:
        active_ticket = None

    current_tickets = space.ticket_set.filter(archived=False)
    tallies = get_votes_for_space(space_name)

    # Space members and their voting status
    # {"joe": 13, "erin": 5}
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
        "points/space.html",
        {
            "active_ticket": active_ticket,
            "all_voted": all_voted,
            "current_tickets": current_tickets,
            "members": members,
            "numbers": numbers,
            "space": space,
            "tallies": tallies,
            "host": request.get_host(),
            "room_name": room_name,
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
    ticket.closed = not ticket.closed
    ticket.save()

    return redirect(reverse("points:space", kwargs={"space_name": space.slug}))


def activate_ticket(request, space_name: str, ticket_id: int):
    """Allow moderator to make a ticket active in a space. Simple toggle.
    Must set other active tickets to null first.
    """

    space = get_object_or_404(Space, slug=space_name)
    ticket = get_object_or_404(Ticket, id=ticket_id)
    space.ticket_set.all().update(active=None)
    ticket.active = True
    ticket.closed = False
    ticket.save()

    return redirect(reverse("points:space", kwargs={"space_name": space.slug}))


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

    return redirect(reverse("points:space", kwargs={"space_name": space.slug}))


def archive_tickets(request, space_name: str):
    """When next week's voting comes, we need to get old tickets out of the way.
    Set those to archived=True (different from closed).
    """

    space = get_object_or_404(Space, slug=space_name)
    tickets = Ticket.objects.filter(space=space, archived=False)
    tickets.update(archived=True)

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


def add_ticket(request, space_name: str):
    "Allow moderator to add a ticket to a space"

    if request.method == "POST":
        form = AddTicketForm(request.POST)
        space = get_object_or_404(Space, slug=space_name)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.space = space
            ticket.save()
            return redirect(reverse("points:space", kwargs={"space_name": space_name}))

    else:
        form = AddTicketForm()

    return render(request, "points/add_ticket.html", {"form": form, "space_name": space_name})


def rt_send_message(request):
    if request.method == "POST":
        message_text = request.POST.get("message", "").strip()
        room_name = request.POST.get("room_name", "general")

        if message_text:

            # Broadcast to all connected clients
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"broadcast_{room_name}", {"type": "broadcast_message", "message": message_text}
            )

    # Return empty response for HTMX
    return HttpResponse("")
