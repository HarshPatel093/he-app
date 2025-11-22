""" 
Configuration of the 'users' app.

This module defines the UsersConfig class, which initializes 
application-specific behavior upon Django startup. 

The application includes a cleanup function that deletes shift 
records older than 30 days once it is ready.
"""

from django.apps import AppConfig
from django.utils import timezone
from datetime import timedelta


class UsersConfig(AppConfig):
    """ Configure Django application for the 'users' app.

    Attributes: default_auto_field (str): Determines the default primary key type.
    Name (str): The name of the Django application.

    Once Django has finished loading all apps, it executes the ready() method.
    It automatically deletes Shift entries older than 30 days to keep database clean.
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    # This technique deletes shift records older than 30 days using a cutoff date and filtering the Shift model.
    def ready(self):
       
        from django.db.utils import OperationalError
        try:
            from .models import Shift

            # Compute cutoff date (30 days before today)
            cutoff_date = timezone.now().date() - timedelta(days=30)

            # Query shifts older than cutoff
            old_shifts = Shift.objects.filter(date__lt=cutoff_date)
            deleted_count = old_shifts.count()

            # Delete old shift records if any exist
            if deleted_count > 0:
                old_shifts.delete()
                print(f"🗑️ Auto-deleted {deleted_count} shift(s) older than 30 days")

        except OperationalError:
            pass