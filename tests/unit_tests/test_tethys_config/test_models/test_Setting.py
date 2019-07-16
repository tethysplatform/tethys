from tethys_sdk.testing import TethysTestCase
from tethys_config.models import Setting


class SettingTest(TethysTestCase):
    def set_up(self):
        pass

    def tear_down(self):
        pass

    def test_Setting_unicode(self):
        set_title = Setting.objects.get(name='Site Title')

        # Check result
        self.assertEqual('Site Title', str(set_title))

    def test_Setting_str(self):
        set_title = Setting.objects.get(name='Site Title')

        # Check result
        self.assertEqual('Site Title', str(set_title))

    def test_Setting_as_dict(self):
        set_all = Setting.as_dict()

        # Check result
        self.assertIsInstance(set_all, dict)
        self.assertIn('site_title', set_all)
