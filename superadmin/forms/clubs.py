from django import forms
from club.models import Club

class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['user','title', 'contact_no']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 50}),
            'contact_no': forms.NumberInput(attrs={'class': 'form-control', 'maxlength': 30}),
        }

    def clean_contact_no(self):
        contact_no = self.cleaned_data.get('contact_no')
        if not contact_no.isnumeric():
            raise forms.ValidationError("Contact number must contain only digits.")
        return contact_no