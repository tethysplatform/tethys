from importlib import reload
from unittest import mock

from django.test import TestCase, override_settings
from django.urls import reverse

import tethys_portal.forms as tp_forms


class TethysPortalAccountsCaptchaRenderingTest(TestCase):
    def tearDown(self):
        reload(tp_forms)

    def render_login(self):
        with mock.patch("tethys_portal.views.accounts.LoginForm", tp_forms.LoginForm):
            return self.client.get(reverse("accounts:login"))

    def render_register(self):
        with mock.patch(
            "tethys_portal.views.accounts.RegisterForm", tp_forms.RegisterForm
        ):
            return self.client.get(reverse("accounts:register"))

    @override_settings(
        ENABLE_CAPTCHA=True, RECAPTCHA_PRIVATE_KEY="", RECAPTCHA_PUBLIC_KEY=""
    )
    def test_login_page_renders_captcha_when_enabled(self):
        reload(tp_forms)
        self.assertIn("captcha", tp_forms.LoginForm().fields)

        response = self.render_login()

        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'name="captcha_1"')

    @override_settings(ENABLE_CAPTCHA=False)
    def test_login_page_omits_captcha_when_disabled(self):
        reload(tp_forms)
        self.assertNotIn("captcha", tp_forms.LoginForm().fields)

        response = self.render_login()

        self.assertEqual(200, response.status_code)
        self.assertNotContains(response, 'name="captcha_1"')

    @override_settings(
        ENABLE_CAPTCHA=True,
        ENABLE_OPEN_SIGNUP=True,
        RECAPTCHA_PRIVATE_KEY="",
        RECAPTCHA_PUBLIC_KEY="",
    )
    def test_register_page_renders_captcha_when_enabled(self):
        reload(tp_forms)
        self.assertIn("captcha", tp_forms.RegisterForm().fields)

        response = self.render_register()

        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'name="captcha_1"')

    @override_settings(ENABLE_CAPTCHA=False, ENABLE_OPEN_SIGNUP=True)
    def test_register_page_omits_captcha_when_disabled(self):
        reload(tp_forms)
        self.assertNotIn("captcha", tp_forms.RegisterForm().fields)

        response = self.render_register()

        self.assertEqual(200, response.status_code)
        self.assertNotContains(response, 'name="captcha_1"')
