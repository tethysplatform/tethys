import unittest
import tethys_apps.base.testing.testing as base_testing
import mock
from tethys_apps.base.app_base import TethysBase

class TestTethysTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('tethys_apps.harvester.SingletonHarvester')
    def test_TethysTestCase(self, mock_harvest):
        mock_harvest().extension_modules = {'Test Extension': 'tethysext.test_extension'}
        apps = TethysBase()
