from apscheduler.schedulers.background import BackgroundScheduler

from django.utils import timezone

from .models import TrainingRequest


# Schedules a task to update event scores every hour.
def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(remove_stale_requests, 'interval', hours=1)
    scheduler.start()


def remove_stale_requests():
    TrainingRequest.objects.filter(end__lte=timezone.now()).delete()
