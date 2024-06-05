from rest_framework import serializers
from authentication.models import User
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from base.models import Interest
from chat.models import Room
from chat.serializers import RoomSerializer
from club.models import Event
from user.models import (
    FavouriteUser,
    UserBlock,
    UserCard,
    UserImage,
    UserInterest,
    ChatRequest,
)
from utils.constants import DATA, SUCCESS
from utils.stripe import create_card_token
from utils.utils import rename_file
from django.contrib.gis.geos import Point
import logging
logger = logging.getLogger(__name__)

class UUIDRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return str(value.uuid)

    def to_internal_value(self, data):
        return self.queryset.get(uuid=data)


# User Image Serializer
class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserImage
        fields = ("uuid", "image")


# User Interest Serializer
class UserInterestSerializer(serializers.ModelSerializer):
    uuid = serializers.CharField(source="interest.uuid")
    title = serializers.CharField(source="interest.title")

    class Meta:
        model = UserInterest
        fields = ["uuid", "title"]


# To get user profile info
class UserProfileSerializer(serializers.ModelSerializer):
    images = UserImageSerializer(many=True, read_only=True, source="userimage_set")
    interests = UserInterestSerializer(
        many=True, read_only=True, source="userinterest_set"
    )
    room = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "uuid",
            "email",
            "full_name",
            "dob",
            "gender",
            "intro",
            "profile_picture",
            "phone",
            "location",
            "latitude",
            "longitude",
            "email_verified",
            "is_active",
            "is_staff",
            "is_profile_setup",
            "device_token",
            "last_seen",
            "interests",
            "images",
            "room"
        ]
        extra_kwargs = {"password": {"write_only": True, "required": False}}


    def get_room(self, obj):
        try:
            # Get the current user from request
            if self.context:
                user = self.context['request'].user
                logger.info(f"room_sender_id: {user.id}, room_receiver_id: {obj.id}")
                logger.info(f"room_sender_id: {obj.id}, room_receiver_id: {user.id}")
                # Filter room where the current user is either sender or receiver
                room = Room.objects.filter(
                    Q(room_sender_id=user.id, room_receiver_id=obj.id) | Q(room_sender_id=obj.id, room_receiver_id=user.id)
                )
                if room.exists():
                    logger.info(f"get_room(), room: {room}")
                    # Serialize filtered rooms
                    serializer = RoomSerializer(room.first())
                    return serializer.data
            return None
        except (AttributeError, FileNotFoundError, Exception) as ex:
            logger.error(f"get_room(), error: {str(ex)}")
            return None

# To update the user profile info
class UpdateUserProfileSerializer(serializers.ModelSerializer):
    images = UserImageSerializer(many=True, read_only=True, source="userimage_set")
    interests = UserInterestSerializer(
        many=True, read_only=True, source="userinterest_set"
    )

    class Meta:
        model = User
        fields = [
            "uuid",
            "email",
            "full_name",
            "dob",
            "gender",
            "intro",
            "profile_picture",
            "phone",
            "location",
            "latitude",
            "longitude",
            "email_verified",
            "is_active",
            "is_profile_setup",
            "device_token",
            "last_seen",
            "interests",
            "images",
        ]
        extra_kwargs = {"password": {"write_only": True, "required": False}}

    def update(self, instance, validated_data):
        if self.context.get("request"):
            # Save Point
            longitude = self.context.get("request").POST.get("longitude")
            latitude = self.context.get("request").POST.get("latitude")
            if longitude and latitude:
                point = Point(float(longitude), float(latitude))
                instance.point = point
            profile_picture = self.context.get("request").FILES.get("profile_picture")
            response = rename_file(profile_picture)
            if response[SUCCESS]:
                profile_picture.name = response[DATA]
            images_data = self.context.get("request").FILES.getlist("images")
            if images_data and len(images_data) > 0:
                for image in images_data:                     
                    UserImage.objects.create(user=instance, image=image)
            get_interests = self.context.get("request").POST.get("interests")
            if get_interests:
                # Clear existing interests for the user
                instance.userinterest_set.all().delete()
                interests = get_interests.split(",")
                for interest_uuid in interests:
                    interest = Interest.objects.get(uuid=interest_uuid)
                    UserInterest.objects.create(user=instance, interest=interest)
        # Update the User model instance
        instance = super().update(instance, validated_data)
        return instance
    
     


# User Block Serializer
class UserBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBlock
        fields = "__all__"


# User Card Serializer
class UserCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCard
        fields = ("uuid", "name","card_token", "default")

    # Create
    def create(self, validated_data):
        stripe_customer_id = self.context.get("request").user.stripe_customer_id
        payload = {}
        payload['user_id'] = self.context.get("request").user.id
        payload['stripe_customer_id'] = stripe_customer_id
        payload['number'] = self.context.get("request").data.get("number")
        payload['exp_month'] = self.context.get("request").data.get("exp_month")
        payload['exp_year'] = self.context.get("request").data.get("exp_year")
        payload['cvc'] = self.context.get("request").data.get("cvc")
        payload['card_token'] = self.context.get("request").data.get("card_token")
        
        # data = attach_card_to_customer(stripe_customer_id, card_token)
        create_card = create_card_token(payload)
        if create_card[SUCCESS]:
            card = UserCard.objects.create(**validated_data)
            return card
        return None


# Favourite User Serializer
class FavouriteUserSerializer(serializers.ModelSerializer):
    # receiver = UUIDRelatedField(queryset=User.objects.all(), required=True)
    # sender = UUIDRelatedField(queryset=User.objects.all(), required=True)

    class Meta:
        model = FavouriteUser
        fields = ("uuid", "user_liked", "user_liked_by", 'event_id', 'status')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user_liked"] = {
            "uuid": instance.user_liked.uuid,
            "full_name": instance.user_liked.full_name,
            "email": instance.user_liked.email,
        }
        representation["user_liked_by"] = {
            "uuid": instance.user_liked_by.uuid,
            "full_name": instance.user_liked_by.full_name,
            "email": instance.user_liked_by.email,
        }
        return representation


# Chat Request Serializer
class ChatRequestSerializer(serializers.ModelSerializer):
    receiver = UUIDRelatedField(queryset=User.objects.all(), required=True)
    sender = UUIDRelatedField(queryset=User.objects.all(), required=True)

    class Meta:
        model = ChatRequest
        fields = ("uuid", "sender", "receiver", "status")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["sender"] = {
            "uuid": instance.sender.uuid,
            "full_name": instance.sender.full_name,
            "email": instance.sender.email,
        }
        representation["receiver"] = {
            "uuid": instance.receiver.uuid,
            "full_name": instance.receiver.full_name,
            "email": instance.receiver.email,
        }
        return representation
