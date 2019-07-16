from django.urls import reverse, resolve
from tethys_sdk.testing import TethysTestCase


class TestTethysServicesUrls(TethysTestCase):

    def set_up(self):
        pass

    def tear_down(self):
        pass

    def test_service_urls_wps_services(self):
        url = reverse('services:wps_service', kwargs={'service': 'foo'})
        resolver = resolve(url)
        self.assertEqual('/developer/services/wps/foo/', url)
        self.assertEqual('wps_service', resolver.func.__name__)
        self.assertEqual('tethys_services.views', resolver.func.__module__)

    def test_service_urls_wps_process(self):
        url = reverse('services:wps_process', kwargs={'service': 'foo', 'identifier': 'bar'})
        resolver = resolve(url)
        self.assertEqual('/developer/services/wps/foo/process/bar/', url)
        self.assertEqual('wps_process', resolver.func.__name__)
        self.assertEqual('tethys_services.views', resolver.func.__module__)

    def test_urlpatterns_datasethome(self):
        url = reverse('services:datasets_home')
        resolver = resolve(url)
        self.assertEqual('/developer/services/datasets/', url)
        self.assertEqual('datasets_home', resolver.func.__name__)
        self.assertEqual('tethys_services.views', resolver.func.__module__)

    def test_urlpatterns_wpshome(self):
        url = reverse('services:wps_home')
        resolver = resolve(url)
        self.assertEqual('/developer/services/wps/', url)
        self.assertEqual('wps_home', resolver.func.__name__)
        self.assertEqual('tethys_services.views', resolver.func.__module__)
