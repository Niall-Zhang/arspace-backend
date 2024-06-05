from django import forms
from club.models import Cast,Event, EventCast, EventImage, EventTicket, Ticket
from django.contrib.gis.geos import Point
# Date Input
class DateInput(forms.DateInput):
    input_type = 'date'

# Time Input
class TimeInput(forms.TimeInput):
    input_type = 'time'

# Mutiple File Input
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


# Mutiple File Field
class MultipleFileField(forms.FileField):
    def __init__(self, *args, custom_class=None, **kwargs):
        widget = MultipleFileInput(attrs={'class': custom_class}) if custom_class else MultipleFileInput()
        kwargs.setdefault("widget", widget)
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

# Event Form
class EventForm(forms.ModelForm):
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    casts = forms.ModelMultipleChoiceField(queryset=Cast.objects.all(), widget=forms.CheckboxSelectMultiple)
    tickets = forms.ModelMultipleChoiceField(queryset=Ticket.objects.all(), widget=forms.CheckboxSelectMultiple)
    images = MultipleFileField(custom_class="form-control",required=False)
    class Meta:
        model = Event
        fields = ['club', 'title', 'description',"date","time","latitude","longitude","location"]
        widgets = {
            'club': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 30}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 100}),
            'date':  DateInput(attrs={'class':'form-control'}),
            'time':  TimeInput(attrs={'class':'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['casts'].initial = self.instance.eventcast_set.values_list('cast', flat=True)    
            self.fields['tickets'].initial = self.instance.eventticket_set.values_list('ticket', flat=True)    

    def save(self, commit=True):
        event = super().save(commit=False)
        longitude = self.cleaned_data.get("longitude")
        latitude = self.cleaned_data.get("latitude")
        if longitude and latitude:
            event.point = Point(float(longitude), float(latitude))
        if commit:
            if event.pk:
                event.save()
                EventCast.objects.filter(event=event).delete()
                EventTicket.objects.filter(event=event).delete()
            else:                
                event.save()
            self.save_m2m()
            for cast in self.cleaned_data['casts']:
                EventCast.objects.create(event=event, cast=cast)   
            for ticket in self.cleaned_data['tickets']:
                EventTicket.objects.create(event=event, ticket=ticket)        
        return event

# Ticket Form
class TicketForm(forms.ModelForm):
    class Meta:
        model = EventTicket
        fields = ['event','ticket']