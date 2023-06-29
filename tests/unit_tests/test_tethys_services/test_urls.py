from django.urls import reverse, resolve
from tethys_sdk.testing import TethysTestCase

from django.conf import settings

prefix_to_path = ""
if settings.PREFIX_TO_PATH is not None and len(settings.PREFIX_TO_PATH) != 0:
    prefix_to_path = f"/{settings.PREFIX_TO_PATH}"


class TestTethysServicesUrls(TethysTestCase):
    def set_up(self):
        pass

    def tear_down(self):
        pass

    def test_service_urls_wps_services(self):
        url = reverse("services:wps_service", kwargs={"service": "foo"})
        resolver = resolve(url)
        self.assertEqual(f"{prefix_to_path}/developer/services/wps/foo/", url)
        self.assertEqual("wps_service", resolver.func.__name__)
        self.assertEqual("tethys_services.views", resolver.func.__module__)

    def test_service_urls_wps_process(self):
        url = reverse(
            "services:wps_process", kwargs={"service": "foo", "identifier": "bar"}
        )
        resolver = resolve(url)
        self.assertEqual(
            f"{prefix_to_path}/developer/services/wps/foo/process/bar/", url
        )
        self.assertEqual("wps_process", resolver.func.__name__)
        self.assertEqual("tethys_services.views", resolver.func.__module__)

    def test_urlpatterns_datasethome(self):
        url = reverse("services:datasets_home")
        resolver = resolve(url)
        self.assertEqual(f"{prefix_to_path}/developer/services/datasets/", url)
        self.assertEqual("datasets_home", resolver.func.__name__)
        self.assertEqual("tethys_services.views", resolver.func.__module__)

    def test_urlpatterns_wpshome(self):
        url = reverse("services:wps_home")
        resolver = resolve(url)
        self.assertEqual(f"{prefix_to_path}/developer/services/wps/", url)
        self.assertEqual("wps_home", resolver.func.__name__)
        self.assertEqual("tethys_services.views", resolver.func.__module__)
