"""
Django management command to delete feedback entries older than 30 days.

It helps keep the database cleanby removing outdated client feedback entries.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import Feedback
from datetime import timedelta

class Command(BaseCommand):
    help = 'Deletes client feedback older than 30 days'

    def handle(self, *args, **kwargs):
        # Determine the cutoff timestamp (30 days before current time)
        cutoff_date = timezone.now() - timedelta(days=30)

        # Query all feedback entries older than the cutoff timestamp
        old_feedbacks = Feedback.objects.filter(created_at__lt=cutoff_date)
        
        # Count them for logging
        count = old_feedbacks.count()

        # Delete records
        old_feedbacks.delete()

        # Output a success message in console
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} feedback entries older than 30 days."))
