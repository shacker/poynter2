from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

from poynter.points.views import home as points_home

urlpatterns = [
    path("", points_home, name="points_home"),
    path("points/", include("poynter.points.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("-/", include("django_alive.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
