"""
URL configuration for arspace project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from base.v1 import views
urlpatterns = [
    path("dj-admin/", admin.site.urls),
    # 500 Error Page
    path("500", views.server_error, name="500"),
    # Password Reset Token
    path("password-reset/<str:token>",views.password_reset_token,name="password-reset-token"),
    # Password Reset Confirm
    path("password-reset-confirm",views.PasswordResetConfirmView.as_view(),name="password-reset-confirm"),
    path("admin/", include("superadmin.urls")),
    path("api/v1/auth/", include("authentication.v1.urls")),    
    path("api/v1/", include("user.v1.urls")),
    path("api/v1/", include("base.v1.urls")),
    path("api/v1/", include("club.v1.urls")),
    path("api/v1/", include("order.v1.urls")),
    path("api/v1/", include("chat.v1.urls")),
]
