from tethys_sdk.testing import TethysTestCase

import tethys_portal.asgi as asgi
from django.test import override_settings
from django.urls import URLPattern


class TestAsgiApplication(TethysTestCase):
    def set_up(self):
        pass

    def tear_down(self):
        pass

    def test_application(self):
        application = asgi.application
        self.assertIn("websocket", application.application_mapping)
        self.assertIn("http", application.application_mapping)


@override_settings(PREFIX_URL="test/prefix", MULTIPLE_APP_MODE=True)
class TestAsgiApplicationWithURLPrefix(TethysTestCase):
    import sys
    from importlib import reload, import_module
    from django.conf import settings
    from django.urls import clear_url_caches

    @classmethod
    def reload_urlconf(self, urlconf=None):
        self.clear_url_caches()
        if urlconf is None:
            urlconf = self.settings.ROOT_URLCONF
        if urlconf in self.sys.modules:
            self.reload(self.sys.modules["tethys_apps.urls"])
            self.reload(self.sys.modules[urlconf])
        else:
            self.import_module(urlconf)

    def set_up(self):
        self.reload_urlconf("tethys_apps.urls")
        self.reload_urlconf("tethys_portal.asgi")
        pass

    @override_settings(PREFIX_URL="/")
    def tearDown(self):
        self.reload_urlconf("tethys_apps.urls")
        pass

    def test_websocket_path(self):
        expected_path = r"^test/prefix/apps/test-app/test-app-ws/ws/$"

        # Get the URLRouter for "websocket" from the application
        asgi_app = asgi.application.application_mapping["websocket"]

        # Get the URLRouter from the AuthMiddlewareStack
        url_router = asgi_app.inner.inner.inner
        # Check if the expected websocket path is in the URLRouter
        self.assertTrue(
            any(
                isinstance(url_pattern, URLPattern)
                and url_pattern.pattern.regex.pattern == expected_path
                for url_pattern in url_router.routes
            )
        )

    def test_handlers_path(self):
        expected_path = r"^test/prefix/apps/test-app/"

        # Get the URLRouter for "http" from the application
        asgi_app = asgi.application.application_mapping["http"]

        # Get the URLRouter from the AuthMiddlewareStack
        url_router = asgi_app.inner.inner.inner
        # Check if the expected http path is in the URLRouter
        self.assertTrue(
            any(
                isinstance(url_pattern, URLPattern)
                and url_pattern.pattern._regex == expected_path
                for url_pattern in url_router.routes
            )
        )
