from rest_framework import generics, status
from chat.models import Message, Room
from chat.serializers import MessageSerializer, NotificationSerializer, RoomSerializer
from order.models import Order
from user.models import Notification
from utils.json_encoder import SingleEscapeJSONRenderer
from utils.utils import upload_file_to_gcp_bucket
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from utils.pagination import CustomPagination
from django.db.models import Q, Max
from rest_framework.response import Response
from rest_framework.decorators import api_view
from arspace import settings
from google.cloud import storage
from rest_framework.renderers import JSONRenderer

# Constants
from utils.constants import (
    ATTACHMENT_UPLOAD_FAILED,
    ATTACHMENT_UPLOAD_SUCCESS,
    DATA,
    ERROR,
    FALSE,
    INVALID_ATTACHMENT,
    MESSAGE,
    NOTIFICATION,
    NOTIFICATION_READ_SUCCESS,
    SUCCESS,
    TRUE,
)

# Get all notifications
class NotificationListView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = NotificationSerializer

    def get_queryset(self):
        queryset = Notification.objects.filter(Q(type=NOTIFICATION) | Q(user=self.request.user,status=False)).order_by("-created_at")
        return queryset
    
    def get(self, request):
        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    SUCCESS: TRUE,
                    MESSAGE: None,
                    DATA: serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except (AttributeError, FileNotFoundError, Exception) as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
            )

# Read Notification
class NotificationInfoView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = NotificationSerializer

    def patch(self, request, *args, **kwargs):
        try:
            uuid = self.kwargs.get("uuid")
            notification = Notification.objects.get(uuid=uuid)
            notification.status = TRUE
            notification.save()

            return Response(
                {SUCCESS: TRUE,MESSAGE:NOTIFICATION_READ_SUCCESS},
                status=status.HTTP_200_OK,
            )
        except (AttributeError, FileNotFoundError, Exception) as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
            )


# Rooms
class RoomsListView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = RoomSerializer


    def get_queryset(self):
        paid_events = self.request.user.order_set.values_list('event', flat=True)
        queryset = (
            Room.objects.filter(
                Q(event__in=paid_events) |
                Q(room_sender=self.request.user) |
                Q(room_receiver=self.request.user) |
                Q(type=NOTIFICATION)
            )
            .annotate(latest_message_time=Max("messages__created_at"))
            .order_by("-latest_message_time")  
        )
        return queryset

    def get_serializer(self, *args, **kwargs):
        # Add latest_message field to serializer fields
        serializer_class = self.serializer_class
        serializer_class.Meta.fields += ["latest_message"]
        return serializer_class(*args, **kwargs)

    def to_representation(self, instance):
        # Include the latest message in the serialized representation
        representation = super().to_representation(instance)
        last_message = instance.last_message
        if last_message:
            representation["latest_message"] = {
                "sender": last_message.room_sender.full_name,
                "message": last_message.message,
                "created_at": last_message.created_at,
            }
        else:
            representation["latest_message"] = None
        return representation

    # Get All Rooms
    def get(self, request):
        try:
            queryset = self.get_queryset()
            search = self.request.query_params.get("search", None)
            if search:
                queryset = queryset.filter(Q(name__icontains=search))
                
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    SUCCESS: TRUE,
                    DATA: serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except (AttributeError, FileNotFoundError, Exception) as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
            )


# Get All Room Messages
class MessageListView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    renderer_classes = [SingleEscapeJSONRenderer]
    # Get all room messages
    def get(self, request, uuid):
        try:
            room = Room.objects.filter(uuid=uuid).first()
            # Update messages status as seen or read
            Message.objects.filter(room=room).update(status=True)
            queryset = queryset = Message.objects.filter(room=room).order_by(
                "-created_at"
            )

            serializer = self.get_serializer(queryset, many=True) 

            return Response(
                {
                    SUCCESS: TRUE,
                    MESSAGE: None,
                    DATA: serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        


        except (AttributeError, FileNotFoundError, Exception) as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
            )

# Upload Chat Attachment
@api_view(["POST"])
def upload_attachment(request):
    try:
        attachment = request.FILES.get("attachment")
        if not attachment:
            return Response(
                {SUCCESS: FALSE, ERROR: INVALID_ATTACHMENT},
                status=status.HTTP_404_NOT_FOUND,
            )
        upload = upload_file_to_gcp_bucket(attachment,"attachment")
        if upload[SUCCESS]:
            return Response(
                {
                    SUCCESS: TRUE,
                    MESSAGE: ATTACHMENT_UPLOAD_SUCCESS,
                    DATA: f"{settings.GCP_BUCKET_URL}{upload[DATA]}",
                },
                status=status.HTTP_200_OK,
            )
        return Response(
                {
                    SUCCESS: FALSE,
                    ERROR: ATTACHMENT_UPLOAD_FAILED,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
    except Exception as ex:
        return Response(
            {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
        )
