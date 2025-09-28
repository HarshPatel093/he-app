from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from .models import UserProfile, Shift  

class CreateUser(forms.ModelForm):
    name = forms.CharField(required=True, max_length=100)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Re-enter Password")
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['email', 'password', 'name']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data

class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ['staff', 'clients', 'date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'staff': forms.Select(attrs={'class': 'select2'}),        
            'clients': forms.SelectMultiple(attrs={'class': 'select2'}) 
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['staff'].label = "Assign Staff Member"
        self.fields['clients'].label = "Allocate Clients"
        self.fields['date'].label = "Shift Date"
        self.fields['start_time'].label = "Start Time"
        self.fields['end_time'].label = "End Time"