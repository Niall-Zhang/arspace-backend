from django.urls import path, re_path

from chat.consumers import ConnectSocket,PrivateRoomChat,EventGroupChat

websocket_urlpatterns = [
    path("ws/connect", ConnectSocket.as_asgi()),
    path("ws/private/<uuid:uuid>", PrivateRoomChat.as_asgi()),
    path("ws/group/<uuid:uuid>", EventGroupChat.as_asgi()),
]
