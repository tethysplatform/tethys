import unittest

from django.apps import apps
from tethys_config.apps import TethysPortalConfig


class TethysConfigAppsTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_TethysPortalConfig(self):
        app_config = apps.get_app_config("tethys_config")
        name = app_config.name
        verbose_name = app_config.verbose_name

        self.assertEqual("tethys_config", name)
        self.assertEqual("Tethys Portal", verbose_name)
        self.assertTrue(isinstance(app_config, TethysPortalConfig))
