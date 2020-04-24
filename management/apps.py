from django.apps import AppConfig


class ManagementConfig(AppConfig):
    name = 'management'

    def ready(self):
        import management.signals
