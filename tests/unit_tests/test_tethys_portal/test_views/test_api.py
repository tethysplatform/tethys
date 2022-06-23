from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.urls import reverse

from tethys_apps.base.testing.testing import TethysTestCase


class TethysPortalApiTests(TethysTestCase):

    def set_up(self):
        self.user = User.objects.create_user(username='foo')
        self.user.save()

    def tear_down(self):
        self.user.delete()

    def test_get_csrf_not_authenticated(self):
        """Test get_csrf API endpoint not authenticated."""
        response = self.client.get(reverse('api:get_csrf'))
        self.assertEqual(response.status_code, 401)

    def test_get_csrf_authenticated(self):
        """Test get_csrf API endpoint authenticated."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('api:get_csrf'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, HttpResponse)
        self.assertIn('X-CSRFToken', response.headers)

    def test_get_session_not_authenticated(self):
        """Test get_session API endpoint not authenticated."""
        response = self.client.get(reverse('api:get_session'))
        self.assertEqual(response.status_code, 401)

    def test_get_session_authenticated(self):
        """Test get_session API endpoint authenticated."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('api:get_session'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        # self.assertIn('Set-Cookie', response.headers)
        json = response.json()
        self.assertIn('isAuthenticated', json)
        self.assertTrue(json['isAuthenticated'])

    def test_get_whoami_not_authenticated(self):
        """Test get_whoami API endpoint not authenticated."""
        response = self.client.get(reverse('api:get_whoami'))
        self.assertEqual(response.status_code, 401)

    def test_get_whoami_authenticated(self):
        """Test get_whoami API endpoint authenticated."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('api:get_whoami'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        json = response.json()
        self.assertIn('username', json)
        self.assertIn('firstName', json)
        self.assertIn('lastName', json)
        self.assertIn('email', json)
        self.assertIn('isAuthenticated', json)
        self.assertIn('isStaff', json)
        self.assertEqual('foo', json['username'])
        self.assertTrue(json['isAuthenticated'])

    def test_get_app_valid_id(self):
        """Test get_app API endpoint with valid app id."""
        response = self.client.get(reverse('api:get_app', kwargs={'app': 'test-app'}))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        json = response.json()
        self.assertIn('title', json)
        self.assertIn('description', json)
        self.assertIn('tags', json)
        self.assertIn('package', json)
        self.assertIn('urlNamespace', json)
        self.assertIn('color', json)
        self.assertIn('icon', json)
        self.assertIn('exitUrl', json)
        self.assertIn('rootUrl', json)
        self.assertIn('settingsUrl', json)
        self.assertEqual('Test App', json['title'])
        self.assertEqual('Place a brief description of your app here.', json['description'])
        self.assertEqual('', json['tags'])
        self.assertEqual('test_app', json['package'])
        self.assertEqual('test_app', json['urlNamespace'])
        self.assertEqual('#2c3e50', json['color'])
        self.assertEqual('/static/test_app/images/icon.gif', json['icon'])
        self.assertEqual('/apps/', json['exitUrl'])
        self.assertEqual('/apps/test-app/', json['rootUrl'])
        self.assertRegex(json['settingsUrl'], r'^/admin/tethys_apps/tethysapp/[0-9]+/change/$')

    def test_get_app_invalid_id(self):
        """Test get_app API endpoint with invalid app id."""
        response = self.client.get(reverse('api:get_app', kwargs={'app': 'foo-bar'}))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        json = response.json()
        self.assertIn('error', json)
        self.assertEqual('Could not find app "foo-bar".', json['error'])
