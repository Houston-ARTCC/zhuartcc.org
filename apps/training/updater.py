from apscheduler.schedulers.background import BackgroundScheduler

from django.utils import timezone

from .models import TrainingRequest, TrainingSession


# Schedules a task to update event scores every hour.
from .views import post_ctrs


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(remove_stale_requests, 'interval', hours=1)
    scheduler.add_job(submit_ctrs_records, 'cron', day_of_week='sat')
    scheduler.start()


def remove_stale_requests():
    TrainingRequest.objects.filter(end__lte=timezone.now()).delete()


def submit_ctrs_records():
    sessions = TrainingSession.objects.filter(ctrs_id__isnull=True).filter(student__main_role='HC').exclude(level=7)

    for session in sessions:
        post_ctrs(session)
