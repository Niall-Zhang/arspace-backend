"""
Routes for superadmin
"""
from django.urls import path, include
from superadmin.views import auth
from superadmin.views import interests
from superadmin.views import clubs
from superadmin.views import casts
from superadmin.views import events
from superadmin.views import users
from superadmin.views import orders
from superadmin.views import tickets
from superadmin.views import notification


urlpatterns = [
    # Auth
    path("login", auth.admin_login, name="admin-login"),
    path("logout", auth.admin_logout, name="admin-logout"),
    path("dashboard", auth.admin_dashboard, name="admin-dashboard"),
    path("profile", auth.admin_profile, name="admin-profile"),
    path("settings", auth.admin_settings, name="admin-settings"),
    path("get-total-sale", auth.get_total_sale, name="get-total-sale"),

    # Interests
    path("interests", interests.index, name="admin-interests"),
    path("interests/list", interests.InterestsListView.as_view(), name="admin-interests-list"),
    path("interests/create", interests.create, name="admin-interests-create"),
    path("interests/edit/<uuid:uuid>", interests.edit, name="admin-interests-edit"),
    path("interests/delete/<uuid:uuid>", interests.delete, name="admin-interests-delete"),

    # Clubs
    path("clubs", clubs.index, name="admin-clubs"),
    path("clubs/list", clubs.ClubsListView.as_view(), name="admin-clubs-list"),
    path("clubs/create", clubs.create, name="admin-clubs-create"),
    path("clubs/edit/<uuid:uuid>", clubs.edit, name="admin-clubs-edit"),
    path("clubs/delete/<uuid:uuid>", clubs.delete, name="admin-clubs-delete"),

    # Casts
    path("casts", casts.index, name="admin-casts"),
    path("casts/list", casts.CastsListView.as_view(), name="admin-casts-list"),
    path("casts/create", casts.create, name="admin-casts-create"),
    path("casts/edit/<uuid:uuid>", casts.edit, name="admin-casts-edit"),
    path("casts/delete/<uuid:uuid>", casts.delete, name="admin-casts-delete"),

    # Tickets
    path("tickets", tickets.index, name="admin-tickets"),
    path("tickets/list", tickets.TicketsListView.as_view(), name="admin-tickets-list"),
    path("tickets/create", tickets.create, name="admin-tickets-create"),
    path("tickets/edit/<uuid:uuid>", tickets.edit, name="admin-tickets-edit"),
    path("tickets/delete/<uuid:uuid>", tickets.delete, name="admin-tickets-delete"),

    # Events
    path("events", events.index, name="admin-events"),
    path("events/list", events.EventsListView.as_view(), name="admin-events-list"),
    path("events/create", events.create, name="admin-events-create"),
    path("events/edit/<uuid:uuid>", events.edit, name="admin-events-edit"),
    path("events/images/<uuid:uuid>/delete", events.images_delete, name="admin-events-images-delete"),
    path("events/delete/<uuid:uuid>", events.delete, name="admin-events-delete"),
    

    # Users
    path("users", users.index, name="admin-users"),
    path("users/list", users.UsersListView.as_view(), name="admin-users-list"),
    path("users/create", users.create, name="admin-users-create"),
    path("users/<uuid:uuid>", users.info, name="admin-users-info"),
    path("users/edit/<uuid:uuid>", users.edit, name="admin-users-edit"),
    path("users/status/<uuid:uuid>", users.edit_status, name="admin-users-status"),
    path("users/delete/<uuid:uuid>", users.delete, name="admin-users-delete"),
    path("users/delete/<uuid:uuid>/image", users.delete_image, name="admin-users-delete-image"),
    
    # Orders
    path("orders", orders.index, name="admin-orders"),
    path("orders/list", orders.OrdersListView.as_view(), name="admin-orders-list"),
    path("orders/<uuid:uuid>", orders.info, name="admin-orders-info"),


    #send notification to topics
    path("send-notification-to-topics", notification.send_notification_to_topics, name="send-notification-to-topics"),
    path("notification", notification.send_notification_form, name="notification"),


    #generate ticket

    path('ticket', users.generate_ticket, name="generate-ticket")



    

    
]   