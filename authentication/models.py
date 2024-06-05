from django.db import models
from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.contrib.auth import get_user_model


# User Model
class User(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(unique=False, max_length=50, db_index=True)
    username = models.CharField(max_length=150, unique=False, null=True)
    full_name = models.CharField(max_length=30, null=True, blank=True)
    dob = models.DateTimeField(null=True, blank=True)
    gender = models.CharField(max_length=10)
    intro = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(null=True, upload_to="users")
    phone = models.CharField(null=True, max_length=20)
    location = models.TextField(null=True, blank=True)
    latitude = models.CharField(null=True, max_length=30)
    longitude = models.CharField(null=True, max_length=30)
    point = models.PointField(null=True)
    stripe_customer_id = models.CharField(null=True, max_length=50)
    email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_profile_setup = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    device_token = models.TextField(null=True, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)    

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def save(self, *args, **kwargs):
        # self.username = self.username.replace(" ", "").lower()
        super().save(*args, **kwargs)


# Reset Password
class PasswordReset(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset for {self.user.username}"
