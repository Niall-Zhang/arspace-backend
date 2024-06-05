"""
Club/Events Urls
"""
from django.contrib import admin
from django.urls import path
from club.v1 import views

urlpatterns = [
    # Casts
    path("casts", views.CastListViewAPI.as_view(), name="casts"),
    # Clubs
    path("clubs", views.ClubListViewAPI.as_view(), name="clubs"),
    # Events
    path("events", views.EventsAPI.as_view(), name="events"),
    # Event Info
    path("events/<uuid:uuid>", views.EventInfoAPI.as_view(), name="events-info"),
    
]
