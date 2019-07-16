import os
import unittest
from tethys_apps.static_finders import TethysStaticFinder


class TestTethysStaticFinder(unittest.TestCase):
    def setUp(self):
        self.src_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.root = os.path.join(self.src_dir, 'tests', 'apps', 'tethysapp-test_app',
                                 'tethysapp', 'test_app', 'public')

    def tearDown(self):
        pass

    def test_init(self):
        pass

    def test_find(self):
        tethys_static_finder = TethysStaticFinder()
        path = 'test_app/css/main.css'
        ret = tethys_static_finder.find(path)
        self.assertEqual(os.path.join(self.root, 'css/main.css'), ret)

    def test_find_all(self):
        tethys_static_finder = TethysStaticFinder()
        path = 'test_app/css/main.css'
        ret = tethys_static_finder.find(path, all=True)
        self.assertIn(os.path.join(self.root, 'css/main.css'), ret)

    def test_find_location_with_no_prefix(self):
        prefix = None
        path = 'css/main.css'

        tethys_static_finder = TethysStaticFinder()
        ret = tethys_static_finder.find_location(self.root, path, prefix)

        self.assertEqual(os.path.join(self.root, path), ret)

    def test_find_location_with_prefix_not_in_path(self):
        prefix = 'tethys_app'
        path = 'css/main.css'

        tethys_static_finder = TethysStaticFinder()
        ret = tethys_static_finder.find_location(self.root, path, prefix)

        self.assertIsNone(ret)

    def test_find_location_with_prefix_in_path(self):
        prefix = 'tethys_app'
        path = 'tethys_app/css/main.css'

        tethys_static_finder = TethysStaticFinder()
        ret = tethys_static_finder.find_location(self.root, path, prefix)

        self.assertEqual(os.path.join(self.root, 'css/main.css'), ret)

    def test_list(self):
        tethys_static_finder = TethysStaticFinder()
        expected_ignore_patterns = ''
        expected_app_paths = []
        for path, storage in tethys_static_finder.list(expected_ignore_patterns):
            if 'test_app' in storage.location:
                expected_app_paths.append(path)

        self.assertIn('js/main.js', expected_app_paths)
        self.assertIn('images/icon.gif', expected_app_paths)
        self.assertIn('css/main.css', expected_app_paths)
