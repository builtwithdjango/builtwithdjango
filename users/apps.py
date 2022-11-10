from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "users"

    def ready(self):
        print(self)
        from . import tasks
