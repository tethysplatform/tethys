import pytest
import sys
from importlib import reload, import_module
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.urls import reverse, clear_url_caches
from django.test import override_settings
from django.conf import settings

from tethys_apps.base.testing.testing import TethysTestCase


class TethysPortalApiTests(TethysTestCase):
    def reload_urlconf(self, urlconf=None):
        clear_url_caches()
        if urlconf is None:
            urlconf = settings.ROOT_URLCONF
        if urlconf in sys.modules:
            reload(sys.modules[urlconf])
        else:
            import_module(urlconf)

    def set_up(self):
        self.user = User.objects.create_user(username="foo")
        self.user.save()
        pass

    @override_settings(PREFIX_URL="/")
    def tearDown(self):
        self.user.delete()
        self.reload_urlconf()
        pass

    def test_get_csrf_not_authenticated(self):
        """Test get_csrf API endpoint not authenticated."""
        response = self.client.get(reverse("api:get_csrf"))
        self.assertEqual(response.status_code, 401)

    def test_get_csrf_authenticated(self):
        """Test get_csrf API endpoint authenticated."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("api:get_csrf"))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, HttpResponse)
        self.assertIn("X-CSRFToken", response.headers)

    def test_get_session_not_authenticated(self):
        """Test get_session API endpoint not authenticated."""
        response = self.client.get(reverse("api:get_session"))
        self.assertEqual(response.status_code, 401)

    def test_get_session_authenticated(self):
        """Test get_session API endpoint authenticated."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("api:get_session"))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        # self.assertIn('Set-Cookie', response.headers)
        json = response.json()
        self.assertIn("isAuthenticated", json)
        self.assertTrue(json["isAuthenticated"])

    def test_get_whoami_not_authenticated(self):
        """Test get_whoami API endpoint not authenticated."""
        response = self.client.get(reverse("api:get_whoami"))
        self.assertEqual(response.status_code, 401)

    def test_get_whoami_authenticated(self):
        """Test get_whoami API endpoint authenticated."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("api:get_whoami"))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        json = response.json()
        self.assertIn("username", json)
        self.assertIn("firstName", json)
        self.assertIn("lastName", json)
        self.assertIn("email", json)
        self.assertIn("isAuthenticated", json)
        self.assertIn("isStaff", json)
        self.assertEqual("foo", json["username"])
        self.assertTrue(json["isAuthenticated"])

    @override_settings(MULTIPLE_APP_MODE=True)
    @override_settings(STATIC_URL="/static")
    @override_settings(PREFIX_URL="/")
    @override_settings(LOGIN_URL="/accounts/login/")
    @pytest.mark.django_db
    def test_get_app_valid_id(self):
        self.reload_urlconf()

        """Test get_app API endpoint with valid app id."""
        response = self.client.get(reverse("api:get_app", kwargs={"app": "test-app"}))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        json = response.json()
        self.assertIn("title", json)
        self.assertIn("description", json)
        self.assertIn("tags", json)
        self.assertIn("package", json)
        self.assertIn("urlNamespace", json)
        self.assertIn("color", json)
        self.assertIn("icon", json)
        self.assertIn("exitUrl", json)
        self.assertIn("rootUrl", json)
        self.assertIn("settingsUrl", json)
        self.assertEqual("Test App", json["title"])
        self.assertEqual(
            "Place a brief description of your app here.", json["description"]
        )
        self.assertEqual("", json["tags"])
        self.assertEqual("test_app", json["package"])
        self.assertEqual("test_app", json["urlNamespace"])
        self.assertEqual("#2c3e50", json["color"])
        self.assertEqual("/static/test_app/images/icon.gif", json["icon"])
        self.assertEqual("/apps/", json["exitUrl"])
        self.assertEqual("/apps/test-app/", json["rootUrl"])
        self.assertRegex(
            json["settingsUrl"],
            r"^/admin/tethys_apps/tethysapp/[0-9]+/change/$",
        )

    @override_settings(MULTIPLE_APP_MODE=True)
    @override_settings(PREFIX_URL="test/prefix")
    @override_settings(LOGIN_URL="/test/prefix/test/login/")
    @override_settings(STATIC_URL="/test/prefix/test/static/")
    @pytest.mark.django_db
    def test_get_app_valid_id_with_prefix(self):
        self.reload_urlconf()

        """Test get_app API endpoint with valid app id."""
        response = self.client.get(reverse("api:get_app", kwargs={"app": "test-app"}))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        json = response.json()
        self.assertIn("title", json)
        self.assertIn("description", json)
        self.assertIn("tags", json)
        self.assertIn("package", json)
        self.assertIn("urlNamespace", json)
        self.assertIn("color", json)
        self.assertIn("icon", json)
        self.assertIn("exitUrl", json)
        self.assertIn("rootUrl", json)
        self.assertIn("settingsUrl", json)
        self.assertEqual("Test App", json["title"])
        self.assertEqual(
            "Place a brief description of your app here.", json["description"]
        )
        self.assertEqual("", json["tags"])
        self.assertEqual("test_app", json["package"])
        self.assertEqual("test_app", json["urlNamespace"])
        self.assertEqual("#2c3e50", json["color"])
        self.assertEqual(
            "/test/prefix/test/static/test_app/images/icon.gif", json["icon"]
        )
        self.assertEqual("/test/prefix/apps/", json["exitUrl"])
        self.assertEqual("/test/prefix/apps/test-app/", json["rootUrl"])
        self.assertRegex(
            json["settingsUrl"],
            r"^/test/prefix/admin/tethys_apps/tethysapp/[0-9]+/change/$",
        )

    @override_settings(MULTIPLE_APP_MODE=True)
    @override_settings(STATIC_URL="/static")
    @override_settings(PREFIX_URL="/")
    @override_settings(LOGIN_URL="/accounts/login/")
    @pytest.mark.django_db
    def test_get_app_authenticated(self):
        self.client.force_login(self.user)
        self.reload_urlconf()

        """Test get_app API endpoint with valid app id."""
        response = self.client.get(reverse("api:get_app", kwargs={"app": "test-app"}))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        json = response.json()
        self.assertIn("title", json)
        self.assertIn("description", json)
        self.assertIn("tags", json)
        self.assertIn("package", json)
        self.assertIn("urlNamespace", json)
        self.assertIn("color", json)
        self.assertIn("icon", json)
        self.assertIn("exitUrl", json)
        self.assertIn("rootUrl", json)
        self.assertIn("settingsUrl", json)
        self.assertEqual("Test App", json["title"])
        self.assertEqual(
            "Place a brief description of your app here.", json["description"]
        )
        self.assertEqual("", json["tags"])
        self.assertEqual("test_app", json["package"])
        self.assertEqual("test_app", json["urlNamespace"])
        self.assertEqual("#2c3e50", json["color"])
        self.assertEqual("/static/test_app/images/icon.gif", json["icon"])
        self.assertEqual("/apps/", json["exitUrl"])
        self.assertEqual("/apps/test-app/", json["rootUrl"])
        self.assertRegex(
            json["settingsUrl"],
            r"^/admin/tethys_apps/tethysapp/[0-9]+/change/$",
        )
        self.assertDictEqual(
            {
                "JSON_setting_default_value_required": {
                    "type": "JSON",
                    "value": {"Test": "JSON test String"},
                },
                "Secret_Test_required": {"type": "SECRET", "value": None},
                "default_name": {"type": "STRING", "value": None},
                "enable_feature": {"type": "BOOLEAN", "value": None},
            },
            json["customSettings"],
        )

    def test_get_app_invalid_id(self):
        """Test get_app API endpoint with invalid app id."""
        response = self.client.get(reverse("api:get_app", kwargs={"app": "foo-bar"}))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        json = response.json()
        self.assertIn("error", json)
        self.assertEqual('Could not find app "foo-bar".', json["error"])
