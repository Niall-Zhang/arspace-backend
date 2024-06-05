from django.contrib import admin
from club.models import Cast, Club, Event, EventCast, EventImage

# Register your models here.
admin.site.register(Cast)
admin.site.register(Club)
admin.site.register(Event)
admin.site.register(EventImage)
admin.site.register(EventCast)
