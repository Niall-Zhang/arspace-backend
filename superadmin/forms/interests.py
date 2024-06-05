from django import forms
from base.models import Interest

class InterestForm(forms.ModelForm):
    class Meta:
        model = Interest
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 50})
        }