from django.db import models
import uuid
from authentication.models import User
from club.models import Event, EventTicket, Ticket

# Orders
class Order(models.Model):
    PAYMENT_STATUSES = (
        ('pending', 'pending'),
        ('completed', 'completed'),
        ('failed', 'failed'),
        ('refunded', 'refunded'),
    )
    GATEWAYS = (
        ('stripe', 'stripe'),
    )
    TICKET_TYPE = (
        ('free', 'free'),
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    qty = models.IntegerField(null=True,blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUSES,default='completed', null=True)
    type = models.CharField(max_length=15, choices=TICKET_TYPE, default=None, null=True)
    gateway = models.CharField(max_length=15, choices=GATEWAYS,default='stripe')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = "orders"
        indexes = [models.Index(fields=["uuid"])]


# Order Items
class OrderItem(models.Model):
    STATUSES = (
        ('verified', 'verified'),
        ('not_verified', 'not_verified'),
        ('expired', 'expired'),
    )
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUSES,default='not_verified')
    is_scanned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = "order_items"
        indexes = [models.Index(fields=["uuid"])]