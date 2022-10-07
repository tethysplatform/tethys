from tethys_sdk.testing import TethysTestCase
from tethys_config.models import SettingsCategory


class SettingsCategoryTest(TethysTestCase):
    def set_up(self):
        self.sc_gen = SettingsCategory.objects.get(name="General Settings")
        self.sc_home = SettingsCategory.objects.get(name="Home Page")

    def tear_down(self):
        pass

    def test_Settings_Category_unicode(self):
        self.assertEqual("General Settings", str(self.sc_gen))
        self.assertEqual("Home Page", str(self.sc_home))

    def test_Settings_Category_str(self):
        self.assertEqual("General Settings", str(self.sc_gen))
        self.assertEqual("Home Page", str(self.sc_home))
