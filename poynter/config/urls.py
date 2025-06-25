from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

from poynter.someapp.views import home, send_user_mail

urlpatterns = [
    path("", home, name="home"),
    path("send_email", send_user_mail, name="send_user_mail"),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("-/", include("django_alive.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
