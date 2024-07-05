import json
import os
import traceback

from django.http import Http404, JsonResponse
from authentication.serializers import PasswordResetConfirmSerializer
from rest_framework import generics
from rest_framework.decorators import permission_classes,api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework import viewsets
from base.serializers import InterestSerializer
from utils.pagination import CustomPagination
from utils.validators import format_validation_errors
from rest_framework.response import Response
from rest_framework import status
from utils.constants import (
    INVALID_TOKEN,
    LIST_FETCHED_SUCCESS,
    PASSWORD_RESET_SUCCESS,
    SUCCESS,
    ERROR,
    DATA,
    MESSAGE,
    TRUE,
    FALSE,
)
from authentication.models import PasswordReset, User
from base.models import Interest
from django.shortcuts import render,HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.messages import success, error
from rest_framework.authtoken.models import Token

# Create your views here.
def server_error(request):
    try:
        context = {}
        return render(request, "500.html", context)
    except Exception as ex:
        return HttpResponse(str(ex))        
        

# Interest API
class InterestAPI(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    pagination_class = CustomPagination
    serializer_class = InterestSerializer

    # Search Filter
    def get_queryset(self):
        queryset = Interest.objects.order_by("title").all()
        return queryset

    def get(self, request):
        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    SUCCESS: TRUE,
                    MESSAGE: LIST_FETCHED_SUCCESS,
                    DATA: serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except (AttributeError, FileNotFoundError, Exception) as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
            )


# Password Reset Token
@api_view(["GET","POST"])
def password_reset_token(request,token):
    try:
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            # Validations
            if password is None and confirm_password is None:
                return HttpResponse("Password & Confirm Password are required.")
            elif password is None:
                return HttpResponse("Confirm Password is required.")
            elif confirm_password is None:
                return HttpResponse("Confirm Password is required.")
            
            # Change Password
            if password == confirm_password:
                is_password_reset_exists = PasswordReset.objects.filter(token=token).exists()
                if is_password_reset_exists:
                    password_reset = PasswordReset.objects.get(token=token)
                    user = password_reset.user
                    user.set_password(password)
                    user.save()
                    # Delete token
                    PasswordReset.objects.get(token=token).delete()
                    success(request, 'Password has been changed successfully.')
                    return redirect(f'/password-reset/{token}?success=true')
                error(request, 'Password reset token is expired or invalid.')
                return redirect(f'/password-reset/{token}?error=false')
            error(request, 'Password & Confirm Password does not matched.')
            return redirect(f'/password-reset/{token}?error=false')
            
        context = {"token":token}
        return render(request, "password-reset-token.html", context=context)
    except (AttributeError, FileNotFoundError, Exception) as ex:
        return render(request, "password-reset-token.html", context=context)
    


# Password Reset Cofirm View
class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        try:
            response = {}
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.is_valid(raise_exception=True)

                token = serializer.validated_data["token"]
                password = serializer.validated_data["password"]

                try:
                    password_reset = PasswordReset.objects.get(token=token)
                except PasswordReset.DoesNotExist as ex:
                    return Response(
                        {SUCCESS: FALSE, ERROR: INVALID_TOKEN},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                
                user = password_reset.user
                user.set_password(password)
                user.save()

                # Logout User from all sessions
                Token.objects.filter(user=user).delete()

                # Delete the password reset entry
                password_reset.delete()

                return Response(
                    {SUCCESS: TRUE, MESSAGE: PASSWORD_RESET_SUCCESS},
                    status=status.HTTP_200_OK,
                )
            else:
                error = format_validation_errors(serializer)
                response[SUCCESS] = FALSE
                response[ERROR] = error
                return Response(response, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)},
                status=status.HTTP_404_NOT_FOUND,
            )
    
#to make file read from well-known folder
def serve_well_known(request, filename):
    well_known_dir = os.path.join(os.path.dirname(__file__), '../../.well-known')
    file_path = os.path.join(well_known_dir, filename)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        content_type = 'application/json' if filename.endswith('.json') else 'text/plain'
        return HttpResponse(content, content_type=content_type)
    except FileNotFoundError:
        raise Http404(f"{filename} not found")