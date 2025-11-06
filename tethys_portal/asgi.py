"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

from os import environ
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import re_path
from tethys_portal.optional_dependencies import has_module


def build_application(asgi_app):
    from tethys_portal.urls import websocket_urlpatterns
    from tethys_apps.urls import app_websocket_urls, http_handler_patterns

    websocket_urlpatterns += app_websocket_urls
    if has_module("reactpy_django"):
        from reactpy_django.utils import register_component

        register_component("tethys_apps.base.page_handler.page_component_wrapper")

    application = ProtocolTypeRouter(
        {
            "http": AuthMiddlewareStack(
                URLRouter(
                    [
                        *http_handler_patterns,
                        re_path(r"", asgi_app),
                    ]
                )
            ),
            "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
        }
    )
    return application


environ.setdefault("DJANGO_SETTINGS_MODULE", "tethys_portal.settings")

# This needs to be called before any model imports
asgi_app = get_asgi_application()
application = build_application(asgi_app)
