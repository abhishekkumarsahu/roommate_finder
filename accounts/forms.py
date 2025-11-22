from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class SignupForm(UserCreationForm):
    aadhaar_number = forms.CharField(max_length=20, required=False)
    aadhaar_document = forms.FileField(required=False)

    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'phone', 'aadhaar_number', 'aadhaar_document', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'phone', 'aadhaar_number', 'aadhaar_document', 'latitude', 'longitude']
