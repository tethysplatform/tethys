import pytest
import datetime
import uuid
import unittest
from types import SimpleNamespace
from unittest import mock
from django.test import override_settings

from tethys_portal import utilities


class TethysPortalUtilitiesTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_log_user_in_no_user_or_username(self):
        mock_request = mock.MagicMock()
        mock_request.method = "POST"
        mock_request.POST = "login-submit"
        mock_request.user.is_anonymous = True
        mock_request.user.username = "sam"
        mock_request.GET = ""

        with self.assertRaises(ValueError) as context:
            utilities.log_user_in(mock_request)

        self.assertTrue(
            'You must provide either the "user" or the "username" arguments.'
            in str(context.exception)
        )

    @mock.patch("tethys_portal.utilities.redirect")
    @pytest.mark.django_db
    def test_log_user_in_no_user_username_does_not_exist(self, mock_redirect):
        mock_request = mock.MagicMock()
        mock_request.method = "POST"
        mock_request.POST = "login-submit"
        mock_request.user.is_anonymous = True
        mock_request.user.username = "sam"
        mock_request.GET = ""

        utilities.log_user_in(mock_request, username="sam")

        # mock redirect after logged in using next parameter or default to user profile
        mock_redirect.assert_called_once_with("accounts:login")

    @override_settings(MULTIPLE_APP_MODE=True)
    @mock.patch("tethys_portal.utilities.login")
    @mock.patch("tethys_portal.utilities.redirect")
    def test_log_user_in_no_user_exist(self, mock_redirect, mock_authenticate):
        mock_request = mock.MagicMock()
        mock_request.method = "POST"
        mock_request.POST = "login-submit"
        mock_request.user.is_anonymous = True
        mock_request.user.username = "sam"
        mock_request.GET = ""

        # mock authenticate
        mock_user = mock.MagicMock()
        mock_authenticate.return_value = mock_user

        # mock the password has been verified for the user
        mock_user.is_active = True

        utilities.log_user_in(mock_request, user=mock_user)

        # mock redirect after logged in using next parameter or default to user profile
        mock_redirect.assert_called_once_with("app_library")

    @override_settings(MULTIPLE_APP_MODE=False)
    @mock.patch("tethys_portal.utilities.login")
    @mock.patch("tethys_portal.utilities.redirect")
    def test_log_user_in_no_user_exist_single_app_mode(
        self, mock_redirect, mock_authenticate
    ):
        mock_request = mock.MagicMock()
        mock_request.method = "POST"
        mock_request.POST = "login-submit"
        mock_request.user.is_anonymous = True
        mock_request.user.username = "sam"
        mock_request.GET = ""

        # mock authenticate
        mock_user = mock.MagicMock()
        mock_authenticate.return_value = mock_user

        # mock the password has been verified for the user
        mock_user.is_active = True

        utilities.log_user_in(mock_request, user=mock_user)

        # mock redirect after logged in using next parameter or default to user profile
        mock_redirect.assert_called_once_with("/")

    @override_settings(ALLOWED_HOSTS=["test_host.com"])
    @mock.patch("tethys_portal.utilities.login")
    @mock.patch("tethys_portal.utilities.redirect")
    def test_log_user_in_no_user_exist_next(self, mock_redirect, mock_authenticate):
        mock_request = mock.MagicMock()
        mock_request.method = "POST"
        mock_request.POST = "login-submit"
        mock_request.user.is_anonymous = True
        mock_request.user.username = "sam"
        mock_request.GET = {"next": "foo"}

        # mock authenticate
        mock_user = mock.MagicMock()
        mock_authenticate.return_value = mock_user

        mock_user.is_active = True

        utilities.log_user_in(mock_request, user=mock_user)

        mock_redirect.assert_called_once_with("foo")

    @override_settings(MULTIPLE_APP_MODE=False)
    @override_settings(ALLOWED_HOSTS=["test_host.com"])
    @mock.patch("tethys_portal.utilities.login")
    @mock.patch("tethys_portal.utilities.redirect")
    def test_log_user_in_no_user_exist_next_invalid_single_app_mode(
        self, mock_redirect, mock_authenticate
    ):
        mock_request = mock.MagicMock()
        mock_request.method = "POST"
        mock_request.POST = "login-submit"
        mock_request.user.is_anonymous = True
        mock_request.user.username = "sam"
        mock_request.GET = {"next": "http://malicious_site.com/"}

        # mock authenticate
        mock_user = mock.MagicMock()
        mock_authenticate.return_value = mock_user

        # mock the password has been verified for the user
        mock_user.is_active = True

        utilities.log_user_in(mock_request, user=mock_user)

        mock_redirect.assert_called_once_with("/")

    @override_settings(MULTIPLE_APP_MODE=True)
    @override_settings(ALLOWED_HOSTS=["test_host.com"])
    @mock.patch("tethys_portal.utilities.login")
    @mock.patch("tethys_portal.utilities.redirect")
    def test_log_user_in_no_user_exist_next_invalid_multiple_app_mode(
        self, mock_redirect, mock_authenticate
    ):
        mock_request = mock.MagicMock()
        mock_request.method = "POST"
        mock_request.POST = "login-submit"
        mock_request.user.is_anonymous = True
        mock_request.user.username = "sam"
        mock_request.GET = {"next": "http://malicious_site.com/"}

        # mock authenticate
        mock_user = mock.MagicMock()
        mock_authenticate.return_value = mock_user

        # mock the password has been verified for the user
        mock_user.is_active = True

        utilities.log_user_in(mock_request, user=mock_user)

        mock_redirect.assert_called_once_with("app_library")

    def test_json_serializer_datetime(self):
        d = datetime.datetime(2020, 1, 1)
        ret = utilities.json_serializer(d)
        self.assertEqual("2020-01-01T00:00:00", ret)

    def test_json_serializer_uuid(self):
        u = uuid.uuid4()
        ret = utilities.json_serializer(u)
        self.assertEqual(str(u), ret)

    def test_json_serializer_other(self):
        with self.assertRaises(TypeError) as cm:
            utilities.json_serializer(1)

        self.assertEqual(
            'Object of type "int" is not JSON serializable', str(cm.exception)
        )

    @override_settings(ALLOWED_HOSTS=["test_host.com"])
    def test_sanitize_next_url_valid(self):
        test_next_url = utilities.sanitize_next_url("http://test_host.com/")
        self.assertEqual("http://test_host.com/", test_next_url)

    @override_settings(ALLOWED_HOSTS=["test_host.com"])
    def test_sanitize_next_url_invalid(self):
        test_next_url = utilities.sanitize_next_url("http://malicious_site.com/")
        self.assertIsNone(test_next_url)

    @override_settings(ALLOWED_HOSTS=[])
    def test_sanitize_next_url_no_allowed_hosts(self):
        test_next_url = utilities.sanitize_next_url("http://localhost/")
        self.assertEqual("http://localhost/", test_next_url)

    @override_settings(ALLOWED_HOSTS=[])
    def test_sanitize_next_url_no_allowed_hosts_invalid(self):
        test_next_url = utilities.sanitize_next_url("http://malicious_site.com/")
        self.assertIsNone(test_next_url)

    @override_settings(ALLOWED_HOSTS=["test_host.com"])
    def test_sanitize_next_url_absolute_path(self):
        test_next_url = utilities.sanitize_next_url("/absolute-path/")
        self.assertEqual("/absolute-path/", test_next_url)

    @override_settings(ALLOWED_HOSTS=["test_host.com"])
    def test_sanitize_next_url_relative_path(self):
        test_next_url = utilities.sanitize_next_url("relative-path/")
        self.assertEqual("relative-path/", test_next_url)

    def test_is_password_reset_enabled_no_email_config(self):
        # EMAIL_CONFIG attribute missing entirely -> disabled
        fake_settings = SimpleNamespace(ENABLE_PASSWORD_RESET=True)
        with mock.patch("tethys_portal.utilities.settings", fake_settings):
            self.assertFalse(utilities.is_password_reset_enabled())

    def test_is_password_reset_enabled_empty_email_config(self):
        # EMAIL_CONFIG present but empty -> disabled even if reset is enabled
        fake_settings = SimpleNamespace(EMAIL_CONFIG={}, ENABLE_PASSWORD_RESET=True)
        with mock.patch("tethys_portal.utilities.settings", fake_settings):
            self.assertFalse(utilities.is_password_reset_enabled())

    def test_is_password_reset_enabled_setting_unset_defaults_false(self):
        # Email configured but ENABLE_PASSWORD_RESET not set -> disabled by default
        fake_settings = SimpleNamespace(EMAIL_CONFIG={"EMAIL_HOST": "smtp.example.com"})
        with mock.patch("tethys_portal.utilities.settings", fake_settings):
            self.assertFalse(utilities.is_password_reset_enabled())

    def test_is_password_reset_enabled_setting_false(self):
        # Email configured but reset explicitly disabled -> disabled
        fake_settings = SimpleNamespace(
            EMAIL_CONFIG={"EMAIL_HOST": "smtp.example.com"},
            ENABLE_PASSWORD_RESET=False,
        )
        with mock.patch("tethys_portal.utilities.settings", fake_settings):
            self.assertFalse(utilities.is_password_reset_enabled())

    def test_is_password_reset_enabled_setting_true(self):
        # Email configured and reset explicitly enabled -> enabled
        fake_settings = SimpleNamespace(
            EMAIL_CONFIG={"EMAIL_HOST": "smtp.example.com"},
            ENABLE_PASSWORD_RESET=True,
        )
        with mock.patch("tethys_portal.utilities.settings", fake_settings):
            self.assertTrue(utilities.is_password_reset_enabled())

    def test_is_password_reset_enabled_returns_bool(self):
        # A truthy non-bool setting value is coerced to a real bool
        fake_settings = SimpleNamespace(
            EMAIL_CONFIG={"EMAIL_HOST": "smtp.example.com"},
            ENABLE_PASSWORD_RESET="yes",
        )
        with mock.patch("tethys_portal.utilities.settings", fake_settings):
            result = utilities.is_password_reset_enabled()
        self.assertIs(result, True)

    def test_is_password_reset_enabled_legacy_email_host_user(self):
        # Backwards compatibility: email configured via top-level EMAIL_HOST_USER
        fake_settings = SimpleNamespace(
            EMAIL_HOST_USER="apikey",
            EMAIL_HOST="smtp.sendgrid.net",
            ENABLE_PASSWORD_RESET=True,
        )
        with mock.patch("tethys_portal.utilities.settings", fake_settings):
            self.assertTrue(utilities.is_password_reset_enabled())

    def test_is_password_reset_enabled_legacy_email_host(self):
        # Backwards compatibility: email configured via a top-level, non-local EMAIL_HOST
        fake_settings = SimpleNamespace(
            EMAIL_HOST="smtp.sendgrid.net",
            ENABLE_PASSWORD_RESET=True,
        )
        with mock.patch("tethys_portal.utilities.settings", fake_settings):
            self.assertTrue(utilities.is_password_reset_enabled())

    def test_is_password_reset_enabled_legacy_localhost_not_configured(self):
        # A top-level localhost relay with no auth is indistinguishable from the
        # Django defaults, so it is treated as not configured
        fake_settings = SimpleNamespace(
            EMAIL_HOST="localhost",
            EMAIL_HOST_USER="",
            ENABLE_PASSWORD_RESET=True,
        )
        with mock.patch("tethys_portal.utilities.settings", fake_settings):
            self.assertFalse(utilities.is_password_reset_enabled())

    def test_is_email_configured_via_email_config(self):
        fake_settings = SimpleNamespace(EMAIL_CONFIG={"EMAIL_HOST": "smtp.example.com"})
        with mock.patch("tethys_portal.utilities.settings", fake_settings):
            self.assertTrue(utilities.is_email_configured())

    def test_is_email_configured_not_configured(self):
        fake_settings = SimpleNamespace(EMAIL_CONFIG={}, EMAIL_HOST="localhost")
        with mock.patch("tethys_portal.utilities.settings", fake_settings):
            self.assertFalse(utilities.is_email_configured())
