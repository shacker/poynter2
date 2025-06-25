from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import redirect, render, reverse

from poynter.someapp.models import Dummy


def home(request):
    """
    Single view verifies that these services are wired up correctly on
    an AppPack server instance:

    """

    ctx = {}

    return render(request, "home.html", ctx)


def send_user_mail(request):
    """Send a test email.
    Important: You must have configured the environment variable `TEST_EMAIL_TO=you@energy-solution.com`
    and have enabled this server instance to send email during setup and in code.
    """

    if settings.TEST_EMAIL_TO:
        try:
            send_mail(
                "Test subject",
                "Here is the message body.",
                settings.DEFAULT_FROM_EMAIL,
                [settings.TEST_EMAIL_TO],
                fail_silently=False,
            )
            messages.success(request, "Email sent successfully")
        except:
            messages.error(request, "Could not send email. Check logs and configuration.")
    else:
        messages.error(request, "No value found for settings.TEST_EMAIL_TO.")

    return redirect(reverse("home"))
