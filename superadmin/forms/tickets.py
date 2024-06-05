from django import forms
from club.models import Ticket

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['name', 'price',"units"]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 50}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'maxlength': 30}),
            'units': forms.NumberInput(attrs={'class': 'form-control', 'maxlength': 30}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.left = instance.units
        if commit:
            instance.save()
        return instance