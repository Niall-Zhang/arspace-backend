from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from authentication.models import User
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q, Sum
from django.db.models.functions import TruncMonth
from django.contrib import messages
from base.models import Settings
from club.models import Club, Event
from order.models import Order
from utils.constants import (
    DATA,
    ERROR,
    FALSE,
    INVALID_OLD_PASSWORD,
    INVALID_PASSWORD,
    LOGIN_ACCOUNT,
    INVALID_LOGIN_CREDENTIALS,
    LOGIN_SUCCESS,
    PROFILE_CHANGED_SUCCESS,
    SETTINGS_ADDED_SUCCESS,
    SUCCESS,
    TRUE,
    MESSAGE,
    USER_NOT_FOUND,
)
from utils.utils import delete_file_from_gcp_bucket, upload_file_to_gcp_bucket

# Create your views here.
def admin_login(request):
    try:
        if request.method == "POST":
            email = request.POST.get("email")
            password = request.POST.get("password")

            try:
                user = User.objects.get(
                    Q(email=email) & Q(is_superuser=TRUE) & Q(is_staff=TRUE)
                )
            except:
                return JsonResponse({SUCCESS: FALSE, ERROR: USER_NOT_FOUND})

            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({SUCCESS: TRUE, MESSAGE: LOGIN_SUCCESS})
            else:
                return JsonResponse(
                    {SUCCESS: FALSE, ERROR: INVALID_LOGIN_CREDENTIALS}
                )
        else:
            if request.user.is_authenticated and request.user.is_superuser:
                return redirect("admin-dashboard")
            return render(request, "login.html")
    except Exception as ex:
        return JsonResponse({SUCCESS: FALSE, ERROR: ex})


# Logout User
@login_required(login_url="admin-login")
def admin_logout(request):
    logout(request)
    messages.success(request, ("Logged out."))
    return redirect("admin-login")


# Admin Dashboard
@login_required(login_url="admin-login")
def admin_dashboard(request):
    try:
        if request.user.is_authenticated & request.user.is_superuser:
            events = Event.objects.all().order_by('-created_at')
            clubs = Club.objects.all().count()
            users = User.objects.exclude(is_superuser=True).count()
            orders = Order.objects.all().order_by('-created_at')[:5]
            return render(
                request,
                "superadmin/dashboard.html",
                {
                    "events_count": events.count(),
                    "events": events[:5],
                    "clubs": clubs,
                    "users": users,
                    "orders": orders,
                    "orders_count":orders.count()
                },
            )
        else:
            return redirect("admin-login")
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":"/admin/dashboard"}
        return render(request,"500.html",context)
    

def get_total_sale(request):
    try:
        sale_by_month = Order.objects.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            total_sale=Sum('total')
        ).order_by('month')
        
        revenue_data = [{'month': entry['month'].strftime('%m'), 'total_sale': entry['total_sale']} for entry in sale_by_month]        
        return JsonResponse({SUCCESS: TRUE,DATA:revenue_data})
    except Exception as ex:
        return JsonResponse({SUCCESS: FALSE,ERROR:str(ex)})
    

# Admin Profile
@login_required(login_url="admin-login")
def admin_profile(request):
    try:
        if request.method == "POST" and request.POST.get('type') == "update_info":
            try:
                profile_picture = request.FILES.get("profile_picture")
                full_name = request.POST.get("full_name")
                phone = request.POST.get("phone")
                location = request.POST.get("location")
                latitude = request.POST.get("latitude")
                longtitude = request.POST.get("longtitude")
                dob = request.POST.get("dob")
                gender = request.POST.get("gender")
                intro = request.POST.get("intro")
                user = request.user

                # Change Profile Picture
                if profile_picture is not None:
                    upload = upload_file_to_gcp_bucket(profile_picture,"users")
                    if upload[SUCCESS]:
                        delete_file_from_gcp_bucket(user.profile_picture)
                        user.profile_picture = upload[DATA] 

                
                user.full_name = full_name
                user.phone = phone
                user.location = location
                user.latitude = latitude
                user.longtitude = longtitude
                user.dob = dob
                user.gender = gender
                user.intro = intro
                user.save()
                messages.success(request, PROFILE_CHANGED_SUCCESS)
                return redirect("admin-profile")

            except Exception as ex:
                messages.error(request, str(ex))        
                context = {ERROR:str(ex),"return_url":"/admin/profile"}
                return render(request,"500.html",context)

        elif request.method == "POST" and request.POST.get('type') == "update_password":
            try:
                current_password = request.POST.get("current_password")
                if check_password(current_password, request.user.password):
                    password = request.POST.get("password")
                    if password:
                        user = request.user
                        user.set_password(password)
                        user.save()
                        messages.success(request, PROFILE_CHANGED_SUCCESS)
                        return redirect("admin-profile")
                    messages.error(request, INVALID_PASSWORD)
                    return redirect("admin-profile")
                messages.error(request, INVALID_OLD_PASSWORD)
                return redirect("admin-profile")
            except Exception as ex:
                messages.error(request, str(ex))        
                context = {ERROR:str(ex),"return_url":"/admin/profile"}
                return render(request,"500.html",context)

        if request.user.is_authenticated & request.user.is_superuser:
            users = User.objects.exclude(is_superuser=True).count()
            return render(
                request,
                "superadmin/profile.html",
                {
                    "users": users,
                },
            )
        else:
            messages.error(request, LOGIN_ACCOUNT)  
            return redirect("admin-login")
    except Exception as ex:
        messages.error(request, str(ex))        
        context = {ERROR:str(ex),"return_url":"/admin/profile"}
        return render(request,"500.html",context)
    

# Admin Settings Page
def admin_settings(request):
    try:
        if request.method == "POST":
            meta_keys = [
                "stripe_publishable_key",
                "stripe_secret_key",
                "fees"
            ]

            for key in meta_keys:
                value = request.POST.get(key)
                if value is not None:
                    Settings.objects.update_or_create(
                        meta_key=key, defaults={"meta_value": value}
                    )
            messages.success(request, SETTINGS_ADDED_SUCCESS)
        return render(request,"superadmin/settings.html")
    except Exception as ex:
        messages.error(request, str(ex))
        context = {ERROR:str(ex),"return_url":"/admin/settings"}
        return render(request,"500.html",context)
    
