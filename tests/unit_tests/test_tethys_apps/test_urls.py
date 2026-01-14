from django.urls import reverse, resolve
from tethys_portal import urls
from tethys_sdk.testing import TethysTestCase
from django.test import override_settings
from django.urls.exceptions import NoReverseMatch
from unittest import mock
from django.views.generic.base import RedirectView


@override_settings(MULTIPLE_APP_MODE=True)
class TestUrls(TethysTestCase):
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

    @override_settings(MULTIPLE_APP_MODE=True)
    def test_urls(self):
        # This executes the code at the module level
        url = reverse("app_library")
        resolver = resolve(url)
        self.assertEqual("/apps/", url)
        self.assertEqual("tethys_apps.views.library", resolver._func_path)

        url = reverse("send_beta_feedback")
        resolver = resolve(url)
        self.assertEqual("/apps/send-beta-feedback/", url)
        self.assertEqual(
            "tethys_apps.views.send_beta_feedback_email", resolver._func_path
        )

        url = reverse("test_app:home")
        resolver = resolve(url)
        self.assertEqual("/apps/test-app/", url)
        self.assertEqual("tethysapp.test_app.controllers.home", resolver._func_path)

        url = reverse("test_extension:home", kwargs={"var1": "foo", "var2": "bar"})
        resolver = resolve(url)
        self.assertEqual("/extensions/test-extension/foo/bar/", url)
        self.assertEqual(
            "tethysext.test_extension.controllers.home", resolver._func_path
        )

        url = reverse("test_extension:home", args=["foo", "bar"])
        resolver = resolve(url)
        self.assertEqual("/extensions/test-extension/foo/bar/", url)
        self.assertEqual(
            "tethysext.test_extension.controllers.home", resolver._func_path
        )

        # ensure app urls are at the end
        self.assertEqual(
            urls.urlpatterns[-2].urlconf_module.__name__, "tethys_apps.urls"
        )

    @mock.patch("django.urls.include")
    @mock.patch("tethys_portal.optional_dependencies.has_module")
    def test_reactpy_django_urls(self, mock_has_module, mock_include):
        mock_has_module.return_value = True
        from tethys_portal import urls
        from importlib import reload

        reload(urls)
        mock_include.assert_any_call("reactpy_django.http.urls")


# probably need to test for extensions manually
@override_settings(MULTIPLE_APP_MODE=True)
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
        self.assertEqual("tethys_apps.views.library", resolver._func_path)

        url = reverse("send_beta_feedback")
        resolver = resolve(url)
        self.assertEqual("/test/prefix/apps/send-beta-feedback/", url)
        self.assertEqual(
            "tethys_apps.views.send_beta_feedback_email", resolver._func_path
        )

        url = reverse("test_app:home")
        resolver = resolve(url)
        self.assertEqual("/test/prefix/apps/test-app/", url)
        self.assertEqual("tethysapp.test_app.controllers.home", resolver._func_path)

        url = reverse("test_extension:home", kwargs={"var1": "foo", "var2": "bar"})
        resolver = resolve(url)
        self.assertEqual("/test/prefix/extensions/test-extension/foo/bar/", url)
        self.assertEqual(
            "tethysext.test_extension.controllers.home", resolver._func_path
        )

        url = reverse("test_extension:home", args=["foo", "bar"])
        resolver = resolve(url)
        self.assertEqual("/test/prefix/extensions/test-extension/foo/bar/", url)
        self.assertEqual(
            "tethysext.test_extension.controllers.home", resolver._func_path
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
        with self.assertRaises(NoReverseMatch):
            reverse("home")
            reverse("app_library")

        url = reverse("send_beta_feedback")
        resolver = resolve(url)
        self.assertEqual("/send-beta-feedback/", url)
        self.assertEqual("send_beta_feedback_email", resolver.func.__name__)
        self.assertEqual("tethys_apps.views", resolver.func.__module__)

        url = reverse("test_app:home")
        resolver = resolve(url)
        self.assertEqual("/", url)
        self.assertEqual("home", resolver.func.__name__)
        self.assertEqual("tethysapp.test_app.controllers", resolver.func.__module__)

        url = reverse("test_extension:home", kwargs={"var1": "foo", "var2": "bar"})
        resolver = resolve(url)
        self.assertEqual("/extensions/foo/bar/", url)
        self.assertEqual("home", resolver.func.__name__)
        self.assertEqual(
            "tethysext.test_extension.controllers", resolver.func.__module__
        )

        # ensure app urls are at the end
        self.assertEqual(
            urls.urlpatterns[-2].urlconf_module.__name__, "tethys_apps.urls"
        )


@override_settings(MULTIPLE_APP_MODE=False)
class TestUrlsWithStandaloneAppNoApp(TethysTestCase):
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

    @mock.patch("tethys_apps.utilities.get_configured_standalone_app")
    def set_up(self, mock_get_configured_standalone_app):
        mock_get_configured_standalone_app.return_value = []
        self.reload_urlconf()
        pass

    @override_settings(MULTIPLE_APP_MODE=True)
    def tearDown(self):
        self.reload_urlconf()
        pass

    def test_urls(self):
        # This executes the code at the module level
        with self.assertRaises(NoReverseMatch):
            reverse("app_library")

        url = reverse("home")
        resolver = resolve(url)
        self.assertEqual("/", url)
        self.assertEqual(resolver.func.view_class, RedirectView)
        self.assertEqual("user:profile", resolver.func.view_initkwargs["pattern_name"])

        url = reverse("send_beta_feedback")
        resolver = resolve(url)
        self.assertEqual("/send-beta-feedback/", url)
        self.assertEqual("send_beta_feedback_email", resolver.func.__name__)
        self.assertEqual("tethys_apps.views", resolver.func.__module__)

        url = reverse("test_app:home")
        resolver = resolve(url)
        self.assertEqual("/", url)
        self.assertEqual(resolver.func.view_class, RedirectView)
        self.assertEqual("user:profile", resolver.func.view_initkwargs["pattern_name"])

        url = reverse("test_extension:home", kwargs={"var1": "foo", "var2": "bar"})
        resolver = resolve(url)
        self.assertEqual("/extensions/foo/bar/", url)
        self.assertEqual("home", resolver.func.__name__)
        self.assertEqual(
            "tethysext.test_extension.controllers", resolver.func.__module__
        )
