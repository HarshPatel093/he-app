from django.apps import AppConfig
from django.utils import timezone
from datetime import timedelta


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
       
        from django.db.utils import OperationalError
        try:
            from .models import Shift

            cutoff_date = timezone.now().date() - timedelta(days=30)

            old_shifts = Shift.objects.filter(date__lt=cutoff_date)
            deleted_count = old_shifts.count()

            if deleted_count > 0:
                old_shifts.delete()
                print(f"🗑️ Auto-deleted {deleted_count} shift(s) older than 30 days")

        except OperationalError:
            pass