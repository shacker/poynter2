from django.urls import path

from . import consumers

# Holds URL patterns for websocket URLs, consumed by asgi.py
websocket_urlpatterns = [
    path("ws/broadcast/<str:space_name>", consumers.BroadcastConsumer.as_asgi()),
]
