"""
WSGI config for testrunner project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "poynter.config.settings")

application = get_wsgi_application()

# Enable BasicAuth for all non-prod server instances:
# apppack -a [yourserver/pipeline] config set WSGI_AUTH_CREDENTIALS=esn:solutions
if "WSGI_AUTH_CREDENTIALS" in os.environ:
    import wsgi_basic_auth

    application = wsgi_basic_auth.BasicAuth(application, exclude_paths=["/-/"])
