from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from superadmin.views.views import superuser_required
from arspace.settings import GCP_BUCKET_URL
from django.contrib import messages
from django_serverside_datatable.views import ServerSideDatatableView
from order.models import Order
from utils.constants import ERROR

# Show all Orders
@login_required(login_url="admin-login")
@superuser_required
def index(request):
    try:
        context = {"GCP_BUCKET_URL": GCP_BUCKET_URL}
        return render(request, "superadmin/orders/index.html", context)
    except Exception as ex:
        messages.error(request, ex)
        return redirect("admin-dashboard")


# Get all orders using datatables
class OrdersListView(ServerSideDatatableView):
    queryset = (
        Order.objects.all().prefetch_related("orderitem_set").order_by("-created_at")
    )
    columns = ["uuid", "user__email", "event__title", "total", "payment_status", "created_at"]


# Order Info
@login_required(login_url="admin-login")
@superuser_required
def info(request, uuid):
    try:
        order = Order.objects.prefetch_related("orderitem_set").get(uuid=uuid)
        return render(
            request,
            "superadmin/orders/info.html",
            {"order": order},
        )
    except Exception as ex:
        messages.error(request, ex)        
        context = {ERROR:str(ex),"return_url":"/admin/orders"}
        return render(request,"500.html",context)