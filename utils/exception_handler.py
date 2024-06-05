from rest_framework.views import exception_handler
from utils.constants import SUCCESS, ERROR
from rest_framework.exceptions import PermissionDenied
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None and response.status_code == 401:
        response.data[SUCCESS] = False
        response.data[ERROR] = "Invalid request or token."
        response.status_code = status.HTTP_401_UNAUTHORIZED

    elif response is not None and response.status_code == 405:
        response.data[SUCCESS] = False
        response.data[ERROR] = "Method not allowed."
        response.status_code = status.HTTP_404_NOT_FOUND

    elif response is not None and response.status_code == 500:
        response.data[SUCCESS] = False
        response.data[ERROR] = "Server error."
        response.status_code = status.HTTP_404_NOT_FOUND

    elif response is not None and response.status_code == 403:
        response.data[SUCCESS] = False
        response.data[ERROR] = "You don't have permission to perform this action."
        response.status_code = status.HTTP_404_NOT_FOUND

    else:
        response.data[SUCCESS] = False
        response.data[ERROR] = "Some error occurred."
        # response.status_code = status.HTTP_404_NOT_FOUND

    return response
