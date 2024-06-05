import uuid
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from superadmin.forms.users import UserForm
from superadmin.views.views import superuser_required
from django.contrib import messages
from django_serverside_datatable.views import ServerSideDatatableView
from authentication.models import User
from order.models import Order, OrderItem
from arspace.settings import GCP_BUCKET_URL
from django.http import JsonResponse
from django.db.models import Sum
from user.models import UserImage
from club.models import Event, Ticket
from datetime import datetime
from utils.constants import (
    ERROR,
    FALSE,
    FORM,
    INVALID_FORM_DATA,
    NOTIFICATION_SENT_SUCCESS,
    POST,
    SUCCESS,
    TRUE,
    MESSAGE,
    NULL,
    FREE,
    USER_CREATED_SUCCESS,
    USER_DELETE_SUCCESS,
    USER_IMAGE_DELETE_SUCCESS,
    USER_IMAGE_NOT_FOUND,
    USER_NOT_FOUND,
    USER_STATUS_CHANGED_SUCCESS,
    USER_UPDATED_SUCCESS,
    FREE_TICKET_CREATED_SUCCESS,
)

# Show all Users
@login_required(login_url="admin-login")
@superuser_required
def index(request):
    try:
        context = {"GCP_BUCKET_URL": GCP_BUCKET_URL}
        return render(request, "superadmin/users/index.html", context)
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":"/admin/users"}
        return render(request,"500.html",context)


# Get all users using datatables
class UsersListView(ServerSideDatatableView):
    queryset = User.objects.exclude(is_superuser=True)
    columns = [
        "uuid",
        "email",
        "location",
        "profile_picture",
        "is_staff",
        "is_active",
        "date_joined",
    ]

# Create User
@login_required(login_url="admin-login")
@superuser_required
def create(request):
    try:
        context = {}
        if request.method == POST:
            form = UserForm(request.POST,request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, USER_CREATED_SUCCESS)
                return redirect('admin-users')
            else:                
                context = {FORM:form}
                messages.error(request, INVALID_FORM_DATA)
                return render(request,'superadmin/users/create.html',context)
        
        form = UserForm()
        context = {FORM:form}
        return render(request,'superadmin/users/create.html',context)
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":"/admin/users/create"}
        return render(request,"500.html",context)


@login_required(login_url="admin-login")
@superuser_required
def info(request, uuid):
    try:
        user = User.objects.get(uuid=uuid)
        images = UserImage.objects.filter(user=user)
        orders = (
            Order.objects.filter(user=user)
            .prefetch_related("orderitem_set")
            .order_by("-created_at")
        )
        paid_orders_amount = orders.aggregate(Sum("total"))["total__sum"]
        if paid_orders_amount is None:
            paid_orders_amount = 0
        
        joined_events = orders.count()
        return render(
            request,
            "superadmin/users/info.html",
            {"user": user,"images":images, "orders": orders,"paid_orders_amount":paid_orders_amount,"joined_events":joined_events, "GCP_BUCKET_URL": GCP_BUCKET_URL},
        )
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":"/admin/users"}
        return render(request,"500.html",context)



# Edit User
@login_required(login_url="admin-login")
@superuser_required
def edit(request,uuid):
    try:
        context = {}
        current_date = datetime.now().date()
        user = get_object_or_404(User, uuid=uuid)
        events = Event.objects.filter(date__gte=current_date).order_by("id")
        tickets = Ticket.objects.filter()
        if request.method == POST:
            form = UserForm(request.POST,request.FILES,instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, USER_CREATED_SUCCESS)
                return redirect('admin-users')
            else:                
                context = {FORM:form}
                messages.error(request, INVALID_FORM_DATA)
                return render(request,'superadmin/users/edit.html',context)
        
        form = UserForm(instance=user)
        context = {FORM:form,"user":user, 'events':events,"tickets":tickets}
        return render(request,'superadmin/users/edit.html',context)
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":f"/admin/users/edit/{uuid}"}
        return render(request,"500.html",context)


# Edit User Status
def edit_status(request, uuid):
    try:
        if request.method == "POST":
            if uuid:
                user = User.objects.get(uuid=uuid)
                status = request.POST.get("status")
                if status == "true":
                    user.is_active = True
                else:
                    user.is_active = False
                user.save()
                return JsonResponse(
                    {SUCCESS: TRUE, MESSAGE: USER_STATUS_CHANGED_SUCCESS}
                )
            return JsonResponse({SUCCESS: FALSE, ERROR: USER_NOT_FOUND})
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":f"/admin/users/edit/{uuid}"}
        return render(request,"500.html",context)
    

# Delete User
def delete(request, uuid):
    try:
        if request.method == "POST":
            if uuid:
                User.objects.get(uuid=uuid).delete()
                return JsonResponse(
                    {SUCCESS: TRUE, MESSAGE: USER_DELETE_SUCCESS}
                )
            return JsonResponse({SUCCESS: FALSE, ERROR: USER_NOT_FOUND})
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":f"/admin/users"}
        return render(request,"500.html",context)

# Delete User Image
def delete_image(request, uuid):
    try:
        if request.method == "POST":
            if uuid:
                UserImage.objects.get(uuid=uuid).delete()
                return JsonResponse(
                    {SUCCESS: TRUE, MESSAGE: USER_IMAGE_DELETE_SUCCESS}
                )
            return JsonResponse({SUCCESS: FALSE, ERROR: USER_IMAGE_NOT_FOUND})
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":f"/admin/users"}
        return render(request,"500.html",context)
    

#free ticket generate
@login_required(login_url="admin-login")
@superuser_required
def generate_ticket(request):
    try:
        if request.method == "POST":
            event = request.POST.get('event')
            ticket = request.POST.get('ticket')
            user_uuid = request.POST.get('user_uuid')

            # Retrieve the user object using the provided UUID
            user = get_object_or_404(User, uuid=user_uuid)
            user_id = user.id

            # Create an order for the free ticket
            order = Order.objects.create(
                total=0,
                event_id=event,
                user_id=user_id, 
                qty=1,
                payment_status=None,
                type=FREE
            )
            OrderItem.objects.create(price=0,order_id=order.id,ticket_id=ticket)
            
            ticket = Ticket.objects.get(id=ticket)
            original_ticket_left = ticket.left
            
            #after distribute free ticket
            if original_ticket_left > 0 :
                left_ticket = original_ticket_left - order.qty
                ticket.left = left_ticket
                ticket.save()
            
            
            return JsonResponse({SUCCESS: TRUE, MESSAGE: FREE_TICKET_CREATED_SUCCESS})
    except Exception as ex:
        return JsonResponse({SUCCESS: FALSE, ERROR: str(ex)})