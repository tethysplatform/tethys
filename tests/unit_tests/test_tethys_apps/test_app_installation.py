import unittest
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

    def test_find_resource_files_rel_to(self):
        ret = tethys_app_installation.find_resource_files(self.root, '')
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
