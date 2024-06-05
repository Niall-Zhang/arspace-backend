
from django.shortcuts import render
from rest_framework import generics,status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from authentication.models import User
from club.models import Event, EventTicket, Ticket
from user.models import FavouriteUser
from utils.pagination import CustomPagination
from django.db.models import Q
from rest_framework.response import Response
from datetime import datetime, timedelta

# Constants
from utils.constants import DATA, ERROR, EVENT_HAS_EXPIRED, EXPIRED, FALSE, FEMALE, INVALID_QTY, INVALID_TICKET_ID, LIST_FETCHED_SUCCESS, MALE, MESSAGE, NOT_VERIFIED, ORDER_CREATED_SUCCESS, ORDER_INFO_SUCCESS, ORDER_NOT_FOUND, STATUS, SUCCESS, TICKET_ALREADY_VERIFIED, TICKET_INVALID, TICKET_NOT_FOUND, TICKET_VERIFIED, TRUE, TICKET_ALREADY_USED, EVENT_EXPIRED, VERIFIED, ALL
# Models
from order.models import Order, OrderItem
# Serializer
from order.serializers import EventUserSerializer, OrderHistoryOrderItemSerializer, OrderItemSerializer, OrderSerializer
from utils.payment import pay_via_stripe
from utils.utils import get_settings
from utils.validators import format_validation_errors

class OrderAPIView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    # Search Filter
    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user).order_by("-created_at")
        # search = self.request.query_params.get("search", None)
        # if search:
        #     queryset = Order.objects.filter(Q(event__icontains=search))
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        return serializer.instance

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
            serializer = self.get_serializer(data=request.data,context={"request": request})
            if serializer.is_valid():                
                ticket_id = request.data.get('ticket_id', None)
                qty = request.data.get('qty', 0)
                # Check if ticket id is not none
                if ticket_id is None:
                    return Response(
                        {
                            SUCCESS: FALSE,
                            ERROR: INVALID_TICKET_ID
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )
                # Check if qty is not 0
                if qty is 0:
                    return Response(
                        {
                            SUCCESS: FALSE,
                            ERROR: INVALID_QTY
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )
                total = 0
                event_ticket = Ticket.objects.get(uuid=ticket_id)
                event_ticket_price = event_ticket.price
                fees = int(get_settings('fees')) if get_settings('fees') else 0
                total += ( int(qty) * event_ticket_price ) + fees
                
                instance = serializer.save(user=self.request.user,total=total,qty=qty)
                # Payment using stripe
                payload = {}
                payload['email'] = request.user.email
                payload['stripe_customer_id'] = request.user.stripe_customer_id
                payload['amount'] = total
                payload['card_token'] = request.data.get('card_token')
                payload['event'] = instance.event.title
                payload['order'] = instance
                
                payment = pay_via_stripe(payload)
                if payment[SUCCESS]:
                    
                    return Response(
                        {
                            SUCCESS: TRUE,
                            MESSAGE: ORDER_CREATED_SUCCESS,
                            DATA: serializer.data,
                        },
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    {
                        SUCCESS: FALSE,
                        ERROR: payment[ERROR]
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                error = format_validation_errors(serializer)
                response = {}
                response[SUCCESS] = FALSE
                response[ERROR] = error
                return Response(response, status=status.HTTP_404_NOT_FOUND)

        except (AttributeError, FileNotFoundError, Exception) as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
            )
        

# My Tickets
class TicketListView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = OrderItemSerializer

    # Search Filter
    def get_queryset(self):
        current_date = datetime.now().date()
        type = self.request.GET.get('type')
        if type is not None:
            queryset = OrderItem.objects.filter(order__user=self.request.user,order__event__date__lte=current_date).order_by("-created_at")
        else:
            queryset = OrderItem.objects.filter(order__user=self.request.user,order__event__date__gte=current_date).order_by("-created_at")
            
        return queryset    

    def get(self, request):
        try:
            queryset = self.get_queryset()
            # page = self.paginate_queryset(queryset)

            # if page is not None:
            #     serializer = self.get_serializer(page, many=True)
            #     return self.get_paginated_response(serializer.data)

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

class OrderInfoAPIView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]    
    serializer_class = OrderSerializer

    def get_order(self, uuid):
        try:
            return Order.objects.filter(uuid=uuid, user=self.request.user).first()
        except:
            return None

    # Info
    def get(self, request, uuid):
        try:
            order = self.get_order(uuid=uuid)
            if order == None:
                return Response(
                    {SUCCESS: FALSE, ERROR: ORDER_NOT_FOUND},
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = self.serializer_class(order, context={"request": request})

            return Response(
                {SUCCESS: TRUE, MESSAGE: ORDER_INFO_SUCCESS, DATA: serializer.data},
                status=status.HTTP_200_OK,
            )

        except (AttributeError, Exception) as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
            )
    
# Get Event Users
class EventUsersAPIView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = EventUserSerializer
    
    def get(self, request, uuid):
        try:            
            try:
                event = Event.objects.get(uuid=uuid)
                favourite_user_ids = FavouriteUser.objects.filter(event_id=event, status=True, user_liked_by_id=request.user.id).values_list("user_liked_id")

                event_user_ids = Order.objects.filter(event_id=event).exclude(user_id=request.user.id).exclude(user_id__in=favourite_user_ids).values_list("user_id").distinct()

                queryset = User.objects.filter(id__in=event_user_ids)

                # Search filters
                gender = request.query_params.get("gender", None)
                min_age = request.query_params.get("min_age",0)
                max_age = request.query_params.get("max_age",0)
                if gender and gender == MALE:
                    queryset = queryset.filter(Q(gender=MALE))
                elif gender and gender == FEMALE:
                    queryset = queryset.filter(Q(gender=FEMALE))
                elif gender and gender == ALL:
                    queryset = queryset
                if min_age and max_age:
                    # Calculate birth date range based on age
                    today = datetime.now().date()
                    birthdate_min = today - timedelta(days=int(min_age) * 365)
                    birthdate_max = today - timedelta(days=(int(max_age) - 1) * 365)
                    queryset = queryset.filter(Q(dob__gte=birthdate_max) & Q(dob__lte=birthdate_min))
                page = self.paginate_queryset(queryset)
                
                # Pagination
                if page is not None:
                    serializer = self.get_serializer(page, many=True, context={'request': request})
                    return self.get_paginated_response(serializer.data)
                                
                serializer = self.get_serializer(queryset, many=True, context={'request': request})
                return Response(
                    {SUCCESS: TRUE, MESSAGE: ORDER_INFO_SUCCESS, DATA: None},
                    status=status.HTTP_200_OK,
                )
            except (AttributeError, Exception) as ex:
                return Response(
                    {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
                )
        except (AttributeError, Exception) as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)}, status=status.HTTP_404_NOT_FOUND
            )

# Verify Order
class VerifyOrderAPIView(generics.GenericAPIView):
    serializer_class = OrderItemSerializer

    def get_order_item(self, uuid):
        return OrderItem.objects.filter(uuid=uuid,order__event__club__user=self.request.user).first()

    def post(self, request, uuid):
        try:
            order_item = self.get_order_item(uuid=uuid)
            if not order_item:
                return Response(
                    {SUCCESS: FALSE,ERROR:TICKET_NOT_FOUND, STATUS:TICKET_INVALID},
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = self.serializer_class(order_item, context={"request": request})
            order = order_item.order

            if order.event.date < datetime.today().date():
                order_item.status = EXPIRED
                order_item.is_scanned = TRUE
                order_item.save()
                return Response(
                    {SUCCESS: FALSE, ERROR: EVENT_HAS_EXPIRED,STATUS:EVENT_EXPIRED},
                    status=status.HTTP_404_NOT_FOUND
                )
            elif order_item.status == EXPIRED:
                order_item.is_scanned = TRUE
                order_item.save()
                return Response(
                    {SUCCESS: FALSE, ERROR: EVENT_HAS_EXPIRED, STATUS:EVENT_EXPIRED},
                    status=status.HTTP_404_NOT_FOUND,
                )
            elif order_item.status == VERIFIED:
                order_item.is_scanned = TRUE
                order_item.save()
                return Response(
                    {SUCCESS: FALSE, ERROR: TICKET_ALREADY_USED, STATUS:TICKET_ALREADY_VERIFIED},
                    status=status.HTTP_404_NOT_FOUND,
                )
            elif order_item.status == NOT_VERIFIED:
                order_item.status = VERIFIED
                order_item.is_scanned = TRUE
                order_item.save()
                return Response(
                    {SUCCESS: TRUE,STATUS:TICKET_VERIFIED},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {SUCCESS: FALSE, ERROR: TICKET_NOT_FOUND, STATUS:TICKET_INVALID},
                    status=status.HTTP_404_NOT_FOUND,
                )

        except Exception as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex),STATUS:TICKET_INVALID}, status=status.HTTP_404_NOT_FOUND
            )
            
class OrderHistoryAPIView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = OrderHistoryOrderItemSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return OrderItem.objects.filter(order__event__club__user=self.request.user,is_scanned=TRUE)

    def get(self, request):
        
        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True,context={"request": request})
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True,context={"request": request})
            return Response(
                {
                    SUCCESS: TRUE,
                    MESSAGE: LIST_FETCHED_SUCCESS,
                    DATA: serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as ex:
            return Response(
                {SUCCESS: FALSE, ERROR: str(ex)},
                status=status.HTTP_404_NOT_FOUND
            )
        
    