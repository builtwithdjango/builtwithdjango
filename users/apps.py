import logging

from django.apps import AppConfig

logger = logging.getLogger(__file__)


class UsersConfig(AppConfig):
    name = "users"

    def ready(self):
        logger.info(self)
        from . import tasks
