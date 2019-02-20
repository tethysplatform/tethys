import unittest
from unittest import mock
import os
import sys
import tethys_apps.app_installation as tethys_app_installation

if sys.version_info[0] < 3:
    callable_mock_path = '__builtin__.callable'
else:
    callable_mock_path = 'builtins.callable'


class TestAppInstallation(unittest.TestCase):
    def setUp(self):
        self.src_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.root = os.path.join(self.src_dir, 'tests', 'apps', 'tethysapp-test_app',
                                 'tethysapp',  'test_app', 'public')

    def tearDown(self):
        pass

    def test_find_resource_files(self):
        ret = tethys_app_installation.find_resource_files(self.root)
        main_js = False
        icon_gif = False
        main_css = False
        if any('/js/main.js' in s for s in ret):
            main_js = True
        if any('/images/icon.gif' in s for s in ret):
            icon_gif = True
        if any('/css/main.css' in s for s in ret):
            main_css = True

        self.assertTrue(main_js)
        self.assertTrue(icon_gif)
        self.assertTrue(main_css)

    def test_get_tethysapp_directory(self):
        ret = tethys_app_installation.get_tethysapp_directory()
        self.assertIn('tethys_apps/tethysapp', ret)

    @mock.patch('tethys_apps.app_installation.install')
    def test__run_install(self, mock_install):
        # mock the self input
        mock_self = mock.MagicMock(app_package='tethys_apps', app_package_dir='/test_app/', dependencies=['foo'])

        # call the method for testing
        tethys_app_installation._run_install(self=mock_self)

        # check the install call
        mock_install.run.assert_called_with(mock_self)

    @mock.patch('tethys_apps.app_installation.develop')
    @mock.patch(callable_mock_path)
    def test__run_develop(self, mock_callable, mock_develop):

        # mock the self input
        mock_self = mock.MagicMock(app_package='tethys_apps', app_package_dir='/test_app/', dependencies=['foo'])

        # call the method for testing
        tethys_app_installation._run_develop(self=mock_self)

        # mock callable method
        mock_callable.return_value = True

        # check the develop call
        mock_develop.run.assert_called_with(mock_self)

    def test_custom_install_command(self):
        app_package = 'tethys_apps'
        app_package_dir = '/test_app/'
        dependencies = 'foo'

        ret = tethys_app_installation.custom_install_command(app_package, app_package_dir, dependencies)

        self.assertEquals('tethys_apps', ret.app_package)
        self.assertEquals('/test_app/', ret.app_package_dir)
        self.assertEquals('foo', ret.dependencies)
        self.assertEquals('tethys_apps.app_installation', ret.__module__)

    def test_custom_develop_command(self):
        app_package = 'tethys_apps1'
        app_package_dir = '/test_app/'
        dependencies = 'foo'

        ret = tethys_app_installation.custom_develop_command(app_package, app_package_dir, dependencies)

        self.assertEquals('tethys_apps1', ret.app_package)
        self.assertEquals('/test_app/', ret.app_package_dir)
        self.assertEquals('foo', ret.dependencies)
        self.assertEquals('tethys_apps.app_installation', ret.__module__)
