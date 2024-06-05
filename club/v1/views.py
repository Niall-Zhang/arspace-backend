from django.shortcuts import render
from rest_framework import generics,status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from utils.pagination import CustomPagination
from django.db.models import Q
from rest_framework.response import Response
# Constants
from utils.constants import DATA, ERROR, EVENT_CREATED_SUCCESS, EVENT_DELETED_SUCCESS, EVENT_INFO_SUCCESS, EVENT_NOT_FOUND, EVENT_UPDATED_SUCCESS, FALSE, LIST_FETCHED_SUCCESS, MESSAGE, SUCCESS, TRUE
# Serializers
from club.serializers import CastSerializer,ClubSerializer,EventSerializer

# Models
from club.models import Cast, Club, Event

from utils.validators import format_validation_errors
from datetime import datetime

# Cast List Api
class CastListViewAPI(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    pagination_class = CustomPagination
    serializer_class = CastSerializer

    # Search Filter
    def get_queryset(self):
        queryset = Cast.objects.order_by("-name").all()
        search = self.request.query_params.get("search", None)
        if search:
            queryset = Cast.objects.filter(Q(name__icontains=search))
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
        

# Club List Api
class ClubListViewAPI(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    pagination_class = CustomPagination
    serializer_class = ClubSerializer

    # Search Filter
    def get_queryset(self):
        queryset = Club.objects.order_by("-title").all()
        search = self.request.query_params.get("search", None)
        if search:
            queryset = Club.objects.filter(Q(title__icontains=search))
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
        

# My Events
class EventsAPI(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    pagination_class = CustomPagination
    serializer_class = EventSerializer

    # Search Filter
    def get_queryset(self):
        # queryset = Event.objects.all().order_by(
        #     "-created_at"
        # )
        current_date = datetime.now().date()
        queryset = Event.objects.filter(date__gte=current_date).order_by("-created_at")
        search = self.request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(Q(title__icontains=search))
        return queryset

    # Perform Create Event
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

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

    # Create
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            response = {}
            if serializer.is_valid():
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                return Response(
                    {
                        SUCCESS: TRUE,
                        MESSAGE: EVENT_CREATED_SUCCESS,
                        DATA: serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                error = format_validation_errors(serializer)
                response[SUCCESS] = FALSE
                response[ERROR] = error
                return Response(response, status=status.HTTP_404_NOT_FOUND)

        except (AttributeError, FileNotFoundError, Exception) as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
            )
        

# My Event Info
class EventInfoAPI(generics.GenericAPIView):
    serializer_class = EventSerializer

    def get_event(self, uuid):
        try:
            return Event.objects.filter(uuid=uuid).first()
        except:
            return None
        
    

    # Info
    def get(self, request, uuid):
        try:
            event = self.get_event(uuid=uuid)
            if event == None:
                return Response(
                    {SUCCESS: FALSE, ERROR: EVENT_NOT_FOUND},
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = self.serializer_class(event, context={"request": request})

            return Response(
                {SUCCESS: TRUE, MESSAGE: EVENT_INFO_SUCCESS, DATA: serializer.data},
                status=status.HTTP_200_OK,
            )

        except (AttributeError, Exception) as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
            )

    # Update
    def put(self, request, uuid):
        try:
            event = self.get_event(uuid)
            if event == None:
                return Response(
                    {SUCCESS: FALSE, ERROR: EVENT_NOT_FOUND},
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = self.serializer_class(
                event, data=request.data, partial=True, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()

                return Response(
                    {
                        SUCCESS: TRUE,
                        MESSAGE: EVENT_UPDATED_SUCCESS,
                        DATA: serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {SUCCESS: FALSE, ERROR: serializer.errors},
                status=status.HTTP_404_NOT_FOUND,
            )

        except (AttributeError, FileNotFoundError, Exception) as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
            )

    # Delete
    def delete(self, request, uuid):
        try:
            event = self.get_event(uuid)
            if event == None:
                return Response(
                    {SUCCESS: FALSE, ERROR: EVENT_NOT_FOUND},
                    status=status.HTTP_404_NOT_FOUND,
                )

            event.delete()
            return Response(
                {SUCCESS: TRUE, MESSAGE: EVENT_DELETED_SUCCESS},
                status=status.HTTP_200_OK,
            )
        except (AttributeError, FileNotFoundError, Exception) as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
            )
        


