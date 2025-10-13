from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from datetime import timedelta
from users.models import Feedback

def delete_old_feedback():
    cutoff = timezone.now() - timedelta(days=30)
    old_feedback = Feedback.objects.filter(created_at__lt=cutoff)
    count = old_feedback.count()
    old_feedback.delete()
    print(f"[{timezone.now()}] Deleted {count} feedback entries older than 30 days.")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(delete_old_feedback, 'interval', days=1)
    scheduler.start()