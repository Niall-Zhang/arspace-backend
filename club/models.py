from django.db import models
from django.contrib.gis.db import models
from authentication.models import User
import uuid

# Cast
class Cast(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(null=True)
    image = models.ImageField(null=True, upload_to="casts")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = "casts"

    def __str__(self):
        return self.name

# Club
class Club(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    title = models.CharField(max_length=50, unique=True, db_index=True)
    contact_no = models.CharField(max_length=30, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = "clubs"

    def __str__(self):
        return self.title

# Event
class Event(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(null=True)   
    date = models.DateField(null=True,blank=True)
    time = models.TimeField(null=True,blank=True)
    latitude = models.CharField(null=True, max_length=30)
    longitude = models.CharField(null=True, max_length=30)
    point = models.PointField(null=True)
    location = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = "events"    


# Event Images
class EventImage(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    image = models.ImageField(null=True, upload_to="events")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = "event_images"
        indexes = [models.Index(fields=["uuid"])]

# Tickets
class Ticket(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=50, unique=True, db_index=True, blank=True)    
    price = models.FloatField(null=True)
    currency = models.CharField(max_length=10, default="$", null=True, blank=True)
    left = models.IntegerField(null=True)
    units = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = "tickets"
        indexes = [models.Index(fields=["uuid"])]

    def __str__(self):
        return self.name

# Event Tickets
class EventTicket(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE,null=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE,null=True)
    class Meta:
        db_table = "event_tickets"
        indexes = [models.Index(fields=["uuid"])]
    
# Event Casts
class EventCast(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    cast = models.ForeignKey(Cast, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = "event_casts"
        indexes = [models.Index(fields=["uuid"])]


# Liked Event
class EventLike(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = "event_like"
        indexes = [models.Index(fields=["uuid"])]