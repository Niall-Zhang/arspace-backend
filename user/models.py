from django.db import models
from authentication.models import User
import uuid
from base.models import Interest
from chat.models import Room
from club.models import Event

# User Block Model
class UserBlock(models.Model):
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE)
    blocked_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blocked_by", null=True
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = "user_block"


# User Images
class UserImage(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(null=True, upload_to="user_images")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = "user_images"
        indexes = [models.Index(fields=["uuid"])]

    def __str__(self):
        return self.image


# User Interest
class UserInterest(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = "user_interests"
        indexes = [models.Index(fields=["uuid"])]

    def __str__(self):
        return self.interest


# User Card
class UserCard(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=35, null=True, blank=True)
    card_token = models.CharField(max_length=35)
    default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = "user_cards"
        indexes = [models.Index(fields=["uuid"])]


# Favourite User
class FavouriteUser(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user_liked = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_liked"
    )
    user_liked_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_liked_by"
    )
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="event_id", db_column='event_id', null=True)
    status = models.BooleanField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = "favourite_users"
        indexes = [models.Index(fields=["uuid"])]


# Chat Request
class ChatRequest(models.Model):
    STATUSES = (
        ("pending", "pending"),
        ("accepted", "accepted"),
        ("rejected", "rejected"),
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="receiver"
    )
    status = models.CharField(max_length=15, choices=STATUSES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = "chat_requests"
        indexes = [models.Index(fields=["uuid"])]


# Notification
class Notification(models.Model):
    TYPES = (
        ('event', 'event'),
        ('room', 'room'),
        ('like', 'like'),
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.TextField(null=True)
    message = models.TextField(null=True)
    type = models.CharField(max_length=15, choices=TYPES)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
    liked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,related_name="liked_by")
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)