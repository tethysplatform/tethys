from django.test import Client
from django.contrib.auth import get_user_model
from django.test import TestCase


class TethysAppsLibraryTests(TestCase):

    def setUp(self):
        from tethys_apps.harvester import SingletonHarvester
        harvester = SingletonHarvester()
        harvester.harvest()

        self.username = 'testuser'
        self.password = '12345'
        User = get_user_model()
        self.user = User.objects.create_user(username=self.username,
                                             password=self.password,
                                             email='foo_exist@aquaveo.com')
        self.client = Client()

    def tearDown(self):
        self.user.delete()

    def test_apps_homepage(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get('/apps/')

        self.assertFalse(response.context['user'].is_anonymous())
        self.assertTrue(response.context['user'].is_authenticated())
        self.assertTrue(response.context['user'].username, self.username)
        self.assertEqual(response.status_code, 200)

        # Test some bytes/strings should appear on /apps/ page
        self.assertIn(b"Apps Library", response.content)
        self.assertIn(self.username.encode(), response.content)
