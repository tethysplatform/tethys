import unittest
from unittest import mock
import tethys_apps
from tethys_apps.apps import TethysAppsConfig


class TestApps(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_TethysAppsConfig(self):
        self.assertEqual("tethys_apps", TethysAppsConfig.name)
        self.assertEqual("Tethys Apps", TethysAppsConfig.verbose_name)

    @mock.patch("tethys_apps.apps.sync_portal_cookies")
    @mock.patch("tethys_apps.apps.has_module", return_value=True)
    @mock.patch("tethys_apps.apps.SingletonHarvester")
    def test_ready(self, mock_singleton_harvester, _, mock_sync_portal_cookies):
        tethys_app_config_obj = TethysAppsConfig("tethys_apps", tethys_apps)
        tethys_app_config_obj.ready()
        mock_sync_portal_cookies.assert_called_once()
        mock_singleton_harvester().harvest.assert_called()
