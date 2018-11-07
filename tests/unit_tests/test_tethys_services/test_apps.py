import unittest
from tethys_services.apps import TethysServicesConfig


class TestApps(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_TethysServiceConfig(self):
        self.assertEqual('tethys_services', TethysServicesConfig.name)
        self.assertEqual("Tethys Services", TethysServicesConfig.verbose_name)
