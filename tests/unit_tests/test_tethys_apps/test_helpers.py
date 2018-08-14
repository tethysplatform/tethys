import unittest
import mock

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

    @mock.patch('tethys_apps.helpers.os.path.isdir')
    @mock.patch('tethys_apps.helpers.os.listdir')
    @mock.patch('tethys_apps.helpers.get_tethysapp_dir')
    def test_get_installed_tethys_apps_mock(self, mock_dir, mock_listdir, mock_isdir):
        # Get list of apps installed in the mock directory
        mock_dir.return_value = '/foo/bar'
        mock_listdir.return_value = ['.gitignore', 'foo_app', '__init__.py', '__init__.pyc']
        mock_isdir.side_effect = [False, True, False, False]
        result = helpers.get_installed_tethys_apps()
        self.assertTrue('foo_app' in result)

    def test_get_installed_tethys_extensions(self):
        # Get a list of installed extensions
        result = helpers.get_installed_tethys_extensions()
        self.assertTrue('test_extension' in result)

    @mock.patch('tethys_apps.helpers.SingletonHarvester')
    def test_get_installed_tethys_extensions_error(self, mock_harvester):
        # Mock the extension_modules variable with bad data
        mock_harvester().extension_modules = {'foo_invalid_foo': 'tethysext.foo_invalid_foo'}

        # Get a list of installed extensions
        result = helpers.get_installed_tethys_extensions()
        self.assertEqual({}, result)
