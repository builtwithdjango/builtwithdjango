from django.apps import AppConfig

from builtwithdjango.utils import get_builtwithdjango_logger

logger = get_builtwithdjango_logger(__name__)


class UsersConfig(AppConfig):
    name = "users"

    def ready(self):
        from . import tasks
