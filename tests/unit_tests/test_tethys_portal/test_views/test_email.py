from importlib import reload

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
