from rest_framework import serializers
from utils.constants import (
    INCORRECT_USERNAME_EMAIL_PASSWORD,
    USER_IS_INACTIVE,
    USER_IS_UNVERIFIED,
)

from base.models import Interest


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ["uuid", "title"]        


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


# Password Reset
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


# Password Reset Confirm
class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    password = serializers.CharField(write_only=True)
