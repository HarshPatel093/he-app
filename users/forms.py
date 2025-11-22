""" 
Forms for the Holiday Explorers System.

This module defines the form classes for adding new users and creating shifts.
Each form has validation and display options.
"""

from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from .models import UserProfile, Shift  

class CreateUser(forms.ModelForm):
    """ This form allows admin to create a new user and related user profile.

    This form collects the following:
        - Name: User's full name
        - Email:  Login using email address
        - Password: User Input
        - Confirm Password:  Ensures the password confirmation matches
        - Date of Birth:  User's date of birth
        - role: User position (admin, staff, or client)

    The form uses custom validation to guarantee that passwords match.
    """
    name = forms.CharField(required=True, max_length=100)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Re-enter Password")
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)

    # The meta setting specifies which Django model fields this form corresponds to.
    class Meta:
        model = User
        fields = ['email', 'password', 'name']

    # Validates form-wide fields
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        # Checks whether password and confirm password matches, if not raised an error
        # Returns cleaned_data with validated form input
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data

class ShiftForm(forms.ModelForm):
    """ Form for creating or updating shift allocations.

    The form collects the following:
        - Staff: Responsible for the shift 
        - Clients:  Multiple clients were assigned to the shift
        - date:  Date of the shift
        - Shift start and end times

    Custom widget styling is used to improve UI (e.g., <input type='date'>).
    """
    # Meta configuration for defining shiftform
    class Meta:

        # Shift model to map the form fields to
        model = Shift

        # fields exposed in the form
        fields = ['staff', 'clients', 'date', 'start_time', 'end_time']

        # Customize HTML input type and add CSS classes (select2)
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'staff': forms.Select(attrs={'class': 'select2'}),        
            'clients': forms.SelectMultiple(attrs={'class': 'select2'}) 
        }
    
    def __init__(self, *args, **kwargs):
        """
        Initialize form and customize field labels.

        Args:
            *args: Variable positional arguments
            **kwargs: Variable keyword arguments

        Returns:
            None
        """
        super().__init__(*args, **kwargs)
        self.fields['staff'].label = "Assign Staff Member"
        self.fields['clients'].label = "Allocate Clients"
        self.fields['date'].label = "Shift Date"
        self.fields['start_time'].label = "Start Time"
        self.fields['end_time'].label = "End Time"