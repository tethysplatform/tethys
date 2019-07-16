import unittest
from unittest import mock

from tethys_apps import helpers


class TethysAppsHelpersTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_tethysapp_dir(self):
        # Get the absolute path to the tethysapp directory
        result = helpers.get_tethysapp_dir()
        self.assertIn('/tethys_apps/tethysapp', result)

    def test_get_installed_tethys_apps(self):
        # Get list of apps installed in the tethysapp directory
        result = helpers.get_installed_tethys_apps()
        self.assertTrue('test_app' in result)

    @mock.patch('tethys_apps.helpers.SingletonHarvester')
    def test_get_installed_tethys_apps_exception(self, mock_harvester):
        mock_harvester().app_modules = {'foo_invalid_foo': 'tethys_app.foo_invalid_foo'}

        result = helpers.get_installed_tethys_apps()
        self.assertEqual({}, result)

    def test_get_installed_tethys_extensions(self):
        # Get a list of installed extensions
        result = helpers.get_installed_tethys_extensions()
        self.assertTrue('test_extension' in result)

    @mock.patch('tethys_apps.helpers.SingletonHarvester')
    def test_get_installed_tethys_extensions_error(self, mock_harvester):
        # Mock the extension_modules variable with bad data
        mock_harvester().extension_modules = {'foo_invalid_foo': 'tethys_ext.foo_invalid_foo'}

        # Get a list of installed extensions
        result = helpers.get_installed_tethys_extensions()
        self.assertEqual({}, result)
