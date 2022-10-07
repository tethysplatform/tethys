from tethys_sdk.testing import TethysTestCase
from tethys_apps.models import TethysExtension


class TethysExtensionTests(TethysTestCase):
    def set_up(self):
        self.test_ext = TethysExtension.objects.get(package="test_extension")

    def tear_down(self):
        pass

    def test_str(self):
        ret = str(self.test_ext)
        self.assertEqual("Test Extension", ret)
