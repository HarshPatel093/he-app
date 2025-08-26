from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class CreateUser(forms.ModelForm):
    name = forms.CharField(required=True, max_length=100)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Re-enter Password")
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=UserProfile.GENDER_CHOICES)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['email', 'password', 'name']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data
