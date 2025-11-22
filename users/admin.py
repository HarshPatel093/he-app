"""
Custom Django admin settings for the UserProfile model.

This module customizes the appearance of UserProfile objects in the Django Admin interface
by specifying viewable columns, searchable fields, and display helpers 
(e.g., showing the user's email and date joined).).
"""

from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserProfile entries.

    list_display:
        Controls which columns appear in the list view.
        - name: The display name of the user.
        - email: A helper function that retrieves the email from User.
        - role: Admin/Staff/Client role.
        - date_of_birth: DOB stored in UserProfile.
        - date_joined: Derived field from the linked User model.

    search_fields:
        Allows searching by name, email, or role.

    list_filter:
        Adds a filter sidebar for filtering by role.
    """
    # Columns that appear in the admin list view
    list_display = ('name', 'email', 'role', 'date_of_birth', 'date_joined')

    # Fields that can be searched through the admin search bar
    search_fields = ('name', 'user__email', 'role')

    # Filters displayed in the right-hand sidebar
    list_filter = ('role',)

    def email(self, obj):
        """
        Returns the email address of the associated User.

        Args:
            obj (UserProfile): The user profile instance.

        Returns:
            str: The email address stored in the linked User model.
        """
        return obj.user.email  

    def date_joined(self, obj):
        """
        Returns the formatted date when the User account was created.

        Args:
            obj (UserProfile): The user profile instance.

        Returns:
            str: Formatted datetime string (YYYY-MM-DD HH:MM).
        """
        return obj.user.date_joined.strftime("%Y-%m-%d %H:%M") 