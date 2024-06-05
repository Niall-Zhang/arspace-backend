from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from utils.constants import (
    COUNT,
    DATA,
    ERROR,
    FALSE,
    LIST_FETCHED_SUCCESS,
    LIST_NOT_FOUND,
    MESSAGE,
    NEXT,
    PREVIOUS,
    SUCCESS,
    TRUE,
)


class CustomPagination(PageNumberPagination):
    page_size_query_param = "limit"

    def get_paginated_response(self, data):
        if data and len(data) > 0:
            return Response(
                {
                    SUCCESS: TRUE,
                    MESSAGE: LIST_FETCHED_SUCCESS,
                    COUNT: self.page.paginator.count,
                    NEXT: self.get_next_link(),
                    PREVIOUS: self.get_previous_link(),
                    DATA: data,
                }
            )
        else:
            return Response(
                {
                    SUCCESS: FALSE,
                    ERROR: LIST_NOT_FOUND,
                }
            )
        
