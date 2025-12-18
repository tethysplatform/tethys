from unittest import TestCase, mock
from django.test import override_settings
from tethys_portal import context_processors


class TestTethysPortalContext(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @staticmethod
    def has_module_side_effect(module_name):
        modules = {
            "analytical": False,
            "cookie_consent": False,
            "termsandconditions": False,
            "mfa": True,
            "django_gravatar": True,
            "session_security": True,
            "oauth2_provider": True,
        }
        return modules.get(module_name, False)

    @staticmethod
    def has_terms_side_effect(module_name):
        modules = {
            "analytical": False,
            "cookie_consent": False,
            "termsandconditions": True,  # Module installed
            "mfa": True,
            "django_gravatar": True,
            "session_security": True,
            "oauth2_provider": True,
        }
        return modules.get(module_name, False)

    @mock.patch("tethys_portal.context_processors.has_module")
    @override_settings(MULTIPLE_APP_MODE=True)
    def test_context_processors_multiple_app_mode(self, mock_has_module):
        mock_user = mock.MagicMock(is_authenticated=True, is_active=True)
        mock_request = mock.MagicMock(user=mock_user)
        mock_has_module.side_effect = (
            self.has_terms_side_effect
        )  # Terms and Conditions module installed
        context = context_processors.tethys_portal_context(mock_request)

        expected_context = {
            "has_analytical": False,
            "has_cookieconsent": False,
            "has_terms": True,  # enabled b/c terms module installed and user present
            "has_mfa": True,
            "has_gravatar": True,
            "has_session_security": True,
            "has_oauth2_provider": True,
            "show_app_library_button": True,
            "single_app_mode": False,
            "configured_single_app": None,
            "idp_backends": {}.keys(),
            "debug_mode": False,
        }
        self.assertDictEqual(context, expected_context)

    @override_settings(MULTIPLE_APP_MODE=True)
    @mock.patch("tethys_portal.context_processors.has_module")
    def test_context_processors_multiple_app_mode_no_request_user(
        self, mock_has_module
    ):
        mock_request = mock.MagicMock()
        del mock_request.user
        assert not hasattr(mock_request, "user")

        mock_has_module.side_effect = (
            self.has_terms_side_effect
        )  # Terms and Conditions module installed
        context = context_processors.tethys_portal_context(mock_request)

        expected_context = {
            "has_analytical": False,
            "has_cookieconsent": False,
            "has_terms": False,  # disabled still because no user in request
            "has_mfa": True,
            "has_gravatar": True,
            "has_session_security": True,
            "has_oauth2_provider": True,
            "show_app_library_button": False,
            "single_app_mode": False,
            "configured_single_app": None,
            "idp_backends": {}.keys(),
            "debug_mode": False,
        }
        self.assertDictEqual(context, expected_context)

    @mock.patch("tethys_portal.context_processors.has_module")
    @mock.patch("tethys_portal.context_processors.messages")
    @mock.patch("tethys_portal.context_processors.get_configured_standalone_app")
    @override_settings(MULTIPLE_APP_MODE=False)
    def test_context_processors_single_app_mode(
        self, mock_get_configured_standalone_app, mock_messages, mock_has_module
    ):
        mock_user = mock.MagicMock(is_authenticated=True, is_active=True)
        mock_request = mock.MagicMock(user=mock_user)
        mock_get_configured_standalone_app.return_value = None
        mock_has_module.side_effect = self.has_module_side_effect
        context = context_processors.tethys_portal_context(mock_request)

        expected_context = {
            "has_analytical": False,
            "has_cookieconsent": False,
            "has_terms": False,
            "has_mfa": True,
            "has_gravatar": True,
            "has_session_security": True,
            "has_oauth2_provider": True,
            "show_app_library_button": False,
            "single_app_mode": True,
            "configured_single_app": None,
            "idp_backends": {}.keys(),
            "debug_mode": False,
        }
        self.assertDictEqual(context, expected_context)
        mock_messages.warning.assert_called_with(
            mock_request,
            "MULTIPLE_APP_MODE is disabled but there is no Tethys application installed.",
        )

    @override_settings(DEBUG=True)
    @mock.patch("tethys_portal.context_processors.has_module")
    def test_context_processors_debug_mode_true(self, mock_has_module):
        mock_has_module.side_effect = self.has_module_side_effect

        mock_request = mock.MagicMock()
        del mock_request.user
        assert not hasattr(mock_request, "user")
        context = context_processors.tethys_portal_context(mock_request)

        expected_context = {
            "has_analytical": False,
            "has_cookieconsent": False,
            "has_terms": False,
            "has_mfa": True,
            "has_gravatar": True,
            "has_session_security": True,
            "has_oauth2_provider": True,
            "show_app_library_button": False,
            "single_app_mode": False,
            "configured_single_app": None,
            "idp_backends": {}.keys(),
            "debug_mode": True,
        }
        self.assertDictEqual(context, expected_context)

    @mock.patch(
        "tethys_portal.context_processors.get_configured_standalone_app",
        return_value=None,
    )
    @mock.patch("tethys_portal.context_processors.has_module", return_value=False)
    @override_settings(DEBUG=True)
    @override_settings(MULTIPLE_APP_MODE=False)
    def test_context_processors_no_optional_modules(self, _, __):
        mock_user = mock.MagicMock(is_authenticated=True, is_active=True)
        mock_request = mock.MagicMock(user=mock_user)
        context = context_processors.tethys_portal_context(mock_request)

        expected_context = {
            "has_analytical": False,
            "has_cookieconsent": False,
            "has_terms": False,
            "has_mfa": False,
            "has_gravatar": False,
            "has_session_security": False,
            "has_oauth2_provider": False,
            "show_app_library_button": False,
            "single_app_mode": True,
            "configured_single_app": None,
            "idp_backends": {}.keys(),
            "debug_mode": True,
        }
        self.assertDictEqual(context, expected_context)
