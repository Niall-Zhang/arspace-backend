"""
User Urls
"""
from django.contrib import admin
from django.urls import path
from user.v1 import views

urlpatterns = [
    path("profile", views.UserProfileView.as_view()),
    path("profile/<uuid>", views.get_user_by_id),
    path("block/<uuid>", views.block_user, name="block"),
    path("block-list", views.block_list, name="block-list"),
    
    path("image/<uuid:uuid>", views.DeleteUserImageAPIView.as_view()),
    
    
    # Events
    path(
        "favourite/events", views.FavouriteEventsAPI.as_view(), name="favourite-events"
    ),
    path(
        "favourite/events/<uuid:uuid>",
        views.FavouriteEventAPI.as_view(),
        name="favourite-events",
    ),
    # Cards
    path("cards", views.CardAPIView.as_view(), name="cards"),
    path("cards/<uuid:uuid>", views.CardInfoView.as_view(), name="cards-info"),
    # Favourite Users
    path("favourite/users", views.FavouriteUsersAPI.as_view(), name="favourite-users"),
    path(
        "favourite/users/<uuid:uuid>",
        views.FavouriteUserAPI.as_view(),
        name="favourite-users",
    ),
    # Requests
    path("chat-requests", views.ChatRequestsAPIView.as_view(), name="chat-requests"),
    path(
        "chat-requests/<uuid:uuid>",
        views.ChatRequestAPIView.as_view(),
        name="accept-reject-chat-requests",
    ),
]
