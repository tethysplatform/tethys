from unittest import TestCase, mock
from django.test import override_settings
from tethys_portal import context_processors


class TestTethysPortalContext(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @override_settings(MULTIPLE_APP_MODE=True)
    def test_context_processors_multiple_app_mode(self):
        mock_user = mock.MagicMock(is_authenticated=True, is_active=True)
        mock_request = mock.MagicMock(user=mock_user)
        context = context_processors.tethys_portal_context(mock_request)

        expected_context = {
            "has_analytical": True,
            "has_cookieconsent": True,
            "has_terms": True,
            "has_mfa": True,
            "has_gravatar": True,
            "has_session_security": True,
            "has_oauth2_provider": True,
            "show_app_library_button": True,
            "single_app_mode": False,
            "configured_single_app": None,
            "idp_backends": {}.keys(),
        }
        self.assertDictEqual(context, expected_context)

    @override_settings(MULTIPLE_APP_MODE=True)
    def test_context_processors_multiple_app_mode_no_request_user(self):
        mock_request = mock.MagicMock()
        del mock_request.user
        assert not hasattr(mock_request, "user")
        context = context_processors.tethys_portal_context(mock_request)

        expected_context = {
            "has_analytical": True,
            "has_cookieconsent": True,
            "has_terms": False,
            "has_mfa": True,
            "has_gravatar": True,
            "has_session_security": True,
            "has_oauth2_provider": True,
            "show_app_library_button": False,
            "single_app_mode": False,
            "configured_single_app": None,
            "idp_backends": {}.keys(),
        }
        self.assertDictEqual(context, expected_context)

    @override_settings(MULTIPLE_APP_MODE=False)
    @mock.patch("tethys_portal.context_processors.messages")
    @mock.patch("tethys_portal.context_processors.get_configured_standalone_app")
    def test_context_processors_single_app_mode(
        self, mock_get_configured_standalone_app, mock_messages
    ):
        mock_user = mock.MagicMock(is_authenticated=True, is_active=True)
        mock_request = mock.MagicMock(user=mock_user)
        mock_get_configured_standalone_app.return_value = None
        context = context_processors.tethys_portal_context(mock_request)

        expected_context = {
            "has_analytical": True,
            "has_cookieconsent": True,
            "has_terms": True,
            "has_mfa": True,
            "has_gravatar": True,
            "has_session_security": True,
            "has_oauth2_provider": True,
            "show_app_library_button": False,
            "single_app_mode": True,
            "configured_single_app": None,
            "idp_backends": {}.keys(),
        }
        self.assertDictEqual(context, expected_context)
        mock_messages.warning.assert_called_with(
            mock_request,
            "MULTIPLE_APP_MODE is disabled but there is no Tethys application installed.",
        )
