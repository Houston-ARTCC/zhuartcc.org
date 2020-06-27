from django.apps import AppConfig


class UserConfig(AppConfig):
    name = 'apps.user'

    # Overrides ready method to include scheduler for roster update
    def ready(self):
        from .updater import update_scheduler
        update_scheduler()
