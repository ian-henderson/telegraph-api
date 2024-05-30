"""
ASGI config for telegraph project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
import os

from chat.routing import websocket_urlpatterns
from .middleware import JwtAuthMiddleware


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            JwtAuthMiddleware(URLRouter(websocket_urlpatterns))
        ),
    }
)
