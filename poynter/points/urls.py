from django.urls import path

from poynter.points import views, views_htmx

app_name = "points"

urlpatterns = [
    path("add_ticket/<str:space_name>", views.add_ticket, name="add_ticket"),
    path("archive_tickets/<str:space_name>", views.archive_tickets, name="archive_tickets"),
    path("boot_users/<str:space_name>", views.boot_users, name="boot_users"),
    path("clear_space_cache/<str:space_name>", views.clear_space_cache, name="clear_space_cache"),
    path("space/<str:space_name>", views.space, name="space"),
    # HTMX views
    path("tally/single/", views_htmx.tally_single, name="tally_single"),
    path(
        "display_ticket_table/<str:space_name>",
        views_htmx.display_ticket_table,
        name="display_ticket_table",
    ),
    path(
        "display_ticket_control/<str:space_name>",
        views_htmx.display_ticket_control,
        name="display_ticket_control",
    ),
    path(
        "display_active_ticket/<str:space_name>",
        views_htmx.display_active_ticket,
        name="display_active_ticket",
    ),
    path(
        "display_voting_row/<str:space_name>",
        views_htmx.display_voting_row,
        name="display_voting_row",
    ),
    path(
        "display_members/<str:space_name>",
        views_htmx.display_members,
        name="display_members",
    ),
    path("join_leave_space/<str:space_name>", views_htmx.join_leave_space, name="join_leave_space"),
    path("rt_send/", views_htmx.rt_send_message, name="rt_send_message"),
    path(
        "activate_ticket/<str:space_name>/<int:ticket_id>",
        views_htmx.activate_ticket,
        name="activate_ticket",
    ),
    path(
        "open_close_ticket/<int:ticket_id>",
        views_htmx.open_close_ticket,
        name="open_close_ticket",
    ),
    path("open_close_space/<str:space_name>", views_htmx.open_close_space, name="open_close_space"),
]
