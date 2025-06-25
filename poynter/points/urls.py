from django.urls import path

from poynter.points import views, views_htmx

app_name = "points"

urlpatterns = [
    path("about/", views.about, name="about"),
    path("space/<str:slug>", views.space, name="space"),
    path("join_leave_space/<str:slug>", views.join_leave_space, name="join_leave_space"),
    path(
        "open_close_ticket/<str:slug>/<int:ticket_id>",
        views.open_close_ticket,
        name="open_close_ticket",
    ),
    path(
        "activate_ticket/<str:slug>/<int:ticket_id>", views.activate_ticket, name="activate_ticket"
    ),
    path("open_close_space/<str:slug>", views.open_close_space, name="open_close_space"),
    path("boot_users/<str:slug>", views.boot_users, name="boot_users"),
    path("tally/single/", views_htmx.tally_single, name="tally_single"),
]
