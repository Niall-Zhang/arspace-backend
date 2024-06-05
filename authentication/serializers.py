from rest_framework import serializers
from utils.constants import (
    CLUB,
    INCORRECT_USERNAME_EMAIL_PASSWORD,
    INVALID_USER_TYPE,
    UNAUTHORIZED_ACCESS,
    USER,
    USER_IS_INACTIVE,
    USER_IS_UNVERIFIED,
)


from .models import User
from django.contrib.auth.password_validation import validate_password
from django.db.models import Avg
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate


# User Registration Serializer
class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data.get("password"))
        return super().create(validated_data)


# User Login Serializer
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    is_staff = serializers.BooleanField()

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        is_staff = data.get("is_staff")
        user = authenticate(email=username, password=password)
        if user:
            if user.is_staff is not is_staff:
                raise serializers.ValidationError(UNAUTHORIZED_ACCESS)
            elif not user.is_active:
                raise serializers.ValidationError(USER_IS_INACTIVE)
            elif not user.email_verified:
                raise serializers.ValidationError(USER_IS_UNVERIFIED)

            return user
        else:
            raise serializers.ValidationError(INCORRECT_USERNAME_EMAIL_PASSWORD)


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
