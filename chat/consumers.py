import json,base64
from urllib.parse import parse_qs
from rest_framework.response import Response
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser
from chat.serializers import GetMessageSerializer
from chat.models import Message, Room
from order.models import Order
from utils.constants import BODY, DEVICE_TOKEN, ERROR, FALSE, NEW_MESSAGE_RECEIVED, ROOM, ROOM_ID, SUCCESS, TITLE, TYPE, UPCOMING_EVENT_NEAR, USER_ID,MESSAGE
from rest_framework import status

from utils.firebase import send_notification_using_fcm
from utils.utils import store_notification

# Connect Web Socket
class ConnectSocket(AsyncWebsocketConsumer):
    # Connect
    async def connect(self):
        query_string = self.scope.get("query_string", b"").decode("utf-8")
        self.query_params = {
            key: value[0] for key, value in parse_qs(query_string).items()
        }
        # Get current logged in user by token
        token = self.query_params["token"]
        if token is not None:
            user = await self.get_user_by_token(token)
            if user is not None:
                await self.accept()

    # Get User By Token
    @database_sync_to_async
    def get_user_by_token(self, token_key):
        try:
            token = Token.objects.get(key=token_key)
            return token.user
        except Token.DoesNotExist:
            return AnonymousUser()

# Connect Private Room
class PrivateRoomChat(AsyncWebsocketConsumer):
    # Connect
    async def connect(self):
        try:
            query_string = self.scope.get("query_string", b"").decode("utf-8")
            self.query_params = {
                key: value[0] for key, value in parse_qs(query_string).items()
            }
            # Get current logged in user by token
            token = self.query_params["token"]
            if token is not None:
                user = await self.get_user_by_token(token)
                self.current_user_id = user.id
                # self.sender_username = await self.get_user(current_user_id)
                self.sender_username = user.full_name
                room_uuid = self.scope["url_route"]["kwargs"]["uuid"]
                get_room = await self.get_room(room_uuid)
                if get_room is not None:
                    self.room = get_room
                    self.room_id = get_room.id
                    self.room_name = get_room.name.replace(" ", "")
                    self.room_group_name = f"chat_{self.room_name}"
                    await self.channel_layer.group_add(
                        self.room_group_name, self.channel_name
                    )

            await self.accept()
        except (Exception,AttributeError) as ex:
            await self.send(
                text_data=json.dumps(
                    {
                       SUCCESS:FALSE,ERROR:str(ex)
                    }
                )
            )
            await self.close()

    # Disconnect
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_layer)
        await self.disconnect(close_code)

    # Receive
    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
            message = data["message"]
            attachment = data["attachment"]
            await self.save_message(
                sender_id=self.current_user_id,
                message=message,
                attachment=attachment,
                room_id=self.room_id,
            )

            messages = await self.get_messages()
            # messages_json = json.dumps(messages)
            # encoded_messages = base64.b64encode(messages_json.encode('utf-8')).decode('utf-8')
            # encoded_messages = messages
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "messages": messages,
                },
            )
        except (Exception,AttributeError) as ex:
            await self.send(
                text_data=json.dumps(
                    {
                       SUCCESS:FALSE,ERROR:str(ex)
                    }
                )
            )
            await self.close()

    async def chat_message(self, event):
        try:
            message = event["message"]
            messages = event["messages"]
            # attachment = event["attachment"]

            await self.send(
                text_data=json.dumps(
                    {
                        "message": message,
                        "sender_username": self.sender_username,
                        "messages": messages,
                    }
                )
            )
        except (Exception,AttributeError) as ex:
            await self.send(
                text_data=json.dumps(
                    {
                       SUCCESS:FALSE,ERROR:str(ex)
                    }
                )
            )
            await self.close()

    # Get User By Token
    @database_sync_to_async
    def get_user_by_token(self, token_key):
        try:
            token = Token.objects.get(key=token_key)
            return token.user
        except Token.DoesNotExist:
            return AnonymousUser()

    # Get User By Id
    @database_sync_to_async
    def get_user(self, id):
        return get_user_model().objects.filter(id=id).first()

    # Get Room
    @database_sync_to_async
    def get_room(self, uuid):
        try:
            room = Room.objects.get(uuid=uuid)
            return room
        except Room.DoesNotExist:
            return None

    # Get Messages
    @database_sync_to_async
    def get_messages(self):
        try:
            messages = Message.objects.filter(room_id=self.room_id).order_by('-created_at')
            serializer = GetMessageSerializer(messages, many=True)
            return serializer.data
        except (Exception,AttributeError) as ex:
            return None

    # Save Messages
    @database_sync_to_async
    def save_message(self, sender_id, message, attachment, room_id):
        try:
            Message.objects.create(
                message_sender_id=sender_id,
                message=message,
                attachment=attachment,
                room_id=room_id,
            )
            room = self.room
            if room.room_sender_id == sender_id:
                user_id = room.room_receiver_id
            elif room.room_receiver_id == sender_id:
                user_id = room.room_sender_id
            payload = {USER_ID:user_id,TITLE:NEW_MESSAGE_RECEIVED,TYPE:ROOM,MESSAGE:message,ROOM:room}
            store_notification(payload)
            # Send Firebase Notification
            user = self.get_user(user_id)
            if user.device_token is not None:
                send_notification_using_fcm({TITLE:NEW_MESSAGE_RECEIVED,BODY:message,DEVICE_TOKEN:user.device_token})
        except (Exception,AttributeError) as ex:
            return None


# Connect Event Group
class EventGroupChat(AsyncWebsocketConsumer):
    # Connect
    async def connect(self):
        try:
            query_string = self.scope.get("query_string", b"").decode("utf-8")
            self.query_params = {
                key: value[0] for key, value in parse_qs(query_string).items()
            }
            # Get current logged in user by token
            token = self.query_params["token"]
            if token is not None:
                user = await self.get_user_by_token(token)
                self.current_user_id = user.id
                # self.sender_username = await self.get_user(current_user_id)
                self.sender_username = user.full_name
                room_uuid = self.scope["url_route"]["kwargs"]["uuid"]
                get_room = await self.get_room(room_uuid)
                if get_room is not None:
                    self.room = get_room
                    self.room_id = get_room.id
                    self.room_name = get_room.name.replace(" ", "")
                    self.room_group_name = f"chat_{self.room_name}"
                    await self.channel_layer.group_add(
                        self.room_group_name, self.channel_name
                    )

            await self.accept()
        except (Exception,AttributeError) as ex:
            await self.send(
                text_data=json.dumps(
                    {
                       SUCCESS:FALSE,ERROR:str(ex)
                    }
                )
            )
            await self.close()

    # Disconnect
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_layer)
        await self.disconnect(close_code)

    # Receive
    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        message = data["message"]
        attachment = data["attachment"]
        await self.save_message(
            sender_id=self.current_user_id,
            message=message,
            attachment=attachment,
            room_id=self.room_id,
        )

        messages = await self.get_messages()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "messages": messages,
            },
        )

    async def chat_message(self, event):
        try:
            message = event["message"]
            messages = event["messages"]
            # attachment = event["attachment"]

            await self.send(
                text_data=json.dumps(
                    {
                        "message": message,
                        "sender_username": self.sender_username,
                        "messages": messages,
                    }
                )
            )
        except (Exception,AttributeError) as ex:
            await self.send(
                text_data=json.dumps(
                    {
                       SUCCESS:FALSE,ERROR:str(ex)
                    }
                )
            )
            await self.close()

    # Get User By Token
    @database_sync_to_async
    def get_user_by_token(self, token_key):
        try:
            token = Token.objects.get(key=token_key)
            return token.user
        except Token.DoesNotExist:
            return AnonymousUser()

    # Get User By Id
    @database_sync_to_async
    def get_user(self, id):
        return get_user_model().objects.filter(id=id).first()

    # Get Room
    @database_sync_to_async
    def get_room(self, uuid):
        try:
            room = Room.objects.get(uuid=uuid)
            return room
        except Room.DoesNotExist:
            return None
        
    # Get Room/Event Users
    def get_room_users(self,event_id):
        try:
            orders = Order.objects.filter(event_id=event_id)
            users = orders.user_set.all()
            return users
        except Room.DoesNotExist:
            return []

    # Get Messages
    @database_sync_to_async
    def get_messages(self):
        try:
            messages = Message.objects.filter(room_id=self.room_id).order_by('-created_at')
            serializer = GetMessageSerializer(messages, many=True)
            return serializer.data
        except (Exception,AttributeError) as ex:
            return None

    # Save Messages
    @database_sync_to_async
    def save_message(self, sender_id, message, attachment, room_id):
        try:
            Message.objects.create(
                message_sender_id=sender_id,
                message=message,
                attachment=attachment,
                room_id=room_id,
            )
            users = self.get_room_users(self.room.event_id)
            if len(users) > 0:
                for user in users:
                    if sender_id != user.id:
                        payload = {USER_ID:user.id,TITLE:NEW_MESSAGE_RECEIVED,TYPE:ROOM,MESSAGE:message,ROOM_ID:room_id}
                        store_notification(payload)
                        # Send Firebase Notification
                        if user.device_token is not None:
                            send_notification_using_fcm({TITLE:NEW_MESSAGE_RECEIVED,BODY:message,DEVICE_TOKEN:user.device_token})
        except (Exception,AttributeError) as ex:
            return None