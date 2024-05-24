from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nxtbn.core'

    def ready(self):
        import nxtbn.core.signals  # noqa
