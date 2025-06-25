from django.urls import path

from poynter.points import views, views_htmx

app_name = "points"

urlpatterns = [
    # path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("votes/", views.votes, name="votes"),
    path("space/<str:slug>", views.space, name="space"),
    path("join_leave_space/<str:slug>", views.join_leave_space, name="join_leave_space"),
    path("tally/single/", views_htmx.tally_single, name="tally_single"),
]
