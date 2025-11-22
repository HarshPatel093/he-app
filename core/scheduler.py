from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from datetime import timedelta
from users.models import Feedback

def delete_old_feedback():
    """
    Deletes feedback entries older than 30 days.

    This function is used to delete feedback records whose `created_at` timestamp 
    is more than 30 days old.
    The function calculates a cutoff datetime and deletes all matching rows.

    Returns:
        None (as it performs database cleanup)
    """
    # Calculate the cutoff created time: any feedback older than this will be removed
    cutoff = timezone.now() - timedelta(days=30)
    old_feedback = Feedback.objects.filter(created_at__lt=cutoff)
    count = old_feedback.count()
    old_feedback.delete()
    print(f"[{timezone.now()}] Deleted {count} feedback entries older than 30 days.")

def start_scheduler():
    """
    This function starts an APScheduler BackgroundScheduler and
    schedules the `delete_old_feedback` task to run once every 24 hours.

    Returns:
        None
    """
    # Create a new background scheduler instance
    scheduler = BackgroundScheduler()
    scheduler.add_job(delete_old_feedback, 'interval', days=1)
    scheduler.start()