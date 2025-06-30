from django.urls import path

from . import consumers

# Holds URL patterns for websocket URLs, consumed by asgi.py
websocket_urlpatterns = [
    path("ws/broadcast/", consumers.BroadcastConsumer.as_asgi()),
]
