from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import Feedback
from datetime import timedelta

class Command(BaseCommand):
    help = 'Deletes client feedback older than 30 days'

    def handle(self, *args, **kwargs):
        cutoff_date = timezone.now() - timedelta(days=30)
        old_feedbacks = Feedback.objects.filter(created_at__lt=cutoff_date)
        count = old_feedbacks.count()
        old_feedbacks.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} feedback entries older than 30 days."))
