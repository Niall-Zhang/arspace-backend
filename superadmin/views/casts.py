from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from club.models import Cast
from superadmin.forms.casts import CastForm
from superadmin.views.views import superuser_required
from django.contrib import messages
from django_serverside_datatable.views import ServerSideDatatableView
from django.http import JsonResponse
from utils.constants import CAST_CREATED_SUCCESS, CAST_DELETED_SUCCESS, ERROR, FALSE,FORM, INVALID_REQUEST_METHOD, MESSAGE,POST,CAST_UPDATED_SUCCESS,INVALID_FORM_DATA, SUCCESS, TRUE
from arspace.settings import GCP_BUCKET_URL

# Show all Casts
@login_required(login_url="admin-login")
@superuser_required
def index(request):
    try:        
        context = {"GCP_BUCKET_URL": GCP_BUCKET_URL}
        return render(request, "superadmin/casts/index.html", context)
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":"/admin/casts"}
        return render(request,"500.html",context)


# Get all casts using datatables
class CastsListView(ServerSideDatatableView):
    queryset = (
        Cast.objects.all().order_by("-created_at")
    )
    columns = ["uuid","name","image","description","created_at"]


# Create Cast
@login_required(login_url="admin-login")
@superuser_required
def create(request):
    try:
        context = {}
        if request.method == POST:
            form = CastForm(request.POST,request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, CAST_CREATED_SUCCESS)
                return redirect('admin-casts')
            else:                
                context = {FORM:form}
                messages.error(request, INVALID_FORM_DATA)
                return render(request,'superadmin/casts/create.html',context)
        
        form = CastForm()
        context = {FORM:form}
        return render(request,'superadmin/casts/create.html',context)
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":"/admin/casts/create"}
        return render(request,"500.html",context)
    
# Cast Info
@login_required(login_url="admin-login")
@superuser_required
def edit(request, uuid):
    try:
        context = {}
        cast = get_object_or_404(Cast, uuid=uuid)
        if request.method == POST:
            form = CastForm(request.POST,request.FILES, instance=cast)
            if form.is_valid():
                form.save()
                messages.success(request, CAST_UPDATED_SUCCESS)
                return redirect('admin-casts')
            else:                
                context = {FORM:form}
                messages.error(request, INVALID_FORM_DATA)
                return render(request,'superadmin/casts/edit.html',context)
        
        form = CastForm(instance=cast)
        context = {FORM:form,"cast":cast}
        return render(request, 'superadmin/casts/edit.html', context)
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":f"/admin/casts/edit/{uuid}"}
        return render(request,"500.html",context)
    
# Delete
def delete(request, uuid):
    try:
        if request.method == 'POST':            
            cast = Cast.objects.get(uuid=uuid)
            cast.delete()
            return JsonResponse({SUCCESS:TRUE,MESSAGE:CAST_DELETED_SUCCESS})
        else:
            return JsonResponse({SUCCESS:FALSE,ERROR: INVALID_REQUEST_METHOD})
    except Exception as ex:
        messages.error(request, str(ex))
        return JsonResponse({SUCCESS:FALSE,ERROR: str(ex)})