from django.urls import reverse, resolve
from tethys_sdk.testing import TethysTestCase
from django.test.utils import override_settings


class TestTethysServicesUrls(TethysTestCase):
    def set_up(self):
        pass

    def tear_down(self):
        pass

    def test_service_urls_wps_services(self):
        url = reverse("services:wps_service", kwargs={"service": "foo"})
        resolver = resolve(url)
        self.assertEqual("/developer/services/wps/foo/", url)
        self.assertEqual("tethys_services.views.wps_service", resolver._func_path)

    def test_service_urls_wps_process(self):
        url = reverse(
            "services:wps_process", kwargs={"service": "foo", "identifier": "bar"}
        )
        resolver = resolve(url)
        self.assertEqual("/developer/services/wps/foo/process/bar/", url)
        self.assertEqual("tethys_services.views.wps_process", resolver._func_path)

    def test_urlpatterns_datasethome(self):
        url = reverse("services:datasets_home")
        resolver = resolve(url)
        self.assertEqual("/developer/services/datasets/", url)
        self.assertEqual("tethys_services.views.datasets_home", resolver._func_path)

    def test_urlpatterns_wpshome(self):
        url = reverse("services:wps_home")
        resolver = resolve(url)
        self.assertEqual("/developer/services/wps/", url)
        self.assertEqual("tethys_services.views.wps_home", resolver._func_path)


@override_settings(PREFIX_URL="test/prefix")
class TestTethysServicesUrlsWithPrefix(TethysTestCase):
    import sys
    from importlib import reload, import_module
    from django.conf import settings
    from django.urls import clear_url_caches

    @classmethod
    def reload_urlconf(self, urlconf=None):
        self.clear_url_caches()
        if urlconf is None:
            urlconf = self.settings.ROOT_URLCONF
        if urlconf in self.sys.modules:
            self.reload(self.sys.modules[urlconf])
        else:
            self.import_module(urlconf)

    def set_up(self):
        self.reload_urlconf()
        pass

    @override_settings(PREFIX_URL="/")
    def tearDown(self):
        self.reload_urlconf()
        pass

    def test_service_urls_wps_services(self):
        url = reverse("services:wps_service", kwargs={"service": "foo"})
        resolver = resolve(url)
        self.assertEqual("/test/prefix/developer/services/wps/foo/", url)
        self.assertEqual("tethys_services.views.wps_service", resolver._func_path)

    def test_service_urls_wps_process(self):
        url = reverse(
            "services:wps_process", kwargs={"service": "foo", "identifier": "bar"}
        )
        resolver = resolve(url)
        self.assertEqual("/test/prefix/developer/services/wps/foo/process/bar/", url)
        self.assertEqual("tethys_services.views.wps_process", resolver._func_path)

    def test_urlpatterns_datasethome(self):
        url = reverse("services:datasets_home")
        resolver = resolve(url)
        self.assertEqual("/test/prefix/developer/services/datasets/", url)
        self.assertEqual("tethys_services.views.datasets_home", resolver._func_path)

    def test_urlpatterns_wpshome(self):
        url = reverse("services:wps_home")
        resolver = resolve(url)
        self.assertEqual("/test/prefix/developer/services/wps/", url)
        self.assertEqual("tethys_services.views.wps_home", resolver._func_path)
