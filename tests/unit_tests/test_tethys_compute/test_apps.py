import unittest

from django.apps import apps
from tethys_compute.apps import TethysComputeConfig


class TethysComputeConfigAppsTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_TethysComputeConfig(self):
        app_config = apps.get_app_config("tethys_compute")
        name = app_config.name
        verbose_name = app_config.verbose_name

        self.assertEqual("tethys_compute", name)
        self.assertEqual("Tethys Compute", verbose_name)
        self.assertTrue(isinstance(app_config, TethysComputeConfig))
