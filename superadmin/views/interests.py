from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from base.models import Interest
from superadmin.forms.interests import InterestForm
from superadmin.views.views import superuser_required
from django.contrib import messages
from django_serverside_datatable.views import ServerSideDatatableView
from django.http import JsonResponse
from utils.constants import INTEREST_CREATED_SUCCESS, INTEREST_DELETED_SUCCESS, ERROR, FALSE,FORM, INVALID_REQUEST_METHOD, MESSAGE,POST,INTEREST_UPDATED_SUCCESS,INVALID_FORM_DATA, SUCCESS, TRUE

# Show all Interests
@login_required(login_url="admin-login")
@superuser_required
def index(request):
    try:
        context = {}
        return render(request, "superadmin/interests/index.html", context)
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":"/admin/interests"}
        return render(request,"500.html",context)


# Get all interests using datatables
class InterestsListView(ServerSideDatatableView):
    queryset = (
        Interest.objects.all().order_by("-created_at")
    )
    columns = ["uuid", "title","created_at"]


# Create Interest
@login_required(login_url="admin-login")
@superuser_required
def create(request):
    try:
        context = {}
        if request.method == POST:
            form = InterestForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, INTEREST_CREATED_SUCCESS)
                return redirect('admin-interests')
            else:                
                context = {FORM:form}
                messages.error(request, INVALID_FORM_DATA)
                return render(request,'superadmin/interests/create.html',context)
        
        form = InterestForm()
        context = {FORM:form}
        return render(request,'superadmin/interests/create.html',context)
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":"/admin/interests/create"}
        return render(request,"500.html",context)
    
# Interest Info
@login_required(login_url="admin-login")
@superuser_required
def edit(request, uuid):
    try:
        context = {}
        interest = get_object_or_404(Interest, uuid=uuid)
        if request.method == POST:
            form = InterestForm(request.POST, instance=interest)
            if form.is_valid():
                form.save()
                messages.success(request, INTEREST_UPDATED_SUCCESS)
                return redirect('admin-interests')
            else:                
                context = {FORM:form}
                messages.error(request, INVALID_FORM_DATA)
                return render(request,'superadmin/interests/edit.html',context)
        
        form = InterestForm(instance=interest)
        context = {FORM:form}
        return render(request, 'superadmin/interests/edit.html', context)
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":f"/admin/interests/edit/{uuid}"}
        return render(request,"500.html",context)
    
# Delete
def delete(request, uuid):
    try:
        if request.method == 'POST':            
            interest = Interest.objects.get(uuid=uuid)
            interest.delete()
            return JsonResponse({SUCCESS:TRUE,MESSAGE:INTEREST_DELETED_SUCCESS})
        else:
            return JsonResponse({SUCCESS:FALSE,ERROR: INVALID_REQUEST_METHOD})
    except Exception as ex:
        messages.error(request, str(ex))
        return JsonResponse({SUCCESS:FALSE,ERROR: str(ex)})