from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from superadmin.views.views import superuser_required
from django.contrib import messages
import uuid
from utils.constants import (
    ERROR,
    FALSE,
    NEW_MESSAGE_RECEIVED,
    NOTIFICATION,
    ROOM,
    TITLE,
    TRUE,
    SUCCESS,
    MESSAGE,
    NOTIFICATION_SENT_SUCCESS,
    TYPE,
)
from chat.models import Room, Message
from utils.utils import store_notification

import logging

# Get a logger instance
logger = logging.getLogger(__name__)

@login_required(login_url="admin-login")
@superuser_required
def send_notification_to_topics(request):
    try:
        if request.method == "POST":
            notification_title = request.POST.get('name')
            notification_message = request.POST.get('message')
        
            chat_room = Room.objects.create(
                uuid=uuid.uuid4(),
                name=notification_title,
                type=NOTIFICATION
            )

            # Create a new Message object associated with the created Room
            chat_message = Message.objects.create(
                message=notification_message,
                room_id=chat_room.id
            )
            payload = {TITLE:NEW_MESSAGE_RECEIVED,TYPE:NOTIFICATION,MESSAGE:notification_message,ROOM:chat_room}
            store_notification(payload)
            return JsonResponse({ SUCCESS: TRUE, MESSAGE:NOTIFICATION_SENT_SUCCESS})
    except Exception as ex:
        return JsonResponse({SUCCESS:FALSE, ERROR: str(ex)})



def send_notification_form(request):
    return render(request, 'superadmin/notification/index.html')