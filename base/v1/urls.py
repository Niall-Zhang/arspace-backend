"""
Base Urls
"""
from django.contrib import admin
from django.urls import path
from base.v1 import views

urlpatterns = [
     
     
    
    # Interests
    path("interests", views.InterestAPI.as_view(), name="interests"),
]
