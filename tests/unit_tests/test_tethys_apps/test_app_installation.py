import unittest
import sys
import tethys_apps.app_installation as tethys_app_installation
from unittest import mock
from pathlib import Path

if sys.version_info[0] < 3:
    callable_mock_path = "__builtin__.callable"
else:
    callable_mock_path = "builtins.callable"


class TestAppInstallation(unittest.TestCase):
    def setUp(self):
        self.src_dir = Path(__file__).parents[3]
        self.rel_path = (
            Path("tests")
            / "apps"
            / "tethysapp-test_app"
            / "tethysapp"
            / "test_app"
            / "public"
        )
        self.root = str(self.src_dir / self.rel_path)

    def tearDown(self):
        pass

    def check_paths(self, ret):
        file_names = [Path(p).name for p in ret]
        for file_name in ("main.js", "icon.gif", "main.css"):
            self.assertIn(file_name, file_names)

    def test_find_resource_files(self):
        ret = tethys_app_installation.find_resource_files(self.root)
        self.check_paths(ret)

    def test_find_resource_files_rel_to(self):
        ret = tethys_app_installation.find_resource_files(self.root, "")
        self.check_paths(ret)

    def test_find_resource_files_of_type(self):
        app_root = self.src_dir / self.rel_path.parents[1]
        ret = tethys_app_installation.find_resource_files_of_type(
            "public", "test_app", app_root
        )
        self.check_paths(ret)

    @mock.patch("tethys_apps.app_installation.find_resource_files_of_type")
    def test_find_all_resource_files(self, mock_find_type):
        package = "package"
        app_root = "app_root"
        tethys_app_installation.find_all_resource_files(
            app_package=package, app_root=app_root
        )
        self.assertEqual(
            [
                mock.call("templates", package, app_root),
                mock.call("public", package, app_root),
                mock.call("workspaces", package, app_root),
            ],
            mock_find_type.call_args_list,
        )
