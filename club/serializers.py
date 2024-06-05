from rest_framework import serializers
from authentication.models import User

# Models
from club.models import Cast, Club,Event, EventCast, EventImage, EventLike, EventTicket, Ticket
from utils.utils import get_settings, to_utc_timestamp
from django.utils.dateformat import format
from django.utils import timezone

class UUIDRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return str(value.uuid)

    def to_internal_value(self, data):
        return self.queryset.get(uuid=data)

# Cast Serializer
class CastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cast
        fields = [
            'uuid',
            'name',
            "description",
            "image",
        ]

# Club Serializer
class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = [
            'uuid',
            'title',
        ]

# Event Image Serializer
class EventImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventImage
        fields = ("uuid", "image")


# Ticket Serializer
class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("uuid","name","price","currency","units","left")
    
# Event Ticket Serializer
class EventTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTicket
        fields = ["ticket"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation = {
            "uuid": instance.ticket.uuid,
            "name": instance.ticket.name,
            "price": instance.ticket.price,
            "currency": instance.ticket.currency,
            "units": instance.ticket.units,
            "left": instance.ticket.left,
        }
        return representation

# Event Cast Serializer
class EventCastSerializer(serializers.ModelSerializer):    
    cast = serializers.CharField(source="cast.name")
    image = serializers.ImageField(source="cast.image")
    class Meta:
        model = EventCast
        fields = ("uuid","cast","image")

# Event Serializer
class EventSerializer(serializers.ModelSerializer):
    club = UUIDRelatedField(queryset=Club.objects.all(), required=True)
    images = EventImageSerializer(
        many=True, read_only=True, source="eventimage_set"
    )
    casts = EventCastSerializer(
        many=True, read_only=True, source="eventcast_set"
    )
    tickets = EventTicketSerializer(many=True, read_only=True, source="eventticket_set")
    interested_users = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    class Meta:
        model = Event
        fields = [
            'uuid',
            "club",
            "title",
            "description",
            "date",
            "time",
            "latitude",
            "longitude",            
            "location",
            "created_at",
            "images",
            "casts",
            "liked",
            "tickets",
            "interested_users"
        ]

    def get_interested_users(self, obj):
        paid_orders = obj.order_set.all()
        interested_users = User.objects.filter(order__in=paid_orders)
        serialized_users = []
        if len(interested_users) > 0:
            for user in interested_users:
                serialized_user = {
                    'profile_picture': user.profile_picture.url if user.profile_picture else None
                }
                serialized_users.append(serialized_user)
        return serialized_users
    
    def get_liked(self, obj):
        user = self.context["request"].user        
        if user.is_authenticated:           
            return EventLike.objects.filter(user=user, event=obj).exists()
        else:
            return False

    # Create
    def create(self, validated_data):
        event = Event.objects.create(**validated_data)
        # Image
        images = self.context.get("request").FILES.getlist("images")        
        for image in images:
            EventImage.objects.create(event=event, image=image)

        # Cast
        casts = self.context.get("request").POST.getlist("casts")        
        for cast_uuid in casts:
            cast = Cast.objects.get(uuid=cast_uuid)
            EventCast.objects.create(event=event, cast=cast)

        return event
    
    # Update
    def update(self, instance, validated_data):
        if self.context.get("request"):
            # Images
            images = self.context.get("request").FILES.getlist("images")
            if images and len(images) > 0:
                # Clear existing images for the event
                instance.eventimage_set.all().delete()
                for image in images:
                    EventImage.objects.create(event=instance, image=image)
            # Casts
            casts = self.context.get("request").POST.getlist("casts")
            if casts and len(casts) > 0:
                # Clear existing casts for the event
                instance.eventcast_set.all().delete()
                for cast_uuid in casts:
                    cast = Cast.objects.get(uuid=cast_uuid)
                    EventCast.objects.create(event=instance, cast=cast)
        # Update the event model instance
        instance = super().update(instance, validated_data)
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["club"] = {
            "uuid": instance.club.uuid,
            "title": instance.club.title,
            "contact_no": instance.club.contact_no,
        }
        representation['fees'] = int(get_settings('fees')) if get_settings('fees') else 0
        representation['created_at_utc'] = to_utc_timestamp("date",instance.date)
        return representation
    


# Event Like Serializer
class EventLikeSerializer(serializers.ModelSerializer):
    event = UUIDRelatedField(queryset=Event.objects.all(), required=True)

    class Meta:
        model = EventLike
        fields = ("uuid", "event", "user")


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["event"] = {
            "uuid": instance.event.uuid,
            "title": instance.event.title,
        }
        representation["user"] = {
            "uuid": instance.user.uuid,
            "email": instance.user.email,
        }
        return representation