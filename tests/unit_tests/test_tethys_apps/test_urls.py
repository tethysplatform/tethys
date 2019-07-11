from django.urls import reverse, resolve
from tethys_sdk.testing import TethysTestCase


class TestUrls(TethysTestCase):

    def set_up(self):
        pass

    def tear_down(self):
        pass

    def test_urls(self):
        # This executes the code at the module level
        url = reverse('app_library')
        resolver = resolve(url)
        self.assertEqual('/apps/', url)
        self.assertEqual('library', resolver.func.__name__)
        self.assertEqual('tethys_apps.views', resolver.func.__module__)

        url = reverse('send_beta_feedback')
        resolver = resolve(url)
        self.assertEqual('/apps/send-beta-feedback/', url)
        self.assertEqual('send_beta_feedback_email', resolver.func.__name__)
        self.assertEqual('tethys_apps.views', resolver.func.__module__)

        url = reverse('test_app:home')
        resolver = resolve(url)
        self.assertEqual('/apps/test-app/', url)
        self.assertEqual('home', resolver.func.__name__)
        self.assertEqual('tethysapp.test_app.controllers', resolver.func.__module__)

        url = reverse('test_extension:home', kwargs={'var1': 'foo', 'var2': 'bar'})
        resolver = resolve(url)
        self.assertEqual('/extensions/test-extension/foo/bar/', url)
        self.assertEqual('home', resolver.func.__name__)
        self.assertEqual('tethysext.test_extension.controllers', resolver.func.__module__)

        url = reverse('test_extension:home', args=['foo', 'bar'])
        resolver = resolve(url)
        self.assertEqual('/extensions/test-extension/foo/bar/', url)
        self.assertEqual('home', resolver.func.__name__)
        self.assertEqual('tethysext.test_extension.controllers', resolver.func.__module__)
