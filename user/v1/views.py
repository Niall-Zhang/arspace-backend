from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from authentication.models import User
from chat.models import Room
from chat.serializers import RoomSerializer
from club.models import Event, EventLike
from club.serializers import EventLikeSerializer, EventSerializer
from user.models import FavouriteUser, UserBlock, UserCard, ChatRequest
from user.serializers import (
    FavouriteUserSerializer,
    UpdateUserProfileSerializer,
    UserBlockSerializer,
    UserCardSerializer,
    UserProfileSerializer,
    ChatRequestSerializer,
)
from utils.firebase import send_notification_using_fcm
from utils.validators import format_validation_errors
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes
from utils.constants import (
    ACCEPTED,
    BODY,
    CARD_CREATED_SUCCESS,
    CARD_DELETED_SUCCESS,
    CARD_INFO_SUCCESS,
    CARD_NOT_FOUND,
    CHAT_MESSAGE_RECEIVED,    
    CHAT_REQUEST_BODY,
    CHAT_REQUEST_TITLE,
    DEVICE_TOKEN,
    EVENT_LIKED_SUCCESS,
    EVENT_UNLIKED_SUCCESS,
    IS_DEVICE_TOKEN,
    IS_LIKED,
    IS_REQUEST_SENT,
    LIKE,
    LIKED_BY,
    LIKED_YOUR_PROFILE,
    LIST_FETCHED_SUCCESS,
    NEW_MESSAGE_RECEIVED,
    PENDING,
    PRIVATE,
    PROFILE_CHANGED_SUCCESS,
    PROFILE_DATA_SUCCESS,
    REJECTED,
    REQUEST_ACCEPTED_SUCCESS,
    REQUEST_REJECTED_SUCCESS,
    REQUEST_REVERT_SUCCESS,
    REQUEST_SENT_SUCCESS,
    ROOM,
    SUCCESS,
    ERROR,
    DATA,
    MESSAGE,
    TITLE,
    TRUE,
    FALSE,
    TYPE,
    USER_BLOCKED_SUCCESS,
    USER_DELETE_SUCCESS,
    USER_FAVOURITE_SUCCESS,
    USER_ID,
    USER_NOT_FOUND,
    USER_UNBLOCKED_SUCCESS,
    USER_UNFAVOURITE_SUCCESS,
    USER_IMAGE_NOT_FOUND,
    USER_IMAGE_DELETE_SUCCESS,
    EVENT_ID_REQUIRED,
    STATUS_REQIURED
)
from rest_framework.decorators import api_view
from django.http import JsonResponse
from utils.pagination import CustomPagination
from django.db.models import Q
from user.models import UserImage
import logging
logger = logging.getLogger(__name__)

from utils.utils import delete_file_from_gcp_bucket, store_notification
# User Profile View
class UserProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Get Profile Info
    def get(self, request):
        try:
            user = UserProfileSerializer(request.user, context={"request": request})
            return Response(
                {
                    SUCCESS: TRUE,
                    MESSAGE: PROFILE_DATA_SUCCESS,
                    DATA: user.data,
                },
                status=status.HTTP_200_OK,
            )
        except (AttributeError, FileNotFoundError, Exception) as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
            )

    # Update Profile
    def put(self, request):
        try:
            user_profile = request.user
            serializer = UpdateUserProfileSerializer(
                user_profile,
                data=request.data,
                partial=TRUE,
                context={"request": self.request},
            )
            response = {}
            if serializer.is_valid():
                serializer.save()
                serializer = UserProfileSerializer(
                    user_profile, context={"request": request}
                )
                return Response(
                    {
                        SUCCESS: TRUE,
                        MESSAGE: PROFILE_CHANGED_SUCCESS,
                        DATA: serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                error = format_validation_errors(serializer)
                response[SUCCESS] = FALSE
                response[ERROR] = error
                return Response(response, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
            )

    # Delete User Profile

    def delete(self, request, *args, **kwargs):
        try:
            user = get_object_or_404(User, pk=request.user.pk)
            user.delete()

            return Response(
                {SUCCESS: TRUE, MESSAGE: USER_DELETE_SUCCESS},
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            return Response(
                {SUCCESS: FALSE, ERROR: USER_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)},
                status=status.HTTP_404_NOT_FOUND,
            )


# Get User By Id
@api_view(["GET"])
def get_user_by_id(request, uuid):
    try:
        user = User.objects.get(uuid=uuid)
        serializer = UserProfileSerializer(user, context={"request": request})
        return Response(
            {
                SUCCESS: TRUE,
                MESSAGE: PROFILE_DATA_SUCCESS,
                DATA: serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    except (AttributeError, FileNotFoundError, Exception) as ex:
        return Response(
            {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
        )


# Make User Blocked
@api_view(["POST"])
def block_user(request, uuid):
    try:
        is_user_valid = User.objects.filter(uuid=uuid).exists()
        if is_user_valid:
            try:
                get_user_blocked_id = User.objects.get(uuid=uuid)
                UserBlock.objects.get(
                    blocked_user=get_user_blocked_id, blocked_by=request.user
                ).delete()
                return Response(
                    {SUCCESS: TRUE, MESSAGE: USER_UNBLOCKED_SUCCESS},
                    status=status.HTTP_200_OK,
                )
            except UserBlock.DoesNotExist as ex:
                UserBlock.objects.create(
                    blocked_user=get_user_blocked_id, blocked_by=request.user
                )
                return Response(
                    {SUCCESS: TRUE, MESSAGE: USER_BLOCKED_SUCCESS},
                    status=status.HTTP_200_OK,
                )
        return Response(
            {SUCCESS: FALSE, ERROR: USER_NOT_FOUND},
            status=status.HTTP_404_NOT_FOUND,
        )
    except (AttributeError, FileNotFoundError, Exception) as ex:
        return Response(
            {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
        )


# Get blocked users list
@api_view(["GET"])
def block_list(request):
    try:
        blocked_users = UserBlock.objects.filter(blocked_by=request.user)
        serializer = UserBlockSerializer(blocked_users, many=True)
        return Response(
            {SUCCESS: TRUE, MESSAGE: LIST_FETCHED_SUCCESS, DATA: serializer.data},
            status=status.HTTP_404_NOT_FOUND,
        )
    except (AttributeError, FileNotFoundError, Exception) as ex:
        return Response(
            {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
        )


# Favourite Events
class FavouriteEventsAPI(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = EventLikeSerializer
    pagination_class = CustomPagination

    def get(self, request):
        try:
            queryset = EventLike.objects.filter(user=self.request.user).order_by(
                "-created_at"
            )
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    SUCCESS: TRUE,
                    MESSAGE: LIST_FETCHED_SUCCESS,
                    DATA: serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except (AttributeError, FileNotFoundError, Exception) as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
            )


# Like Event
class FavouriteEventAPI(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = EventLikeSerializer

    def patch(self, request, *args, **kwargs):
        try:
            event_uuid = self.kwargs.get("uuid")
            event = generics.get_object_or_404(Event, uuid=event_uuid)
            user = request.user

            # Check if the user has already liked the event
            existing_like = EventLike.objects.filter(user=user, event=event).first()
            is_liked = request.data.get("is_liked")
            if existing_like:
                # Unlike the event
                existing_like.delete()
                return Response(
                    {
                        SUCCESS: TRUE,
                        MESSAGE: EVENT_UNLIKED_SUCCESS,
                        IS_LIKED: FALSE,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                # Like the event
                like = EventLike.objects.create(user=user, event=event)
                serializer = self.get_serializer(like)
                return Response(
                    {SUCCESS: TRUE, MESSAGE: EVENT_LIKED_SUCCESS, IS_LIKED: TRUE},
                    status=status.HTTP_200_OK,
                )

        except Exception as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
            )


# Favourite Users
class FavouriteUsersAPI(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = FavouriteUserSerializer

    def get(self, request):
        try:
            queryset = FavouriteUser.objects.filter(
                user_liked_by=self.request.user
            ).order_by("-created_at")
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    SUCCESS: TRUE,
                    MESSAGE: LIST_FETCHED_SUCCESS,
                    DATA: serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except (AttributeError, FileNotFoundError, Exception) as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
            )


# Favourite User
class FavouriteUserAPI(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FavouriteUserSerializer

    def patch(self, request, *args, **kwargs):
        try:
            
            event_id = request.data.get('event_id')
            user_status = request.data.get('status')

            if event_id is None:
                 return Response(
                        {
                            SUCCESS: FALSE,
                            ERROR: EVENT_ID_REQUIRED,
                        },
                        status=status.HTTP_404_NOT_FOUND
                    ) 
            elif user_status is None:
                return Response(
                    {
                        SUCCESS: FALSE,
                        ERROR: STATUS_REQIURED,
                    },
                   status=status.HTTP_404_NOT_FOUND
                )
            event = get_object_or_404(Event, uuid=event_id)
            user_uuid = self.kwargs.get("uuid")
            user = generics.get_object_or_404(User, uuid=user_uuid)
            # Check if the user has already liked the user
            already_favourite = FavouriteUser.objects.filter(
                user_liked_by=request.user,
                user_liked=user,
                event_id=event
            )

            if already_favourite.exists():
                if user_status == FALSE:
                    logger.info(f"method:already_favourite, deleting rooms")
                    # Delete room & chat if room also created
                    try:
                        Room.objects.filter(
                            Q(room_sender_id=request.user.id, room_receiver_id=user.id, type=PRIVATE)
                        ).delete()
                        logger.info(f"method:already_favourite, room1 deleted")
                    except (AttributeError, FileNotFoundError, Exception) as ex:
                        logger.error(f"room deleted, room_sender_id: {request.user.id}, ex: {str(ex)}")
                    
                    # Delete room & chat if room also created
                    try:
                        Room.objects.filter(
                            Q(room_sender_id=user.id, room_receiver_id=request.user.id, type=PRIVATE)
                        ).delete()
                        logger.info(f"method:already_favourite, room2 deleted")
                    except (AttributeError, FileNotFoundError, Exception) as ex:
                        logger.error(f"room deleted, room_receiver_id: {request.user.id} , ex: {str(ex)} ")

                    # Unfavourite the user
                    already_favourite.update(status=user_status)
                    return Response(
                        {
                            SUCCESS: TRUE,
                            MESSAGE: USER_UNFAVOURITE_SUCCESS,
                            IS_LIKED: FALSE,
                        },
                        status=status.HTTP_200_OK,
                    ) 
                elif user_status == TRUE:
                    FavouriteUser.objects.filter(
                        user_liked_by=request.user,
                        user_liked=user,
                        event_id=event
                    ).update(status=user_status)

                    payload = {USER_ID:user.id,TITLE:f"{request.user.email} {LIKED_YOUR_PROFILE}",TYPE:LIKE,MESSAGE:f"{request.user.email} {LIKED_YOUR_PROFILE}",LIKED_BY:request.user}
                    res = store_notification(payload)
                    logger.info(f"method:patch, store_notification: {res}")
                    is_device_token = FALSE
                    if user.device_token:
                        is_device_token = TRUE                    
                        payload = {TITLE:f"{request.user.email} {LIKED_YOUR_PROFILE}",BODY:f"{request.user.email} {LIKED_YOUR_PROFILE}",DEVICE_TOKEN:user.device_token}
                        res = send_notification_using_fcm(payload)
                        logger.info(f"method:patch, send_notification_using_fcm: {res}")
                        is_other_person_liked = FavouriteUser.objects.filter(
                        user_liked_by=user, user_liked=request.user
                        ).exists()
                        if is_other_person_liked:
                            logger.info(f"method:patch, is_other_person_liked: {is_other_person_liked}")
                            # Check if room is already created
                            case1 = Room.objects.filter(
                                Q(room_sender_id=user.id, room_receiver_id=request.user.id,type=PRIVATE)
                            )

                            # Check if room is already created
                            case2 = Room.objects.filter(
                                Q(room_sender_id=request.user.id, room_receiver_id=user.id,type=PRIVATE)
                            )
                            
                            if case1.exists():
                                serializer = RoomSerializer(case1.first())
                                logger.info(f"case1: {case1}")
                                return Response(
                                    {SUCCESS: TRUE, MESSAGE: USER_FAVOURITE_SUCCESS, IS_LIKED: TRUE,IS_DEVICE_TOKEN:is_device_token,DATA:serializer.data},
                                    status=status.HTTP_200_OK,
                                )
                            elif case2.exists():
                                serializer = RoomSerializer(case2.first())
                                logger.info(f"case2: {case2}")
                                return Response(
                                    {SUCCESS: TRUE, MESSAGE: USER_FAVOURITE_SUCCESS, IS_LIKED: TRUE,IS_DEVICE_TOKEN:is_device_token,DATA:serializer.data},
                                    status=status.HTTP_200_OK,
                                )
                            else:
                                logger.info(f"method:patch, creating room")
                                get_sender = user.full_name
                                get_receiver = request.user.full_name
                                name = f"{get_sender}-{get_receiver}"
                                try:
                                    room = Room.objects.create(
                                        name=name,
                                        room_sender_id=user.id,
                                        room_receiver_id=request.user.id,
                                        type=PRIVATE
                                    )
                                    serializer = RoomSerializer(room)
                                    return Response(
                                        {SUCCESS: TRUE, MESSAGE: USER_FAVOURITE_SUCCESS, IS_LIKED: TRUE,IS_DEVICE_TOKEN:is_device_token,DATA:serializer.data},
                                        status=status.HTTP_200_OK,
                                    )
                                except Exception as ex:
                                    logger.error(f"method:patch, error: {str(ex)}")
                                    return Response(
                                        {SUCCESS: FALSE, ERROR: str(ex)},
                                        status=status.HTTP_404_NOT_FOUND,
                                    )
                    return Response(
                    {SUCCESS: TRUE, MESSAGE: USER_FAVOURITE_SUCCESS, IS_LIKED: TRUE,IS_DEVICE_TOKEN:is_device_token},
                    status=status.HTTP_200_OK,
                )
        
            else:
                # Like the user
                FavouriteUser.objects.create(
                    user_liked_by=request.user, user_liked=user, event_id=event, status=user_status
                )
                payload = {USER_ID:user.id,TITLE:f"{request.user.email} {LIKED_YOUR_PROFILE}",TYPE:LIKE,MESSAGE:f"{request.user.email} {LIKED_YOUR_PROFILE}",LIKED_BY:request.user}
                res = store_notification(payload)
                logger.info(f"method:patch, store_notification: {res}")
                is_device_token = FALSE
                if user.device_token:
                    is_device_token = TRUE                    
                    payload = {TITLE:f"{request.user.email} {LIKED_YOUR_PROFILE}",BODY:f"{request.user.email} {LIKED_YOUR_PROFILE}",DEVICE_TOKEN:user.device_token}
                    res = send_notification_using_fcm(payload)
                    logger.info(f"method:patch, send_notification_using_fcm: {res}")

                # Create Room if other person also liked current user
                is_other_person_liked = FavouriteUser.objects.filter(
                    user_liked_by=user, user_liked=request.user
                ).exists()
                if is_other_person_liked:
                    logger.info(f"method:patch, is_other_person_liked: {is_other_person_liked}")
                    # Check if room is already created
                    case1 = Room.objects.filter(
                        Q(room_sender_id=user.id, room_receiver_id=request.user.id,type=PRIVATE)
                    )

                    # Check if room is already created
                    case2 = Room.objects.filter(
                        Q(room_sender_id=request.user.id, room_receiver_id=user.id,type=PRIVATE)
                    )
                    
                    if case1.exists():
                        serializer = RoomSerializer(case1.first())
                        logger.info(f"case1: {case1}")
                        return Response(
                            {SUCCESS: TRUE, MESSAGE: USER_FAVOURITE_SUCCESS, IS_LIKED: TRUE,IS_DEVICE_TOKEN:is_device_token,DATA:serializer.data},
                            status=status.HTTP_200_OK,
                        )
                    elif case2.exists():
                        serializer = RoomSerializer(case2.first())
                        logger.info(f"case2: {case2}")
                        return Response(
                            {SUCCESS: TRUE, MESSAGE: USER_FAVOURITE_SUCCESS, IS_LIKED: TRUE,IS_DEVICE_TOKEN:is_device_token,DATA:serializer.data},
                            status=status.HTTP_200_OK,
                        )
                    else:
                        logger.info(f"method:patch, creating room")
                        get_sender = user.full_name
                        get_receiver = request.user.full_name
                        name = f"{get_sender}-{get_receiver}"
                        try:
                            room = Room.objects.create(
                                name=name,
                                room_sender_id=user.id,
                                room_receiver_id=request.user.id,
                                type=PRIVATE
                            )
                            serializer = RoomSerializer(room)
                            return Response(
                                {SUCCESS: TRUE, MESSAGE: USER_FAVOURITE_SUCCESS, IS_LIKED: TRUE,IS_DEVICE_TOKEN:is_device_token,DATA:serializer.data},
                                status=status.HTTP_200_OK,
                            )
                        except Exception as ex:
                            logger.error(f"method:patch, error: {str(ex)}")
                            return Response(
                                {SUCCESS: FALSE, ERROR: str(ex)},
                                status=status.HTTP_404_NOT_FOUND,
                            )
                        
                return Response(
                    {SUCCESS: TRUE, MESSAGE: USER_FAVOURITE_SUCCESS, IS_LIKED: TRUE,IS_DEVICE_TOKEN:is_device_token},
                    status=status.HTTP_200_OK,
                )
        except (AttributeError, FileNotFoundError, Exception) as ex:
            logger.error(f"method:patch, error1: {str(ex)}")
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
            )


# Cards
class CardAPIView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = UserCardSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get(self, request):
        try:
            queryset = UserCard.objects.filter(user=self.request.user).order_by(
                "-created_at"
            )
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    SUCCESS: TRUE,
                    MESSAGE: LIST_FETCHED_SUCCESS,
                    DATA: serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except (AttributeError, FileNotFoundError, Exception) as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
            )

    # Create
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data,context={"request": request})
            response = {}
            if serializer.is_valid():
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                return Response(
                    {
                        SUCCESS: TRUE,
                        MESSAGE: CARD_CREATED_SUCCESS,
                        DATA: serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                error = format_validation_errors(serializer)
                response[SUCCESS] = FALSE
                response[ERROR] = error
                return Response(response, status=status.HTTP_404_NOT_FOUND)

        except (AttributeError, FileNotFoundError, Exception) as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
            )

# Card Info 
class CardInfoView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    serializer_class = UserCardSerializer

    def get_card(self, uuid):
        try:
            return UserCard.objects.filter(uuid=uuid).first()
        except:
            return None
        
    # Info
    def get(self, request, uuid):
        try:
            card = self.get_card(uuid=uuid)
            if card == None:
                return Response(
                    {SUCCESS: FALSE, ERROR: CARD_NOT_FOUND},
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = self.serializer_class(card, context={"request": request})

            return Response(
                {SUCCESS: TRUE, MESSAGE: CARD_INFO_SUCCESS, DATA: serializer.data},
                status=status.HTTP_200_OK,
            )

        except (AttributeError, Exception) as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
            )
        
    def delete(self, request, uuid):
        try:
            card = self.get_card(uuid)
            if card == None:
                return Response(
                    {SUCCESS: FALSE, ERROR: CARD_NOT_FOUND},
                    status=status.HTTP_404_NOT_FOUND,
                )

            card.delete()
            return Response(
                {SUCCESS: TRUE, MESSAGE: CARD_DELETED_SUCCESS},
                status=status.HTTP_200_OK,
            )
        except (AttributeError, FileNotFoundError, Exception) as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
            )

# Chat Requests
class ChatRequestsAPIView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = ChatRequestSerializer

    # Perform Create
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    # Search Filter
    def get_queryset(self):
        # Sent Requests
        queryset = ChatRequest.objects.filter(
            sender=self.request.user, status=PENDING
        ).order_by("-created_at")
        # Recevied Requests
        type = self.request.query_params.get("type", None)
        if type and type == "received":
            queryset = ChatRequest.objects.filter(
                receiver=self.request.user, status=PENDING
            ).order_by("-created_at")
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
                    MESSAGE: LIST_FETCHED_SUCCESS,
                    DATA: serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except (AttributeError, FileNotFoundError, Exception) as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
            )

    # Create
    def post(self, request, *args, **kwargs):
        try:
            receiver = request.data.get("receiver")
            get_receiver = User.objects.get(uuid=receiver)
            # Check if the sender has already sent the request to receiver
            existing_sent_request = ChatRequest.objects.filter(
                sender=request.user, receiver=get_receiver
            ).first()
            if existing_sent_request:
                # Unlike the event
                existing_sent_request.delete()
                return Response(
                    {
                        SUCCESS: TRUE,
                        MESSAGE: REQUEST_REVERT_SUCCESS,
                        IS_REQUEST_SENT: FALSE,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                # Send the request
                send_request = ChatRequest.objects.create(
                    sender=request.user, receiver=get_receiver
                )
                serializer = self.get_serializer(send_request)
                return Response(
                    {
                        SUCCESS: TRUE,
                        MESSAGE: REQUEST_SENT_SUCCESS,
                        IS_REQUEST_SENT: TRUE,
                    },
                    status=status.HTTP_200_OK,
                )

        except (AttributeError, FileNotFoundError, Exception) as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
            )


class ChatRequestAPIView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FavouriteUserSerializer

    def patch(self, request, *args, **kwargs):
        try:
            uuid = self.kwargs.get("uuid")
            update_status = request.data.get("status")
            # payload = {TITLE:CHAT_REQUEST_TITLE,BODY:CHAT_REQUEST_BODY,DEVICE_TOKEN:"eZTWiEuqTeuoLZ3xstWNrY:APA91bEslImzSN4fQeJN5UtLYNVnj6W-dl5WKATGjBs1x5lbKxuFr_uZlaAfoUYQGx397Yh-G7RFK9OiFfXedimE6gv-zDtY_t43kTI6Vpc1d5oGMhFGeeuCH39wja7voCqpZzNAtqVB"}
            # response = send_notification_using_fcm(payload)
            if update_status == ACCEPTED:
                STATUS = REQUEST_ACCEPTED_SUCCESS

            elif update_status == REJECTED:
                STATUS = REQUEST_REJECTED_SUCCESS

            chat_request = ChatRequest.objects.filter(
                receiver=request.user, uuid=uuid
            ).first()
            chat_request.status = update_status
            chat_request.save()

            # Create chat room
            if update_status == ACCEPTED:
                get_sender = chat_request.sender.full_name
                get_receiver = chat_request.receiver.full_name
                name = f"{get_sender}-{get_receiver}"
                Room.objects.create(
                    name=name,
                    room_sender_id=chat_request.sender.id,
                    room_receiver_id=chat_request.receiver.id,
                    type="private"
                )

            return Response(
                {SUCCESS: TRUE, MESSAGE: STATUS},
                status=status.HTTP_200_OK,
            )

        except (AttributeError, FileNotFoundError, Exception) as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
            )

# Delete user Image from GCP
class DeleteUserImageAPIView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_image(self, uuid):
        try:
            return UserImage.objects.filter(uuid=uuid).first()
        except:
            return None

    def delete(self, request, uuid):
        try:
            user_image = self.get_image(uuid=uuid)
            if user_image is None:
                return Response(
                    {SUCCESS: False, ERROR: USER_IMAGE_NOT_FOUND},
                    status=status.HTTP_404_NOT_FOUND,
                )
            
            # Delete file from GCP bucket
            delete_file_from_gcp_bucket(user_image.image)

            # Delete record from the database
            user_image.delete()

            return Response(
                {SUCCESS: True, MESSAGE: USER_IMAGE_DELETE_SUCCESS},
                status=status.HTTP_200_OK,
            )

        except Exception as ex:
            return Response(
                {SUCCESS: False, ERROR: str(ex)},
                status=status.HTTP_404_NOT_FOUND
            )
        
