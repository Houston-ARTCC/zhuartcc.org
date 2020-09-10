from django.apps import AppConfig


class TrainingConfig(AppConfig):
    name = 'apps.training'

    # Overrides ready method to include scheduler for removing stale training requests
    def ready(self):
        from .updater import start
        start()
