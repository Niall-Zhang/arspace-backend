"""
Auth Urls
"""
from django.contrib import admin
from django.urls import path
from authentication.v1 import views

urlpatterns = [
    # Register
    path("register", views.UserRegistrationView.as_view(), name="register"),
    # Verify User Otp
    path("verify-otp", views.UserVerificationView.as_view(), name="verify-otp"),
    # Login
    path("login", views.UserLoginAPIView.as_view(), name="login"),
    # Password Reset
    path(
        "password-reset",
        views.PasswordResetRequestView.as_view(),
        name="password-reset",
    ),
    # Resend Verification Otp
    path(
        "resend-verification-otp",
        views.ResendVerificationOtpView.as_view(),
        name="resend-verification-otp",
    ),
    # Logout
    path("logout", views.LogoutAPIView.as_view(), name="logout"),
    path("check-email", views.is_email_exists, name="check-email"),
    path("check-username", views.is_username_exists, name="check-username"),
    path(
        "check-token-expiration",
        views.CheckTokenExpiration.as_view(),
        name="check-token-expiration",
    ),
    # Clear logs
    path("clear_logs", views.clear_logs, name="clear_logs"),
    # Test
    path("test", views.test, name="test"),
]
