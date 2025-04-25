from pathlib import Path
import unittest
from tethys_apps.static_finders import TethysStaticFinder


class TestTethysStaticFinder(unittest.TestCase):
    def setUp(self):
        self.src_dir = Path(__file__).parents[3]
        self.root = (
            self.src_dir
            / "tests"
            / "apps"
            / "tethysapp-test_app"
            / "tethysapp"
            / "test_app"
            / "public"
        )

    def tearDown(self):
        pass

    def test_init(self):
        pass

    def test_find(self):
        tethys_static_finder = TethysStaticFinder()
        path = Path("test_app") / "css" / "main.css"
        path_ret = tethys_static_finder.find(path)
        self.assertEqual(self.root / "css" / "main.css", path_ret)
        str_ret = tethys_static_finder.find(str(path))
        self.assertEqual(self.root / "css" / "main.css", str_ret)

    def test_find_all(self):
        import django

        tethys_static_finder = TethysStaticFinder()
        path = Path("test_app") / "css" / "main.css"
        use_find_all = django.VERSION >= (5, 2)
        if use_find_all:
            path_ret = tethys_static_finder.find(path, find_all=True)
            str_ret = tethys_static_finder.find(str(path), find_all=True)
        else:
            path_ret = tethys_static_finder.find(path, all=True)
            str_ret = tethys_static_finder.find(str(path), all=True)
        self.assertIn(self.root / "css" / "main.css", path_ret)
        self.assertIn(self.root / "css" / "main.css", str_ret)

    def test_find_location_with_no_prefix(self):
        prefix = None
        path = Path("css") / "main.css"

        tethys_static_finder = TethysStaticFinder()
        path_ret = tethys_static_finder.find_location(self.root, path, prefix)
        self.assertEqual(self.root / path, path_ret)
        str_ret = tethys_static_finder.find_location(str(self.root), path, prefix)
        self.assertEqual(self.root / path, str_ret)

    def test_find_location_with_prefix_not_in_path(self):
        prefix = "tethys_app"
        path = Path("css") / "main.css"

        tethys_static_finder = TethysStaticFinder()
        path_ret = tethys_static_finder.find_location(self.root, path, prefix)
        self.assertIsNone(path_ret)
        str_ret = tethys_static_finder.find_location(str(self.root), path, prefix)
        self.assertIsNone(str_ret)

    def test_find_location_with_prefix_in_path(self):
        prefix = "tethys_app"
        path = Path("tethys_app") / "css" / "main.css"

        tethys_static_finder = TethysStaticFinder()
        path_ret = tethys_static_finder.find_location(self.root, path, prefix)
        self.assertEqual(self.root / "css" / "main.css", path_ret)
        str_ret = tethys_static_finder.find_location(str(self.root), path, prefix)
        self.assertEqual(self.root / "css" / "main.css", str_ret)

    def test_list(self):
        tethys_static_finder = TethysStaticFinder()
        expected_ignore_patterns = ""
        expected_app_paths = []
        for path, storage in tethys_static_finder.list(expected_ignore_patterns):
            if "test_app" in storage.location:
                expected_app_paths.append(path)

        self.assertIn(str(Path("js") / "main.js"), expected_app_paths)
        self.assertIn(str(Path("images") / "icon.gif"), expected_app_paths)
        self.assertIn(str(Path("css") / "main.css"), expected_app_paths)
