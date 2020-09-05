from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = 'apps.api'

    # Overrides ready method to include scheduler for api updater
    def ready(self):
        from .updater import start
        start()
