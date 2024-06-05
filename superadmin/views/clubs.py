from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from club.models import Club
from superadmin.forms.clubs import ClubForm
from superadmin.views.views import superuser_required
from django.contrib import messages
from django_serverside_datatable.views import ServerSideDatatableView
from django.http import JsonResponse
from utils.constants import CLUB_CREATED_SUCCESS, CLUB_DELETED_SUCCESS, ERROR, FALSE,FORM, INVALID_REQUEST_METHOD, MESSAGE,POST,CLUB_UPDATED_SUCCESS,INVALID_FORM_DATA, SUCCESS, TRUE

# Show all Clubs
@login_required(login_url="admin-login")
@superuser_required
def index(request):
    try:
        context = {}
        return render(request, "superadmin/clubs/index.html", context)
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":"/admin/clubs"}
        return render(request,"500.html",context)


# Get all clubs using datatables
class ClubsListView(ServerSideDatatableView):
    queryset = (
        Club.objects.all().order_by("-created_at")
    )
    columns = ["uuid", "user__email","title", "contact_no" ,"created_at"]


# Create Club
@login_required(login_url="admin-login")
@superuser_required
def create(request):
    try:
        context = {}
        if request.method == POST:
            form = ClubForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, CLUB_CREATED_SUCCESS)
                return redirect('admin-clubs')
            else:                
                context = {FORM:form}
                messages.error(request, INVALID_FORM_DATA)
                return render(request,'superadmin/clubs/create.html',context)
        
        form = ClubForm()
        context = {FORM:form}
        return render(request,'superadmin/clubs/create.html',context)
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":"/admin/clubs/create"}
        return render(request,"500.html",context)
    
# Club Info
@login_required(login_url="admin-login")
@superuser_required
def edit(request, uuid):
    try:
        context = {}
        club = get_object_or_404(Club, uuid=uuid)
        if request.method == POST:
            form = ClubForm(request.POST, instance=club)
            if form.is_valid():
                form.save()
                messages.success(request, CLUB_UPDATED_SUCCESS)
                return redirect('admin-clubs')
            else:                
                context = {FORM:form}
                messages.error(request, INVALID_FORM_DATA)
                return render(request,'superadmin/clubs/edit.html',context)
        
        form = ClubForm(instance=club)
        context = {FORM:form}
        return render(request, 'superadmin/clubs/edit.html', context)
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":f"/admin/clubs/edit/{uuid}"}
        return render(request,"500.html",context)
    
# Delete
def delete(request, uuid):
    try:
        if request.method == 'POST':            
            club = Club.objects.get(uuid=uuid)
            club.delete()
            return JsonResponse({SUCCESS:TRUE,MESSAGE:CLUB_DELETED_SUCCESS})
        else:
            return JsonResponse({SUCCESS:FALSE,ERROR: INVALID_REQUEST_METHOD})
    except Exception as ex:
        messages.error(request, str(ex))
        return JsonResponse({SUCCESS:FALSE,ERROR: str(ex)})