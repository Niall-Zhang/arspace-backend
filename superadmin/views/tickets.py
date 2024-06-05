from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from club.models import Ticket
from superadmin.forms.tickets import TicketForm
from superadmin.views.views import superuser_required
from django.contrib import messages
from django_serverside_datatable.views import ServerSideDatatableView
from django.http import JsonResponse
from utils.constants import TICKET_CREATED_SUCCESS, TICKET_DELETED_SUCCESS, ERROR, FALSE,FORM, INVALID_REQUEST_METHOD, MESSAGE,POST,TICKET_UPDATED_SUCCESS,INVALID_FORM_DATA, SUCCESS, TRUE

# Show all Tickets
@login_required(login_url="admin-login")
@superuser_required
def index(request):
    try:
        context = {}
        return render(request, "superadmin/tickets/index.html", context)
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":"/admin/tickets"}
        return render(request,"500.html",context)


# Get all tickets using datatables
class TicketsListView(ServerSideDatatableView):
    queryset = (
        Ticket.objects.all().order_by("-created_at")
    )
    columns = ["uuid", "name", "price","left","units" ,"created_at"]


# Create Ticket
@login_required(login_url="admin-login")
@superuser_required
def create(request):
    try:
        context = {}
        if request.method == POST:
            form = TicketForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, TICKET_CREATED_SUCCESS)
                return redirect('admin-tickets')
            else:                
                context = {FORM:form}
                messages.error(request, INVALID_FORM_DATA)
                return render(request,'superadmin/tickets/create.html',context)
        
        form = TicketForm()
        context = {FORM:form}
        return render(request,'superadmin/tickets/create.html',context)
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":"/admin/tickets/create"}
        return render(request,"500.html",context)
    
# Ticket Info
@login_required(login_url="admin-login")
@superuser_required
def edit(request, uuid):
    try:
        context = {}
        club = get_object_or_404(Ticket, uuid=uuid)
        if request.method == POST:
            form = TicketForm(request.POST, instance=club)
            if form.is_valid():
                form.save()
                messages.success(request, TICKET_UPDATED_SUCCESS)
                return redirect('admin-tickets')
            else:                
                context = {FORM:form}
                messages.error(request, INVALID_FORM_DATA)
                return render(request,'superadmin/tickets/edit.html',context)
        
        form = TicketForm(instance=club)
        context = {FORM:form}
        return render(request, 'superadmin/tickets/edit.html', context)
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":f"/admin/tickets/edit{uuid}"}
        return render(request,"500.html",context)
    
# Delete
def delete(request, uuid):
    try:
        if request.method == 'POST':            
            club = Ticket.objects.get(uuid=uuid)
            club.delete()
            return JsonResponse({SUCCESS:TRUE,MESSAGE:TICKET_DELETED_SUCCESS})
        else:
            return JsonResponse({SUCCESS:FALSE,ERROR: INVALID_REQUEST_METHOD})
    except Exception as ex:
        messages.error(request, str(ex))
        return JsonResponse({SUCCESS:FALSE,ERROR: str(ex)})