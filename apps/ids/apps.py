from django.apps import AppConfig


class IdsConfig(AppConfig):
    name = 'apps.ids'

    def ready(self):
        from . import signals
        from .updater import start
        start()
