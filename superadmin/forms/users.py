from django import forms
from authentication.models import User
from django.contrib.auth.hashers import make_password

# User Form
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email','password','profile_picture']
        widgets = {             
            'email': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 30}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'})
        }

    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'minlength': 6}))

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data["password"])
        if commit:
            user.is_active = True
            user.is_staff = True
            user.email_verified = True
            user.save()
        return user