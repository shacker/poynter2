from django.urls import path

from poynter.points import views, views_htmx

app_name = "points"

urlpatterns = [
    path("add_ticket/<str:space_name>", views.add_ticket, name="add_ticket"),
    path(
        "activate_ticket/<str:space_name>/<int:ticket_id>",
        views.activate_ticket,
        name="activate_ticket",
    ),
    path("archive_tickets/<str:space_name>", views.archive_tickets, name="archive_tickets"),
    path("boot_users/<str:space_name>", views.boot_users, name="boot_users"),
    path("clear_space_cache/<str:space_name>", views.clear_space_cache, name="clear_space_cache"),
    path("join_leave_space/<str:space_name>", views.join_leave_space, name="join_leave_space"),
    path("open_close_space/<str:space_name>", views.open_close_space, name="open_close_space"),
    path(
        "open_close_ticket/<int:ticket_id>",
        views.open_close_ticket,
        name="open_close_ticket",
    ),
    path("space/<str:space_name>", views.space, name="space"),
    path("tally/single/", views_htmx.tally_single, name="tally_single"),
]
