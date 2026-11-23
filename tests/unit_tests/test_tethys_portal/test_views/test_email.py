from importlib import reload
from unittest import mock

from django.test import override_settings

import tethys_portal.views.email as email
from tethys_apps.base.testing import testing


class TethysPortalViewsEmailTest(testing.TethysTestCase):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    @override_settings(
        DEFAULT_FROM_EMAIL="<noreply@email.com>",
        EMAIL_FROM="John Smith",
        EMAIL_HOST_USER="",
    )
    def test_TethysPasswordResetView_with_angle_brackets(self):
        reload(email)
        self.assertEqual(
            email.TethysPasswordResetView.from_email, "John Smith <noreply@email.com>"
        )

    @override_settings(
        DEFAULT_FROM_EMAIL="noreply@email.com",
        EMAIL_FROM="John Smith",
        EMAIL_HOST_USER="",
    )
    def test_TethysPasswordResetView_without_angle_brackets(self):
        reload(email)
        self.assertEqual(
            email.TethysPasswordResetView.from_email, "John Smith <noreply@email.com>"
        )

    @override_settings(
        DEFAULT_FROM_EMAIL="foo@email.com",
        EMAIL_FROM="John Smith",
        EMAIL_HOST_USER="host@email.com",
    )
    def test_TethysPasswordResetView_with_email_host_user(self):
        reload(email)
        self.assertEqual(
            email.TethysPasswordResetView.from_email, "John Smith <host@email.com>"
        )

    @override_settings(
        DEFAULT_FROM_EMAIL="noreply@email.com", EMAIL_FROM="", EMAIL_HOST_USER=""
    )
    def test_TethysPasswordResetView_without_from_email(self):
        reload(email)
        self.assertEqual(
            email.TethysPasswordResetView.from_email, "<noreply@email.com>"
        )

    @mock.patch("tethys_portal.views.email.redirect")
    @mock.patch(
        "tethys_portal.views.email.is_password_reset_enabled", return_value=False
    )
    def test_password_reset_view_redirects_when_disabled(
        self, mock_enabled, mock_redirect
    ):
        mock_request = mock.MagicMock()
        response = email.TethysPasswordResetView.as_view()(mock_request)
        mock_redirect.assert_called_once_with("accounts:login")
        self.assertEqual(response, mock_redirect.return_value)

    @mock.patch("tethys_portal.views.email.redirect")
    @mock.patch(
        "tethys_portal.views.email.is_password_reset_enabled", return_value=False
    )
    def test_password_reset_confirm_view_redirects_when_disabled(
        self, mock_enabled, mock_redirect
    ):
        mock_request = mock.MagicMock()
        response = email.TethysPasswordResetConfirmView.as_view()(mock_request)
        mock_redirect.assert_called_once_with("accounts:login")
        self.assertEqual(response, mock_redirect.return_value)

    @mock.patch("django.contrib.auth.views.PasswordResetView.dispatch")
    @mock.patch("tethys_portal.views.email.redirect")
    @mock.patch(
        "tethys_portal.views.email.is_password_reset_enabled", return_value=True
    )
    def test_password_reset_view_proceeds_when_enabled(
        self, mock_enabled, mock_redirect, mock_dispatch
    ):
        mock_request = mock.MagicMock()
        response = email.TethysPasswordResetView.as_view()(mock_request)
        mock_redirect.assert_not_called()
        mock_dispatch.assert_called_once()
        self.assertEqual(response, mock_dispatch.return_value)
