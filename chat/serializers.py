# chat/serializers.py

from rest_framework import serializers
from authentication.models import User
from club.models import Event, EventImage
from club.serializers import EventImageSerializer
from user.models import Notification
from utils.constants import FALSE
from utils.utils import to_utc_timestamp
from .models import Message, Room
from django.utils.dateformat import format
from django.utils import timezone


class UUIDRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return str(value.uuid)

    def to_internal_value(self, data):
        return self.queryset.get(uuid=data)


# Notification
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "uuid",
            "title",
            "message",
            "type",            
            "status",
            "room",
            "event",
            "liked_by",
            "created_at",
            "updated_at",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.liked_by:
            representation["liked_by"] = {
                "uuid": instance.liked_by.uuid,
                "email": instance.liked_by.email
            } 
        else:
            representation["event"] = None
        if instance.event:
            representation["event"] = {
                "uuid": instance.event.uuid,
                "title": instance.event.title
            } 
        else:
            representation["event"] = None
        if instance.room:
            representation["room"] = {
                "uuid": instance.room.uuid,
                "name": instance.room.name,
                "type": instance.room.type,
            } 
        else:
            representation["room"] = None
        return representation

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id",
            "message",
            "message_sender",
            "room",
            "attachment",
            "created_at",
            "updated_at",
        ]  

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.message_sender: 
            representation["message_sender"] = {
                "uuid": instance.message_sender.uuid,
                "full_name": instance.message_sender.full_name,
                "first_name": instance.message_sender.first_name,
                "last_name": instance.message_sender.last_name,
                "profile_picture": instance.message_sender.profile_picture.url
                if instance.message_sender.profile_picture
                else None,
            }
        else:
            representation['message_sender'] = None
        representation["room"] = {
            "uuid": instance.room.uuid,
            "name": instance.room.name,
            "type": instance.room.type,
        }
        representation['created_at_utc'] = to_utc_timestamp("created_at",instance.created_at)
        return representation


# Room Serializer
class RoomSerializer(serializers.ModelSerializer):
    event = UUIDRelatedField(queryset=Event.objects.all(), required=True)
    room_sender = UUIDRelatedField(queryset=User.objects.all(), required=True)
    room_receiver = UUIDRelatedField(queryset=User.objects.all(), required=True)
    latest_message = serializers.SerializerMethodField()
    latest_messages_count = serializers.SerializerMethodField()

    # Get Event Images
    def get_event_images(self, event_instance):
        event_images = EventImage.objects.filter(event=event_instance)
        if event_images.exists():
            return EventImageSerializer(event_images, many=True).data
        else:
            return None

    class Meta:
        model = Room
        fields = [
            "uuid",
            "name",
            "event",
            "type",
            "room_sender",
            "room_receiver",
            "latest_message",
            "latest_messages_count",
            "created_at",
            "updated_at",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.event:
            representation["event"] = {
                "uuid": instance.event.uuid,
                "title": instance.event.title,
                "images": self.get_event_images(instance.event),
            }
        else:
            representation["event"] = None
        if instance.room_sender:
            representation["room_sender"] = {
                "uuid": instance.room_sender.uuid,
                "full_name": instance.room_sender.full_name,
                "first_name": instance.room_sender.first_name,
                "last_name": instance.room_sender.last_name,
                "email": instance.room_sender.email,
                "profile_picture": instance.room_sender.profile_picture.url
                if instance.room_sender.profile_picture
                else None,
            }
        else:
            representation["room_sender"] = None

        if instance.room_receiver:
            representation["room_receiver"] = {
                "uuid": instance.room_receiver.uuid,
                "full_name": instance.room_receiver.full_name,
                "first_name": instance.room_receiver.first_name,
                "last_name": instance.room_receiver.last_name,
                "email": instance.room_receiver.email,
                "profile_picture": instance.room_receiver.profile_picture.url
                if instance.room_receiver.profile_picture
                else None,
            }
        else:
            representation["room_receiver"] = None
        return representation

    def get_latest_message(self, instance):
        last_message = instance.last_message 
        if last_message:
            sender_uuid = last_message.message_sender.uuid if last_message.message_sender else None
            return {
                "sender": sender_uuid,
                "message": last_message.message,
                "attachment": last_message.attachment,
                "created_at": last_message.created_at,
            }
        return None
    
    def get_latest_messages_count(self,instance):
        try:
            messages = Message.objects.filter(room=instance,status=FALSE).count()
            return messages
        except Exception as ex:
            return None
        
    

# Message User Serializer
class UserMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "uuid",
            "email",
            "profile_picture",
        ]


# Message Room Serializer
class RoomMessageSerializer(serializers.ModelSerializer):
    room_sender_info = UserMessageSerializer(source="room_sender", read_only=True)
    room_receiver_info = UserMessageSerializer(source="room_receiver", read_only=True)

    class Meta:
        model = Room
        fields = ["uuid", "name","event", "room_sender_info", "room_receiver_info"]


# Get Message Serializer
class GetMessageSerializer(serializers.ModelSerializer):
    # message_sender = UserMessageSerializer(source="sender", read_only=True)
    # room_info = RoomMessageSerializer(source="room", read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "message",
            "message_sender",
            "room",
            "attachment",
            "created_at",
            "updated_at",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["message_sender"] = {
            "uuid": str(instance.message_sender.uuid), 
            "full_name": instance.message_sender.full_name,
            "first_name": instance.message_sender.first_name,
            "last_name": instance.message_sender.last_name,
            "profile_picture": instance.message_sender.profile_picture.url
            if instance.message_sender.profile_picture
            else None,
        }
        representation["room"] = {
            "uuid": str(instance.room.uuid), 
            "name": instance.room.name,
            "type": instance.room.type,
        }
        representation['created_at_utc'] = to_utc_timestamp("created_at",instance.created_at)
        return representation