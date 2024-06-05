"""
Orders Urls
"""
from django.contrib import admin
from django.urls import path
from order.v1 import views

urlpatterns = [
    path("orders", views.OrderAPIView.as_view(),name="orders"),
    path("tickets", views.TicketListView.as_view(),name="tickets"),
    path("orders/<uuid:uuid>", views.OrderInfoAPIView.as_view(),name="orders-info"),
    path("event/<uuid:uuid>/users", views.EventUsersAPIView.as_view(),name="order-event-users"),
    # Order History
    path("order/history", views.OrderHistoryAPIView.as_view(),name="order-history"),
    # Verify Order
    path("order/<uuid:uuid>", views.VerifyOrderAPIView.as_view(),name="verify-order"),
]
