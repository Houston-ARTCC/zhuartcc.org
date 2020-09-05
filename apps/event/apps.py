from django.apps import AppConfig


class EventConfig(AppConfig):
    name = 'apps.event'

    # Overrides ready method to include scheduler for event score update
    def ready(self):
        from .updater import start
        start()
