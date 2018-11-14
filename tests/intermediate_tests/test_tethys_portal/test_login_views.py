from django.test import TestCase
from django.test import Client
from django.contrib.auth import get_user_model
from captcha.models import CaptchaStore


class TethysLoginViewTests(TestCase):

    def setUp(self):
        self.username = 'testuser'
        self.password = '12345'
        User = get_user_model()
        self.user = User.objects.create_user(username=self.username,
                                             password=self.password,
                                             email='foo_exist@aquaveo.com')
        self.client = Client()
        CaptchaStore.generate_key()
        self.hashkey = CaptchaStore.objects.all()[0].hashkey
        self.response = CaptchaStore.objects.all()[0].response
        self.login_data = {'username': self.username,
                           'password': self.password,
                           'captcha_0': self.hashkey,
                           'captcha_1': self.response,
                           'login-submit': "This key must exist!!!"}

    def tearDown(self):
        self.user.delete()

    def test_login_view(self):
        response = self.client.post('/accounts/login/',
                                    self.login_data,
                                    follow=True)

        self.assertFalse(response.context['user'].is_anonymous())
        self.assertTrue(response.context['user'].is_authenticated())
        self.assertTrue(response.context['user'].username, self.username)
        self.assertEqual(response.status_code, 200)
