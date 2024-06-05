from django.urls import path
from chat.v1.views import (
    NotificationListView,
    NotificationInfoView,
    RoomsListView,
    MessageListView,
    upload_attachment,
)

urlpatterns = [
    path("notifications", NotificationListView.as_view(), name="notifications"),
    path("notifications/<uuid:uuid>", NotificationInfoView.as_view(), name="notifications-info"),
    path("rooms", RoomsListView.as_view(), name="rooms"),
    path("messages/<uuid:uuid>", MessageListView.as_view(), name="messages"),
    path("upload-attachment", upload_attachment, name="upload-attachment"),
]
