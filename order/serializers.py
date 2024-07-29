from chat.models import Room
from rest_framework import serializers
from authentication.models import User
from datetime import datetime
from chat.serializers import RoomSerializer
from order.models import Order, OrderItem
from club.models import Event, EventImage, Ticket
from user.models import FavouriteUser, UserImage
from user.serializers import UserInterestSerializer
from django.utils.dateformat import format
from django.utils import timezone

from utils.utils import event_to_utc_timestamp, to_utc_timestamp

class UUIDRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return str(value.uuid)

    def to_internal_value(self, data):
        return self.queryset.get(uuid=data)


# User Event Serializer
class UserSerializer(serializers.ModelSerializer):
    # images = UserImageSerializer(many=True, read_only=True, source="userimage_set")

    class Meta:
        model = User
        fields = [
            "uuid",
            "full_name",           
            "profile_picture"            
        ]

# OrderItem Serializer
class OrderItemSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()

    # Get Event Images
    def get_event_images(self, event_instance):
        event_images = EventImage.objects.filter(event=event_instance)
        if event_images.exists():
            return EventImageSerializer(event_images, many=True).data
        else:
            return None
    class Meta:
        model = OrderItem
        fields = [
            'uuid',
            "order",
            "ticket",
            'price',
            "created_at",
            "updated_at",
            "status"
        ]

    def get_price(self, obj):
        if obj.price:
            return obj.price
        return None
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["event"] = {
            "uuid": instance.order.event.uuid,
            "name": instance.order.event.title,
            "date": instance.order.event.date,
            "time": instance.order.event.time,
            "location": instance.order.event.location,
            "images": self.get_event_images(instance.order.event),
            "created_at_utc":event_to_utc_timestamp(instance.order.event.date,instance.order.event.time)
        }
        if instance.ticket:
            representation["ticket"] = {
                "uuid": instance.ticket.uuid,
                "name": instance.ticket.name,
            }
        else:
            representation["ticket"] = None
        representation["order"] = {
            "uuid": instance.order.uuid,
            "qty": instance.order.qty,
            "total": instance.order.total,
            "status": instance.order.payment_status,
            "type": instance.order.type,
        }
        return representation
    
# Event Image Serializer
class EventImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventImage
        fields = ['uuid', 'image']
    
# Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    event = UUIDRelatedField(queryset=Event.objects.all(), required=True)
    order_items = serializers.SerializerMethodField()
    other_paid_users = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = [
            'uuid',
            "event",
            "qty",
            "payment_status",
            "order_items",
            "other_paid_users",
            "type",
            "created_at",
            "updated_at",
        ]

    def get_order_items(self, instance):
        order_items = OrderItem.objects.filter(order=instance)
        serializer = OrderItemSerializer(order_items, many=True)
        return serializer.data
    
    def get_other_paid_users(self, obj):
        # Get other users who have paid for the same event
        other_paid_orders = Order.objects.filter(event=obj.event).exclude(user=obj.user)
        other_paid_users = set(order.user for order in other_paid_orders)

        # Serialize the other users
        serialized_users = UserSerializer(other_paid_users, many=True).data
        return serialized_users

    # Get Event Images
    def get_event_images(self, event_instance):
        event_images = EventImage.objects.filter(event=event_instance)
        if event_images.exists():
            return EventImageSerializer(event_images, many=True).data
        else:
            return None
        
    # Get Event Room
    def get_event_room(self,event_instance):
        try: 
            event_room = Room.objects.get(event=event_instance)
            return RoomSerializer(event_room).data
        except Exception as ex:
            return None
        
    

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["event"] = {
            "uuid": instance.event.uuid,
            "title": instance.event.title,
            "date": instance.event.date,
            "time": instance.event.time,
            "club_contact_no": instance.event.club.contact_no,
            "latitude": instance.event.latitude,
            "longitude": instance.event.longitude,
            "location": instance.event.location,
            "images": self.get_event_images(instance.event),
            "room": self.get_event_room(instance.event),
            "created_at_utc": event_to_utc_timestamp(instance.event.date,instance.event.time)
            
        }
        representation["total"] = instance.total
        return representation
    
    # Create
    def create(self, validated_data):
        order = Order.objects.create(**validated_data)
        # Order Items
        ticket_id = self.context['request'].data.get("ticket_id", None)
        qty = self.context['request'].data.get("qty", 0)
        for i in range(0, int(qty)):
            ticket = Ticket.objects.get(uuid=ticket_id)
            OrderItem.objects.create(order=order,ticket=ticket,price=ticket.price)

        return order
    

# Ticket Serializer
class TicketSerializer(serializers.ModelSerializer):
    event = UUIDRelatedField(queryset=Event.objects.all(), required=True)
    order_items = serializers.SerializerMethodField()
    other_paid_users = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = [
            'uuid',
            "event",
            "status",
            "order_items",
            "other_paid_users",
            "created_at",
            "updated_at",
        ]


class EventLimitedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["uuid", "title"]


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["event"] = {
            "uuid": instance.uuid,
            "title": instance.title, 
            "created_at_utc":event_to_utc_timestamp(instance.date,instance.time)
        }
        return representation

    

# Event User Serializer
class EventUserSerializer(serializers.ModelSerializer):
    event = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    interests = UserInterestSerializer(
        many=True, read_only=True, source="userinterest_set"
    )
    liked = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = [
            "uuid",
            "email",
            "full_name",
            "profile_picture",
            "dob",
            "age",
            "gender",
            "interests",
            "liked",
            "event", 
        ]

    def get_event(self, user):
        request = self.context["request"]
        uuid = request.parser_context['kwargs']['uuid']
        event = Event.objects.get(uuid=uuid)
        event_serializer = EventLimitedSerializer(event, context={'request': request})
        return event_serializer.data

    def get_age(self, obj):
        if obj.dob:
            today = datetime.now().date()
            birthdate = obj.dob.date()
            age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
            return age
        return None
    
    def get_liked(self, obj):
        user = self.context["request"].user        
        if user.is_authenticated:           
            return FavouriteUser.objects.filter(user_liked_by=user, user_liked=obj).exists()
        else:
            return False 


# Order History OrderItem Serializer
class OrderHistoryOrderItemSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()    
    
    # Get User Images
    def get_user_images(self, user):
        images = UserImage.objects.filter(user=user)
        if images.exists():
            return EventImageSerializer(images, many=True).data
        else:
            return None
    class Meta:
        model = OrderItem
        fields = [
            'uuid',
            'price',
            "created_at",
            "updated_at",
            "status",
        ]

    def get_price(self, obj):
        if obj.price:
            return obj.price
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["event"] = {
            "uuid": instance.order.event.uuid,
            "name": instance.order.event.title,
            "club": instance.order.event.club.title,
            "created_at_utc":event_to_utc_timestamp(instance.order.event.date,instance.order.event.time)
        }
        representation["user"] = {
            "uuid": instance.order.user.uuid,
            "name": instance.order.user.full_name,
            "email": instance.order.user.email,
            "profile_picture": instance.order.user.profile_picture.url
            if instance.order.user.profile_picture
            else None,
        }
        return representation
