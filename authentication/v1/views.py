from django.http import HttpResponse
from django.shortcuts import get_object_or_404,render,redirect
from django.contrib.messages import success, error
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from authentication.models import PasswordReset, User
from authentication.serializers import (
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    UserRegistrationSerializer,    
)

from django.contrib.auth.password_validation import validate_password
from user.serializers import UserProfileSerializer
from utils.stripe import create_stripe_customer

# from utils.mailer_send import send_email_using_mailersend, test_mailer
from utils.user import (
    generate_token,
    is_user_exists_and_verified,
    is_user_exists_but_not_verified,
)
from utils.utils import (
    generate_otp,
    send_password_reset_token,
    send_verification_otp,
    subscribe_user_to_topic,
    send_messages_to_topics,
)
from utils.validators import format_validation_errors
from rest_framework.views import APIView

from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import update_session_auth_hash
from utils.constants import (
    EMAIL,
    EMAIL_ALREADY_EXISTS_AND_NAVIGATE_TO_LOGIN,
    EMAIL_DOES_NOT_EXIST,
    EMAIL_IS_AVAILABLE,
    EMAIL_NOT_AVAILABLE,
    INVALID_EMAIL,
    INVALID_EMAIL_OR_OTP,
    INVALID_MESSAGE,
    INVALID_OTP,
    INVALID_TOKEN,
    INVALID_USERNAME,
    IS_LOGIN,
    IS_VERIFIED,
    LOGOUT_SUCCESSFULLY,
    OTP_SEND_FAILED,
    OTP_SEND_SUCCESS,
    OTP_SENT_FAILED,
    OTP_SENT_SUCCESS,
    OTP_VERIFIED_FAILED,
    OTP_VERIFIED_SUCCESS,
    PASSWORD_RESET_SUCCESS,
    SUCCESS,
    ERROR,
    DATA,
    MESSAGE,
    TOKEN,
    TOKEN_EXPIRED,
    TOKEN_SEND_EMAIL_FAILED,
    TOKEN_SEND_EMAIL_SUCCESS,
    TRUE,
    FALSE,
    LOGIN_SUCCESS,
    INVALID_LOGIN_CREDENTIALS,
    INVALID_PHONE_NUMBER,
    USER,
    USER_ID,
    USER_NOT_FOUND,
    USER_VERIFICATION_SUCCESS,
    USERNAME_IS_AVAILABLE,
    USERNAME_NOT_AVAILABLE,
    VALID_TOKEN,
    SEND_MESSAGE_TO_TOPIC,
)

from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model
import uuid
from rest_framework.authtoken.models import Token
from arspace import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

import logging
logger = logging.getLogger(__name__)

# Logout
class LogoutAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            request.auth.delete()
            return Response(
                {SUCCESS: TRUE, MESSAGE: LOGOUT_SUCCESSFULLY}, status=status.HTTP_200_OK
            )

        except Exception as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)},
                status=status.HTTP_404_NOT_FOUND,
            )


# Check if email is already exists
@api_view(["POST"])
def is_email_exists(request):
    try:
        email = request.data.get("email")
        if email:
            is_exists = User.objects.filter(email=email).exists()
            if is_exists:
                return Response(
                    {SUCCESS: FALSE, ERROR: EMAIL_NOT_AVAILABLE},
                    status=status.HTTP_404_NOT_FOUND,
                )

            return Response(
                {SUCCESS: TRUE, MESSAGE: EMAIL_IS_AVAILABLE},
                status=status.HTTP_200_OK,
            )
        return Response(
            {SUCCESS: FALSE, ERROR: INVALID_EMAIL},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as ex:
        return Response(
            {SUCCESS: FALSE, ERROR: str(ex)},
            status=status.HTTP_404_NOT_FOUND,
        )


# Check if username is already exists
@api_view(["POST"])
def is_username_exists(request):
    try:
        username = request.data.get("username")
        if username:
            is_exists = User.objects.filter(username=username).exists()
            if is_exists:
                return Response(
                    {SUCCESS: FALSE, ERROR: USERNAME_NOT_AVAILABLE},
                    status=status.HTTP_404_NOT_FOUND,
                )

            return Response(
                {SUCCESS: TRUE, MESSAGE: USERNAME_IS_AVAILABLE},
                status=status.HTTP_200_OK,
            )
        return Response(
            {SUCCESS: FALSE, ERROR: INVALID_USERNAME},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as ex:
        return Response(
            {SUCCESS: FALSE, ERROR: str(ex)},
            status=status.HTTP_404_NOT_FOUND,
        )


# User Registration View
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        try:
            response = {}
            serializer = self.get_serializer(data=request.data)
            # If user exists but not verified
            is_exists = is_user_exists_but_not_verified(request.data["email"])

            if is_exists[SUCCESS]:
                is_sent = send_verification_otp(request.data["email"])
                if is_sent[SUCCESS]:
                    return Response(
                        {SUCCESS: TRUE, MESSAGE: OTP_SEND_SUCCESS, IS_VERIFIED: FALSE},
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    {SUCCESS: FALSE, ERROR: OTP_SEND_FAILED},
                    status=status.HTTP_404_NOT_FOUND,
                )
            # If user exists and verified
            is_exists = is_user_exists_and_verified(request.data["email"])

            if is_exists[SUCCESS]:
                return Response(
                    {
                        SUCCESS: TRUE,
                        MESSAGE: EMAIL_ALREADY_EXISTS_AND_NAVIGATE_TO_LOGIN,
                        IS_LOGIN: TRUE,
                        IS_VERIFIED: TRUE,
                    },
                    status=status.HTTP_200_OK,
                )
            # If user do not exists
            if serializer.is_valid():
                serializer.is_valid(raise_exception=True)
                serializer.save()
                is_sent = send_verification_otp(serializer.data["email"])
                # Create customer on stripe
                create_stripe_customer(serializer.data["email"])
                if is_sent:
                    return Response(
                        {SUCCESS: TRUE, MESSAGE: OTP_SEND_SUCCESS},
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    {SUCCESS: FALSE, ERROR: OTP_SEND_FAILED},
                    status=status.HTTP_404_NOT_FOUND,
                )

            else:
                error = format_validation_errors(serializer)
                response[SUCCESS] = FALSE
                response[ERROR] = error
                return Response(response, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            logger.error(f"method:create(), error: {str(ex)}")
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)},
                status=status.HTTP_404_NOT_FOUND,
            )


# User Verification View
class UserVerificationView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            email = request.data.get("email", "")
            otp = request.data.get("otp", "")

            try:
                user = User.objects.get(email=email, otp=otp)
            except User.DoesNotExist:
                return Response(
                    {SUCCESS: FALSE, ERROR: INVALID_EMAIL_OR_OTP},
                    status=status.HTTP_404_NOT_FOUND,
                )

            user.email_verified = True
            user.is_active = True
            user.otp = None
            user.save()
            token = generate_token(user)
            serializer = UserProfileSerializer(user)
            return Response(
                {
                    SUCCESS: TRUE,
                    MESSAGE: USER_VERIFICATION_SUCCESS,
                    TOKEN: token.key,
                    DATA: serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)},
                status=status.HTTP_404_NOT_FOUND,
            )


# User Login View
class UserLoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                serializer.is_valid(raise_exception=True)

                user = serializer.validated_data
                token = generate_token(user)
                user = UserProfileSerializer(user)
                user_device_token = user.data.get('device_token')
                if user_device_token is not None:
                    subscribe_user_to_topic(user_device_token)

                return Response(
                    {
                        SUCCESS: TRUE,
                        MESSAGE: LOGIN_SUCCESS,
                        TOKEN: token.key,
                        DATA: user.data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {
                    SUCCESS: FALSE,
                    ERROR: INVALID_LOGIN_CREDENTIALS,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)},
                status=status.HTTP_404_NOT_FOUND,
            )


# Password Reset View
class PasswordResetRequestView(generics.CreateAPIView):
    serializer_class = PasswordResetSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data["email"]
                user = get_user_model().objects.filter(email=email).first()

                if user:
                    # Generate a unique token
                    token = uuid.uuid4()

                    # Create a Password Reset token
                    password_reset = PasswordReset.objects.update_or_create(
                        user=user, defaults={"token": token}
                    )
                    is_sent = send_password_reset_token(token, email)
                    if is_sent:
                        return Response(
                            {SUCCESS: TRUE, MESSAGE: TOKEN_SEND_EMAIL_SUCCESS},
                            status=status.HTTP_200_OK,
                        )
                    return Response(
                        {SUCCESS: TRUE, MESSAGE: TOKEN_SEND_EMAIL_FAILED},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {SUCCESS: FALSE, ERROR: EMAIL_DOES_NOT_EXIST},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            return Response(
                {
                    SUCCESS: FALSE,
                    ERROR: INVALID_EMAIL,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)},
                status=status.HTTP_404_NOT_FOUND,
            )


# Resend Verification Otp View
class ResendVerificationOtpView(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        try:
            # If user exists but not verified
            is_exists = is_user_exists_but_not_verified(request.data["email"])
            if is_exists[SUCCESS]:
                is_sent = send_verification_otp(request.data["email"])
                if is_sent[SUCCESS]:
                    return Response(
                        {SUCCESS: TRUE, MESSAGE: OTP_SEND_SUCCESS},
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    {SUCCESS: FALSE, ERROR: OTP_SEND_FAILED},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # If user exists and verified
            is_exists = is_user_exists_and_verified(request.data["email"])
            if is_exists[SUCCESS]:
                return Response(
                    {
                        SUCCESS: TRUE,
                        MESSAGE: EMAIL_ALREADY_EXISTS_AND_NAVIGATE_TO_LOGIN,
                        IS_LOGIN: TRUE,
                    },
                    status=status.HTTP_200_OK,
                )

            # If user does not exists
            return Response(
                {SUCCESS: FALSE, ERROR: USER_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)},
                status=status.HTTP_404_NOT_FOUND,
            )




# Check Token Expiration
class CheckTokenExpiration(APIView):
    def post(self, request):
        token_key = request.data.get(TOKEN)

        if not token_key:
            return Response({ERROR: INVALID_TOKEN}, status=status.HTTP_404_NOT_FOUND)

        try:
            token = Token.objects.get(key=token_key)
            return Response(
                {SUCCESS: TRUE, MESSAGE: VALID_TOKEN},
                status=status.HTTP_200_OK,
            )
        except Token.DoesNotExist:
            return Response(
                {SUCCESS: FALSE, MESSAGE: TOKEN_EXPIRED},
                status=status.HTTP_401_UNAUTHORIZED,
            )




# Clear Logs
def clear_logs(request):
    try:
        with open("logs/debug.log", "w"):
            pass
        return HttpResponse("Logs are cleared.")
    except Exception as ex:
        return HttpResponse(ex)


# Test
def test(request):
    try:
        data = {}
        # data = test_mailer()
        # data = send_email_using_mailersend()
        return Response(
            {SUCCESS: TRUE, DATA: data},
            status=status.HTTP_200_OK,
        )
    except Exception as ex:
        return Response(
            {SUCCESS: FALSE, ERROR: str(ex)},
            status=status.HTTP_404_NOT_FOUND,
        )
    
