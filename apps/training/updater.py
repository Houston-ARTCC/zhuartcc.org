from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone

from .models import TrainingRequest, TrainingSession
from .views import post_ctrs


# Schedules a task to update event scores every hour.
def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(clean_up_training, 'cron', day_of_week='sat')
    scheduler.start()


def clean_up_training():
    remove_stale_requests()
    submit_ctrs_records()


def remove_stale_requests():
    TrainingRequest.objects.filter(end__lte=timezone.now()).delete()


def submit_ctrs_records():
    sessions = TrainingSession.objects.filter(ctrs_id__isnull=True).filter(student__main_role='HC').exclude(level=7)

    for session in sessions:
        post_ctrs(session)
