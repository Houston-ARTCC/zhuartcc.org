from datetime import timedelta
from apscheduler.schedulers.background import BackgroundScheduler

from django.utils import timezone

from .models import Event


# Schedules a task to update event scores every hour.
def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_event_scores, 'interval', hours=1)
    scheduler.start()


def update_event_scores():
    past_events = Event.objects.filter(end__lte=timezone.now()).filter(scored=False)
    for event in past_events:
        if not event.scored:
            event.calculate_scores()
