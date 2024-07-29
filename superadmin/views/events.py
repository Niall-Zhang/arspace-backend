from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from arspace.settings import FCM_SERVER_KEY
from authentication.models import User
from chat.models import Room
from club.models import Event, EventImage
from superadmin.forms.events import EventForm
from superadmin.views.views import superuser_required
from django.contrib import messages
from django_serverside_datatable.views import ServerSideDatatableView
from django.http import JsonResponse
from utils.constants import BODY, CLUB_CREATED_SUCCESS, CLUB_DELETED_SUCCESS, DEVICE_TOKEN, ERROR, EVENT, EVENT_CREATED_SUCCESS, EVENT_DELETED_SUCCESS, EVENT_IMAGE_DELETED_SUCCESS, EVENT_UPDATED_SUCCESS, FALSE,FORM, INVALID_REQUEST_METHOD, MESSAGE,POST,CLUB_UPDATED_SUCCESS,INVALID_FORM_DATA, SUCCESS, TRUE,TITLE,TYPE, UPCOMING_EVENT_NEAR, USER_ID
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.db.models import F
import logging, re

from utils.firebase import send_notifications_using_fcm
from utils.utils import store_notification
logger = logging.getLogger(__name__)

# Show all Events
@login_required(login_url="admin-login")
@superuser_required
def index(request):
    try:
        context = {}
        return render(request, "superadmin/events/index.html", context)
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":"/admin/events"}
        return render(request,"500.html",context)
    

# Get all events using datatables
class EventsListView(ServerSideDatatableView):
    queryset = (
        Event.objects.all().order_by("-id")
    )
    columns = ["uuid", "club__title","title", "date","time" ,"created_at"]

# Create Event
@login_required(login_url="admin-login")
@superuser_required
def create(request):
    try:
        if request.method == 'POST':
            event_form = EventForm(request.POST,request.FILES)
            if event_form.is_valid():
                event = event_form.save()
                # Save Event Images
                images = request.FILES.getlist('images')
                for image in images:
                    image_ins = EventImage(image=image,event=event)
                    image_ins.save()

                # Create Room
                title = re.sub(r'[^A-Za-z0-9 ]+', '', event.title)
                title = title.replace(" ", "-")
                Room.objects.create(name=title,event=event,type="group")
                if event.longitude is not None and event.latitude is not None:
                    # Get event's near by users to send/store notification
                    event_longitude = float(event.longitude)
                    event_latitude = float(event.latitude)
                    radius = 200
                    reference_point = Point(event_longitude, event_latitude)
                    nearby_users = User.objects.filter(point__distance_lte=(reference_point, radius)).exclude(is_superuser=True).values('id', 'device_token')
                    logger.info(f"method: event_create(), nearby_users: {nearby_users}")
                    if len(nearby_users) > 0:
                        for user in nearby_users:
                            logger.info(f"method: event_create(), user: {user}")
                            payload = {USER_ID:user["id"],TITLE:UPCOMING_EVENT_NEAR,TYPE:EVENT,MESSAGE:None,EVENT:event}
                            logger.info(f"method: event_create(), payload: {payload}")
                            # Store Notification
                            store_notification(payload)
                            # Send Firebase Notification
                            if user["device_token"] is not None:
                                device_token = [user["device_token"]]
                                send_notifications_using_fcm({TITLE:UPCOMING_EVENT_NEAR,BODY:UPCOMING_EVENT_NEAR,DEVICE_TOKEN:device_token})
                messages.success(request, EVENT_CREATED_SUCCESS)
                return redirect('admin-events')
            else:   
                context = {'event_form': event_form}
                logger.info(f"event_form: {event_form.errors}")
                messages.error(request, INVALID_FORM_DATA)
                return render(request,'superadmin/events/create.html',context)
        
        form = EventForm()
        context = {FORM: form,"FCM_SERVER_KEY":FCM_SERVER_KEY}
        return render(request, 'superadmin/events/create.html', context)
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":"/admin/events/create"}
        return render(request,"500.html",context)
    

# Event Edit
@login_required(login_url="admin-login")
@superuser_required
def edit(request, uuid):
    try:
        context = {}
        event = get_object_or_404(Event, uuid=uuid)
        if request.method == POST:
            form = EventForm(request.POST,request.FILES, instance=event)
            if form.is_valid():
                form.save()
                # Save Event Images
                images = request.FILES.getlist('images')
                for image in images:
                    image_ins = EventImage(image=image,event=event)
                    image_ins.save()
                messages.success(request, EVENT_UPDATED_SUCCESS)
                return redirect('admin-events')
            else:                
                context = {FORM:form}
                messages.error(request, INVALID_FORM_DATA)
                return render(request,'superadmin/events/edit.html',context)
        
        form = EventForm(instance=event)
        context = {FORM:form,"event":event,"FCM_SERVER_KEY":FCM_SERVER_KEY}
        return render(request, 'superadmin/events/edit.html', context)
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":f"/admin/events/edit/{uuid}"}
        return render(request,"500.html",context)
    
# Delete Event Images
@login_required(login_url="admin-login")
@superuser_required
def images_delete(request,uuid):
    try:
        if request.method == 'POST':            
            event_image = EventImage.objects.get(uuid=uuid)
            event_image.delete()
            return JsonResponse({SUCCESS:TRUE,MESSAGE:EVENT_IMAGE_DELETED_SUCCESS})
        else:
            return JsonResponse({SUCCESS:FALSE,ERROR: INVALID_REQUEST_METHOD})
    except Exception as ex:
        messages.error(request, str(ex))
        return JsonResponse({SUCCESS:FALSE,ERROR: str(ex)})
    

# Delete
def delete(request, uuid):
    try:
        if request.method == 'POST':            
            event = Event.objects.get(uuid=uuid)
            event.delete()
            return JsonResponse({SUCCESS:TRUE,MESSAGE:EVENT_DELETED_SUCCESS})
        else:
            return JsonResponse({SUCCESS:FALSE,ERROR: INVALID_REQUEST_METHOD})
    except Exception as ex:
        messages.error(request, str(ex))
        return JsonResponse({SUCCESS:FALSE,ERROR: str(ex)})