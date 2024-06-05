from django.db import models
import uuid
from authentication.models import User
from club.models import Event

# Room
class Room(models.Model):
    TYPES = (
        ("private", "private"),
        ("group", "group"),
        ("notification", "notification")

    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="event",null=True
    )
    room_sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="room_sender", null=True
    )
    room_receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="room_receiver", null=True
    )
    type = models.CharField(max_length=15, choices=TYPES, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def last_message(self):
        return self.messages.order_by("-created_at").first()


# Message
class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="messages")
    message_sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="message_sender", null=True
    )
    message = models.TextField()
    attachment = models.CharField(max_length=100, blank=True, null=True)
    status = models.BooleanField(default=False, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
