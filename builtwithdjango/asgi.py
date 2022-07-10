"""
ASGI config for builtwithdjango project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application
from turbo.consumers import TurboStreamsConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")


application = ProtocolTypeRouter({"http": get_asgi_application(), "websocket": TurboStreamsConsumer.as_asgi()})
