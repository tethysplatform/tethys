from django.urls import reverse, resolve
from tethys_sdk.testing import TethysTestCase
from django.test import override_settings


class TestUrls(TethysTestCase):
    def set_up(self):
        pass

    def tear_down(self):
        pass

    def test_urls(self):
        # This executes the code at the module level
        url = reverse("app_library")
        resolver = resolve(url)
        self.assertEqual("/apps/", url)
        self.assertEqual("library", resolver.func.__name__)
        self.assertEqual("tethys_apps.views", resolver.func.__module__)

        url = reverse("send_beta_feedback")
        resolver = resolve(url)
        self.assertEqual("/apps/send-beta-feedback/", url)
        self.assertEqual("send_beta_feedback_email", resolver.func.__name__)
        self.assertEqual("tethys_apps.views", resolver.func.__module__)

        url = reverse("test_app:home")
        resolver = resolve(url)
        self.assertEqual("/apps/test-app/", url)
        self.assertEqual("home", resolver.func.__name__)
        self.assertEqual("tethysapp.test_app.controllers", resolver.func.__module__)

        url = reverse("test_extension:home", kwargs={"var1": "foo", "var2": "bar"})
        resolver = resolve(url)
        self.assertEqual("/extensions/test-extension/foo/bar/", url)
        self.assertEqual("home", resolver.func.__name__)
        self.assertEqual(
            "tethysext.test_extension.controllers", resolver.func.__module__
        )

        url = reverse("test_extension:home", args=["foo", "bar"])
        resolver = resolve(url)
        self.assertEqual("/extensions/test-extension/foo/bar/", url)
        self.assertEqual("home", resolver.func.__name__)
        self.assertEqual(
            "tethysext.test_extension.controllers", resolver.func.__module__
        )


# probably need to test for extensions manually
@override_settings(PREFIX_URL="test/prefix")
class TestUrlsWithPrefix(TethysTestCase):
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
        self.reload_urlconf()
        pass

    @override_settings(PREFIX_URL="/")
    def tearDown(self):
        self.reload_urlconf()
        pass

    def test_urls(self):
        # This executes the code at the module level
        url = reverse("app_library")
        resolver = resolve(url)
        self.assertEqual("/test/prefix/apps/", url)
        self.assertEqual("library", resolver.func.__name__)
        self.assertEqual("tethys_apps.views", resolver.func.__module__)

        url = reverse("send_beta_feedback")
        resolver = resolve(url)
        self.assertEqual("/test/prefix/apps/send-beta-feedback/", url)
        self.assertEqual("send_beta_feedback_email", resolver.func.__name__)
        self.assertEqual("tethys_apps.views", resolver.func.__module__)

        url = reverse("test_app:home")
        resolver = resolve(url)
        self.assertEqual("/test/prefix/apps/test-app/", url)
        self.assertEqual("home", resolver.func.__name__)
        self.assertEqual("tethysapp.test_app.controllers", resolver.func.__module__)

        url = reverse("test_extension:home", kwargs={"var1": "foo", "var2": "bar"})
        resolver = resolve(url)
        self.assertEqual("/test/prefix/extensions/test-extension/foo/bar/", url)
        self.assertEqual("home", resolver.func.__name__)
        self.assertEqual(
            "tethysext.test_extension.controllers", resolver.func.__module__
        )

        url = reverse("test_extension:home", args=["foo", "bar"])
        resolver = resolve(url)
        self.assertEqual("/test/prefix/extensions/test-extension/foo/bar/", url)
        self.assertEqual("home", resolver.func.__name__)
        self.assertEqual(
            "tethysext.test_extension.controllers", resolver.func.__module__
        )


@override_settings(MULTIPLE_APP_MODE=False)
class TestUrlsWithStandaloneApp(TethysTestCase):
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
        self.reload_urlconf()
        pass

    @override_settings(MULTIPLE_APP_MODE=True)
    def tearDown(self):
        self.reload_urlconf()
        pass

    def test_urls(self):
        # This executes the code at the module level
        url = reverse("home")
        resolver = resolve(url)
        self.assertEqual("/", url)
        self.assertEqual("RedirectView", resolver.func.__name__)
        self.assertEqual("/test-app/", resolver.func.view_initkwargs["url"])

        url = reverse("app_library")
        resolver = resolve(url)
        self.assertEqual("/apps/", url)
        self.assertEqual("RedirectView", resolver.func.__name__)
        self.assertEqual("/test-app/", resolver.func.view_initkwargs["url"])

        url = reverse("send_beta_feedback")
        resolver = resolve(url)
        self.assertEqual("/send-beta-feedback/", url)
        self.assertEqual("send_beta_feedback_email", resolver.func.__name__)
        self.assertEqual("tethys_apps.views", resolver.func.__module__)

        url = reverse("test_app:home")
        resolver = resolve(url)
        self.assertEqual("/test-app/", url)
        self.assertEqual("home", resolver.func.__name__)
        self.assertEqual("tethysapp.test_app.controllers", resolver.func.__module__)

        url = reverse("test_extension:home", kwargs={"var1": "foo", "var2": "bar"})
        resolver = resolve(url)
        self.assertEqual("/extensions/test-extension/foo/bar/", url)
        self.assertEqual("home", resolver.func.__name__)
        self.assertEqual(
            "tethysext.test_extension.controllers", resolver.func.__module__
        )

        url = reverse("test_extension:home", args=["foo", "bar"])
        resolver = resolve(url)
        self.assertEqual("/extensions/test-extension/foo/bar/", url)
        self.assertEqual("home", resolver.func.__name__)
        self.assertEqual(
            "tethysext.test_extension.controllers", resolver.func.__module__
        )
