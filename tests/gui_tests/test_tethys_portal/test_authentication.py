from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from django.contrib.auth.models import User


class AuthenticationTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()

        cls.user_pass = "userpass"
        cls.user = User.objects.create_user("user", "user@example.com", cls.user_pass)
        cls.super_user_pass = "superpass"
        cls.super_user = User.objects.create_superuser(
            "super_user", "super@example.com", cls.super_user_pass
        )

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_login(self):
        self.selenium.get("%s%s" % (self.live_server_url, "/accounts/login/"))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys(self.user.username)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(self.user_pass)
        self.selenium.find_element_by_name("login-submit").click()
