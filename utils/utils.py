from arspace import settings
from base.models import Settings
from club.models import EventTicket, Ticket
from order.models import OrderItem
from user.models import Notification
from utils.constants import (
    DEDUCTED_EVENT_TICKET_UNITS,
    MESSAGE,
    NO_MORE_SEATS_AVAILABLE,
    NO_ORDER_FOUND,
    NO_ORDER_ITEMS_FOUND,
    OTP_GENERATION_FAILED,
    OTP_SEND_FAILED,
    OTP_SEND_SUCCESS,
    SUCCESS,
    ERROR,
    DATA,
    TRUE,
    FALSE,
    SEND_MESSAGE_TO_TOPIC,
)
from django.utils.dateformat import format
from django.utils import timezone
from datetime import datetime
import pytz

from dotenv import load_dotenv
import random, string, os, uuid

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from utils.email_sender import send_email_using_gmail_smtp

load_dotenv()

import boto3
from storages.backends.s3boto3 import S3Boto3Storage
from google.cloud import storage

# from django.contrib.auth.models import User
from authentication.models import User
import logging

# Get a logger instance
logger = logging.getLogger(__name__)


#firebase import firebase_admin
import firebase_admin
from firebase_admin import messaging
firebase_admin.initialize_app()


# Generate OTP
def generate_otp(length=6):
    try:
        characters = string.digits
        otp = "".join(random.choice(characters) for _ in range(length))
        print(f"otp >>>>>>>> {otp}")
        return otp
    except Exception as ex:
        return None


# Generate Unique Image Name
def generate_unique_filename(file, folder):
    try:
        unique_id = str(uuid.uuid4())
        _, file_extension = os.path.splitext(file)
        new_filename = f"{folder}/{unique_id}{file_extension}"

        return new_filename
    except Exception as ex:
        return FALSE

# Send verification otp on user email
def send_verification_otp(email):
    try:
        otp = generate_otp(6)
        if otp is not None:
            # Update OTP
            user = User.objects.get(email=email)
            user.otp = otp
            user.save()
            # Send Email using Template
            subject = "Email Verification OTP"
            context = {"otp": otp, "email": email}
            html_template = render_to_string("email-verification-otp.html", context)
            plain_text = strip_tags(html_template)
            is_sent = send_email_using_gmail_smtp(
                email, subject, plain_text, html_template
            )
            logger.info(f"method:send_verification_otp, is_sent:{is_sent}")
            return {SUCCESS: TRUE, MESSAGE: OTP_SEND_SUCCESS}
        return {SUCCESS: FALSE, ERROR: OTP_GENERATION_FAILED}
    except Exception as ex:
        return {SUCCESS: FALSE, ERROR: OTP_SEND_FAILED}


# Send password reset token on user email
def send_password_reset_token(token, email):
    try:
        subject = "Password Reset Token"
        app_url = settings.APP_URL
        reset_password_link = f"{settings.APP_URL}password-reset/{token}"
        context = {
            "reset_password_link": reset_password_link,
            "email": email,
            "app_url": app_url,
        }
        html_template = render_to_string("password-reset-email.html", context)
        plain_text = strip_tags(html_template)

        is_sent = send_email_using_gmail_smtp(email, subject, plain_text, html_template)
        logger.info(f"method:send_password_reset_token, is_sent:{is_sent}")
        return TRUE
    except Exception as ex:
        return FALSE


# Rename files 
def rename_file(file):
    try:        
        unique_filename = str(uuid.uuid4())
        file_extension = os.path.splitext(file.name)[-1]        
        new_file_name = f"{unique_filename[:8]}{file_extension}"
        return {SUCCESS: TRUE, DATA: new_file_name}
    except Exception as ex:
        return {SUCCESS: FALSE, ERROR: str(ex)}
    

# Deduct units from event tickets
def deduct_events_seats(payload):
    try:
        logger.info(f"method:deduct_events_seats, payload:{payload}")
        order = payload['order']
        if order:
            # Prefetch related order items for the created order instance            
            order_items = OrderItem.objects.filter(order=order)
            if order_items:
                for order_item in order_items:
                    event_ticket = Ticket.objects.get(id=order_item.ticket.id)
                    left_ticket = int(event_ticket.left)
                    order_qty = int(order.qty)
                    # if left_ticket >= order_qty:
                    if left_ticket > 0:
                        left = left_ticket - 1
                        event_ticket.left = left
                        event_ticket.save()
                    else:
                        return {SUCCESS: FALSE,ERROR:NO_MORE_SEATS_AVAILABLE}
                return {SUCCESS: TRUE,MESSAGE:DEDUCTED_EVENT_TICKET_UNITS}
            return {SUCCESS: FALSE,ERROR:NO_ORDER_ITEMS_FOUND}
        return {SUCCESS: FALSE, ERROR: NO_ORDER_FOUND}
    except (AttributeError, FileNotFoundError, Exception) as ex:
        return {SUCCESS: FALSE, ERROR: str(ex)}

# Upload file to GCP bucket
def upload_file_to_gcp_bucket(file, path):
    try:
        GS_BUCKET_NAME = settings.GS_BUCKET_NAME
        storage_client = storage.Client()
        bucket = storage_client.bucket(GS_BUCKET_NAME)
        rename_file_res = rename_file(file)
        if rename_file_res[SUCCESS]:

            file_name = f"{path}/{rename_file_res[DATA]}"
            logger.info(f"method:upload_file_to_gcp_bucket, key:{file_name}")
            blob = bucket.blob(file_name)
            logger.info(f"method:upload_file_to_gcp_bucket, blob:{blob}")
            blob.upload_from_file(file)
            return {SUCCESS: TRUE,DATA:file_name}
        return rename_file_res
    except Exception as ex:
        logger.error(f"method:upload_file_to_gcp_bucket, error:{str(ex)}")
        return {SUCCESS: FALSE, ERROR: str(ex)}


# Delete file from GCP bucket
def delete_file_from_gcp_bucket(file):
    try:
        file = str(file)
        logger.info(f"method:delete_file_from_gcp_bucket, file:{file}")
        GS_BUCKET_NAME = settings.GS_BUCKET_NAME
        storage_client = storage.Client()
        bucket = storage_client.bucket(GS_BUCKET_NAME)
        blob = bucket.blob(file)
        blob.delete()
    except Exception as ex:
        logger.error(f"method:delete_file_from_gcp_bucket, error:{str(ex)}")
        return {SUCCESS: FALSE, ERROR: str(ex)}
    
# Get Settings
def get_settings(key):
    try:
        setting = Settings.objects.get(meta_key=key)
        return setting.meta_value
    except Exception as ex:
        return None
    

# Store Notification
def store_notification(payload):
    try:
        logger.info(f"method:store_notification, payload:{payload}")
        room = payload["room"] if "room" in payload else None
        event = payload["event"] if "event" in payload else None
        liked_by = payload["liked_by"] if "liked_by" in payload else None
        user_id = payload["user_id"] if "user_id" in payload else None
        
        Notification.objects.create(
            user_id=user_id,
            title=payload["title"],
            message=payload["message"],
            type=payload["type"],
            room=room,
            event=event,
            liked_by=liked_by,
        )
        return {SUCCESS: TRUE}
    except Exception as ex:
        logger.error(f"method:store_notification, error:{str(ex)}")
        return {SUCCESS: FALSE, ERROR: str(ex)}
    
#user subscribe to topic
def subscribe_user_to_topic(device_token):
    try:
        registration_token = device_token
        topic = SEND_MESSAGE_TO_TOPIC
        response = messaging.subscribe_to_topic(registration_token, topic)
        logger.info(f"{response.success_count} token was subscribed successfully")
        return {SUCCESS: TRUE}
    except Exception as ex:
        logger.error(f"device token not found--- error : {str(ex)}")
        return {SUCCESS: FALSE, ERROR: str(ex)}
    


# Message sent to topic
def send_messages_to_topics(request):
    try:
        topic = SEND_MESSAGE_TO_TOPIC
        message = messaging.Message(
            data={
                'title': 'sasasasa',
                'body': 'this is body rest',
            },
            topic=topic,
        )
        logger.info(f"{response} message to topic sent successfully")
        response = messaging.send(message)
        return {SUCCESS: TRUE}
        
    except Exception as ex:
        logger.error(f"message to topic not sent-- error : {str(ex)}")
        return {SUCCESS: FALSE, ERROR: str(ex)}

# Convert UTC 
def to_utc_timestamp(type,date):
    try:
        if type is "date" and date is not None:
            date_time = datetime.strptime(str(date), "%Y-%m-%d")
            date_time = int(date_time.timestamp())     
            return str(date_time)

        elif date is not None:
            date = timezone.make_aware(date, timezone=timezone.utc) if timezone.is_naive(date) else date
            return format(date, 'U')
        return None
    except Exception as ex:
        return str(ex)
    

# Convert event's date & time into unix timestamps
def event_to_utc_timestamp(date, time):
    try:
        if date is not None:
            date_time_str = f"{date} {time}" if time else str(date)
            date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S" if time else "%Y-%m-%d")
            date_time = timezone.make_aware(date_time, timezone=pytz.utc) if timezone.is_naive(date_time) else date_time
            return format(date_time, 'U')
        return None
    except Exception as ex:
        return None
