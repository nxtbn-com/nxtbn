from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nxtbn.users'

    def ready(self):
        import nxtbn.users.signals  # noqa
