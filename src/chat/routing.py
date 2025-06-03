# --------------------------------------------------------------------------
# Description: Routing configuration for the chat application's WebSockets.
# --------------------------------------------------------------------------
from django.urls import path

from . import consumers

websocket_urlpatterns = [
    # re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    # Using path for simplicity, can be changed to re_path for more complex room names
    path("ws/chat/<str:room_name>/", consumers.ChatConsumer.as_asgi()),
]
