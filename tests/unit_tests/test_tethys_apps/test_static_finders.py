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
        ret = tethys_static_finder.find(path)
        self.assertEqual(str(self.root / "css" / "main.css").lower(), ret.lower())

    def test_find_all(self):
        tethys_static_finder = TethysStaticFinder()
        path = Path("test_app") / "css" / "main.css"
        ret = tethys_static_finder.find(path, all=True)
        self.assertIn(
            str(self.root / "css" / "main.css").lower(),
            list(map(lambda x: x.lower(), ret)),
        )

    def test_find_location_with_no_prefix(self):
        prefix = None
        path = Path("css") / "main.css"

        tethys_static_finder = TethysStaticFinder()
        ret = tethys_static_finder.find_location(str(self.root), path, prefix)

        self.assertEqual(str(self.root / path), ret)

    def test_find_location_with_prefix_not_in_path(self):
        prefix = "tethys_app"
        path = Path("css") / "main.css"

        tethys_static_finder = TethysStaticFinder()
        ret = tethys_static_finder.find_location(str(self.root), path, prefix)

        self.assertIsNone(ret)

    def test_find_location_with_prefix_in_path(self):
        prefix = "tethys_app"
        path = Path("tethys_app") / "css" / "main.css"

        tethys_static_finder = TethysStaticFinder()
        ret = tethys_static_finder.find_location(str(self.root), path, prefix)

        self.assertEqual(str(self.root / "css" / "main.css"), ret)

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
