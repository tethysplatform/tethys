from django.test import TestCase
from captcha.models import CaptchaStore
from tethys_portal.forms import LoginForm


class TethysPortalFormsTests(TestCase):

    def setUp(self):
        self.captcha = CaptchaStore.objects.get(hashkey=CaptchaStore.generate_key())
        self.login_data = {'username': 'admin', 'password': 'pass', 'captcha': self.captcha}
        self.register_data = {'username': 'user1', 'email': 'foo@aquaveo.com',
                              'password1': 'abc123', 'password2': 'abc123'}

    def tearDown(self):
        pass

    def test_LoginForm(self):
        login_form = LoginForm(data=self.login_data)
        self.assertTrue(login_form.is_valid())

    def test_RegisterForm(self):
        pass
        # register_form = RegisterForm(data=self.register_data)
        # self.assertTrue(register_form.is_valid())
