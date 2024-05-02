from unittest import TestCase, mock
from django.test import override_settings
from tethys_portal import context_processors


class TestStaticDependency(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @override_settings(MULTIPLE_APP_MODE=False)
    @mock.patch("tethys_portal.context_processors.messages")
    def test_check_single_app_mode_single(self, mock_messages):
        mock_request = mock.MagicMock()
        single_app_mode, configured_single_app = (
            context_processors.check_single_app_mode(mock_request)
        )

        self.assertTrue(single_app_mode)
        self.assertTrue(configured_single_app.name == "Test App")
        mock_messages.assert_not_called()

    @override_settings(MULTIPLE_APP_MODE=False)
    @mock.patch("tethys_portal.context_processors.messages")
    @mock.patch("tethys_portal.context_processors.get_configured_standalone_app")
    def test_check_single_app_mode_single_no_app(
        self, mock_get_configured_standalone_app, mock_messages
    ):
        mock_request = mock.MagicMock()
        mock_get_configured_standalone_app.return_value = None
        single_app_mode, configured_single_app = (
            context_processors.check_single_app_mode(mock_request)
        )

        self.assertTrue(single_app_mode)
        self.assertIsNone(configured_single_app)
        mock_messages.warning.assert_called_with(
            mock_request,
            "MULTIPLE_APP_MODE is disabled but there is no configured tethys application.",
        )

    def test_check_single_app_mode_multiple(self):
        mock_request = mock.MagicMock()
        single_app_mode, configured_single_app = (
            context_processors.check_single_app_mode(mock_request)
        )

        self.assertFalse(single_app_mode)
        self.assertIsNone(configured_single_app)
