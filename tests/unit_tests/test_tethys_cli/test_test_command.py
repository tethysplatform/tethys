import sys
import unittest
from pathlib import Path
from os import devnull

from unittest import mock

from tethys_apps.utilities import get_tethys_src_dir
from tethys_cli.test_command import _test_command, check_and_install_prereqs

FNULL = open(devnull, "w")
TETHYS_SRC_DIRECTORY = get_tethys_src_dir()


class TestCommandTests(unittest.TestCase):
    def setUp(self):
        mock.patch(
            "tethys_cli.test_command.subprocess.run", side_effect=Exception
        ).start()

    def tearDown(self):
        mock.patch.stopall()

    @mock.patch("tethys_cli.test_command.Path.is_file", return_value=True)
    @mock.patch("tethys_cli.test_command.run_process")
    @mock.patch("tethys_cli.test_command.get_manage_path")
    def test_test_command_no_coverage_file_path(
        self, mock_get_manage_path, mock_run_process, _
    ):
        mock_args = mock.MagicMock()
        mock_args.coverage = False
        mock_args.coverage_html = False
        mock_args.file = "foo/bar_file"
        mock_args.unit = False
        mock_args.gui = False
        mock_args.verbosity = None
        mock_get_manage_path.return_value = "/foo/manage.py"
        mock_run_process.return_value = 0

        self.assertRaises(SystemExit, _test_command, mock_args)
        mock_get_manage_path.assert_called()
        mock_run_process.assert_called_once()
        mock_run_process.assert_called_with(
            [sys.executable, "/foo/manage.py", "test", "foo", "--pattern", "bar_file"]
        )

    @mock.patch("tethys_cli.test_command.run_process")
    @mock.patch("tethys_cli.test_command.get_manage_path")
    def test_test_command_no_coverage_file_dot_notation(
        self, mock_get_manage_path, mock_run_process
    ):
        mock_args = mock.MagicMock()
        mock_args.coverage = False
        mock_args.coverage_html = False
        mock_args.file = "foo_file"
        mock_args.unit = False
        mock_args.gui = False
        mock_args.verbosity = None
        mock_get_manage_path.return_value = "/foo/manage.py"
        mock_run_process.return_value = 0

        self.assertRaises(SystemExit, _test_command, mock_args)
        mock_get_manage_path.assert_called()
        mock_run_process.assert_called_once()
        mock_run_process.assert_called_with(
            [sys.executable, "/foo/manage.py", "test", "foo_file"]
        )

    @mock.patch("tethys_cli.test_command.TETHYS_SRC_DIRECTORY", "/foo")
    @mock.patch("tethys_cli.test_command.run_process")
    @mock.patch("tethys_cli.test_command.get_manage_path")
    def test_test_command_coverage_unit(self, mock_get_manage_path, mock_run_process):
        mock_args = mock.MagicMock()
        mock_args.coverage = True
        mock_args.coverage_html = False
        mock_args.file = None
        mock_args.unit = True
        mock_args.gui = False
        mock_args.verbosity = None
        mock_get_manage_path.return_value = "/foo/manage.py"
        mock_run_process.return_value = 0

        self.assertRaises(SystemExit, _test_command, mock_args)
        mock_get_manage_path.assert_called()
        mock_run_process.assert_called()
        mock_run_process.assert_any_call(
            [
                "coverage",
                "run",
                f"--rcfile={Path('/foo/tests/coverage.cfg')}",
                "/foo/manage.py",
                "test",
                str(Path("/foo/tests/unit_tests")),
            ]
        )
        mock_run_process.assert_called_with(
            ["coverage", "report", f"--rcfile={Path('/foo/tests/coverage.cfg')}"]
        )

    @mock.patch("tethys_cli.test_command.run_process")
    @mock.patch("tethys_cli.test_command.get_manage_path")
    def test_test_command_coverage_unit_file_app_package(
        self, mock_get_manage_path, mock_run_process
    ):
        mock_args = mock.MagicMock()
        mock_args.coverage = True
        mock_args.coverage_html = False
        mock_args.file = "/foo/tethys_apps.tethysapp.foo"
        mock_args.unit = True
        mock_args.gui = False
        mock_args.verbosity = None
        mock_get_manage_path.return_value = "/foo/manage.py"
        mock_run_process.return_value = 0

        self.assertRaises(SystemExit, _test_command, mock_args)
        mock_get_manage_path.assert_called()
        mock_run_process.assert_called()
        mock_run_process.assert_any_call(
            [
                "coverage",
                "run",
                "--source=tethys_apps.tethysapp.foo,tethysapp.foo",
                "/foo/manage.py",
                "test",
                "/foo/tethys_apps.tethysapp.foo",
            ]
        )
        mock_run_process.assert_called_with(["coverage", "report"])

    @mock.patch("tethys_cli.test_command.TETHYS_SRC_DIRECTORY", "/foo")
    @mock.patch("tethys_cli.test_command.run_process")
    @mock.patch("tethys_cli.test_command.get_manage_path")
    def test_test_command_coverage_html_unit_file_app_package(
        self, mock_get_manage_path, mock_run_process
    ):
        mock_args = mock.MagicMock()
        mock_args.coverage = False
        mock_args.coverage_html = True
        mock_args.file = "/foo/tethys_apps.tethysapp.foo"
        mock_args.unit = True
        mock_args.gui = False
        mock_args.verbosity = None
        mock_get_manage_path.return_value = "/foo/manage.py"
        mock_run_process.return_value = 0

        self.assertRaises(SystemExit, _test_command, mock_args)
        mock_get_manage_path.assert_called()
        mock_run_process.assert_called()
        mock_run_process.assert_any_call(
            [
                "coverage",
                "run",
                "--source=tethys_apps.tethysapp.foo,tethysapp.foo",
                "/foo/manage.py",
                "test",
                "/foo/tethys_apps.tethysapp.foo",
            ]
        )
        mock_run_process.assert_any_call(
            [
                "coverage",
                "html",
                f"--directory={Path('/foo/tests/coverage_html_report')}",
            ]
        )
        mock_run_process.assert_called_with(
            ["open", str(Path("/foo/tests/coverage_html_report/index.html"))]
        )

    @mock.patch("tethys_cli.test_command.run_process")
    @mock.patch("tethys_cli.test_command.get_manage_path")
    def test_test_command_coverage_unit_file_extension_package(
        self, mock_get_manage_path, mock_run_process
    ):
        mock_args = mock.MagicMock()
        mock_args.coverage = True
        mock_args.coverage_html = False
        mock_args.file = "/foo/tethysext.foo"
        mock_args.unit = True
        mock_args.gui = False
        mock_args.verbosity = None
        mock_get_manage_path.return_value = "/foo/manage.py"
        mock_run_process.return_value = 0

        self.assertRaises(SystemExit, _test_command, mock_args)
        mock_get_manage_path.assert_called()
        mock_run_process.assert_called()
        mock_run_process.assert_any_call(
            [
                "coverage",
                "run",
                "--source=tethysext.foo,tethysext.foo",
                "/foo/manage.py",
                "test",
                "/foo/tethysext.foo",
            ]
        )
        mock_run_process.assert_called_with(["coverage", "report"])

    @mock.patch("tethys_cli.test_command.TETHYS_SRC_DIRECTORY", "/foo/bar")
    @mock.patch("tethys_cli.test_command.run_process")
    @mock.patch("tethys_cli.test_command.get_manage_path")
    def test_test_command_coverage_html_gui_file(
        self, mock_get_manage_path, mock_run_process
    ):
        mock_args = mock.MagicMock()
        mock_args.coverage = False
        mock_args.coverage_html = True
        mock_args.file = "foo_file"
        mock_args.unit = False
        mock_args.gui = True
        mock_args.verbosity = None
        mock_get_manage_path.return_value = "/foo/manage.py"
        mock_run_process.return_value = 0

        self.assertRaises(SystemExit, _test_command, mock_args)
        mock_get_manage_path.assert_called()
        mock_run_process.assert_called()
        mock_run_process.assert_any_call(
            [
                "coverage",
                "run",
                f"--rcfile={Path('/foo/bar/tests/coverage.cfg')}",
                "/foo/manage.py",
                "test",
                "foo_file",
            ]
        )
        mock_run_process.assert_any_call(
            ["coverage", "html", f"--rcfile={Path('/foo/bar/tests/coverage.cfg')}"]
        )
        mock_run_process.assert_called_with(
            ["open", str(Path("/foo/bar/tests/coverage_html_report/index.html"))]
        )

    @mock.patch("tethys_cli.test_command.TETHYS_SRC_DIRECTORY", "/foo")
    @mock.patch("tethys_cli.test_command.webbrowser.open_new_tab")
    @mock.patch("tethys_cli.test_command.run_process")
    @mock.patch("tethys_cli.test_command.get_manage_path")
    def test_test_command_coverage_html_gui_file_exception(
        self, mock_get_manage_path, mock_run_process, mock_open_new_tab
    ):
        mock_args = mock.MagicMock()
        mock_args.coverage = False
        mock_args.coverage_html = True
        mock_args.file = "foo_file"
        mock_args.unit = False
        mock_args.gui = True
        mock_args.verbosity = None
        mock_get_manage_path.return_value = "/foo/manage.py"
        mock_run_process.side_effect = [0, 0, 1]
        mock_open_new_tab.return_value = 1

        self.assertRaises(SystemExit, _test_command, mock_args)
        mock_get_manage_path.assert_called()
        mock_run_process.assert_called()
        mock_run_process.assert_any_call(
            [
                "coverage",
                "run",
                f"--rcfile={Path('/foo/tests/coverage.cfg')}",
                "/foo/manage.py",
                "test",
                "foo_file",
            ]
        )
        mock_run_process.assert_any_call(
            ["coverage", "html", f"--rcfile={Path('/foo/tests/coverage.cfg')}"]
        )
        mock_run_process.assert_called_with(
            ["open", str(Path("/foo/tests/coverage_html_report/index.html"))]
        )
        mock_open_new_tab.assert_called_once()
        mock_open_new_tab.assert_called_with(
            str(Path("/foo/tests/coverage_html_report/index.html"))
        )

    @mock.patch("tethys_cli.test_command.TETHYS_SRC_DIRECTORY", "/foo")
    @mock.patch("tethys_cli.test_command.run_process")
    @mock.patch("tethys_cli.test_command.get_manage_path")
    def test_test_command_unit_no_file(self, mock_get_manage_path, mock_run_process):
        mock_args = mock.MagicMock()
        mock_args.coverage = False
        mock_args.coverage_html = False
        mock_args.file = None
        mock_args.unit = True
        mock_args.gui = False
        mock_args.verbosity = None
        mock_get_manage_path.return_value = "/foo/manage.py"
        mock_run_process.return_value = 0

        self.assertRaises(SystemExit, _test_command, mock_args)

        mock_get_manage_path.assert_called()
        mock_run_process.assert_called_once()
        mock_run_process.assert_called_with(
            [
                sys.executable,
                "/foo/manage.py",
                "test",
                str(Path("/foo/tests/unit_tests")),
            ]
        )

    @mock.patch("tethys_cli.test_command.TETHYS_SRC_DIRECTORY", "/foo")
    @mock.patch("tethys_cli.test_command.run_process")
    @mock.patch("tethys_cli.test_command.get_manage_path")
    def test_test_command_gui_no_file(self, mock_get_manage_path, mock_run_process):
        mock_args = mock.MagicMock()
        mock_args.coverage = False
        mock_args.coverage_html = False
        mock_args.file = None
        mock_args.unit = False
        mock_args.gui = True
        mock_args.verbosity = None
        mock_get_manage_path.return_value = "/foo/manage.py"
        mock_run_process.return_value = 0

        self.assertRaises(SystemExit, _test_command, mock_args)
        mock_get_manage_path.assert_called()
        mock_run_process.assert_called_once()
        mock_run_process.assert_called_with(
            [
                sys.executable,
                "/foo/manage.py",
                "test",
                str(Path("/foo/tests/gui_tests")),
            ]
        )

    @mock.patch("tethys_cli.test_command.write_warning")
    @mock.patch("tethys_cli.test_command.subprocess.run")
    @mock.patch("tethysapp.test_app", new=None)
    @mock.patch("tethysext.test_extension", new=None)
    def test_check_and_install_prereqs(self, mock_run_process, mock_write_warning):
        tests_path = Path(TETHYS_SRC_DIRECTORY) / "tests"
        check_and_install_prereqs(tests_path)
        setup_path = tests_path / "apps" / "tethysapp-test_app"
        extension_setup_path = tests_path / "extensions" / "tethysext-test_extension"

        mock_run_process.assert_any_call(
            [sys.executable, "-m", "pip", "install", "-e", "."],
            stdout=mock.ANY,
            stderr=mock.ANY,
            cwd=str(setup_path),
            check=True,
        )

        mock_run_process.assert_any_call(
            [sys.executable, "-m", "pip", "install", "-e", "."],
            stdout=mock.ANY,
            stderr=mock.ANY,
            cwd=str(extension_setup_path),
            check=True,
        )

        mock_write_warning.assert_called()

    @mock.patch("tethys_cli.test_command.run_process")
    @mock.patch("tethys_cli.test_command.get_manage_path")
    def test_test_command_verbosity(self, mock_get_manage_path, mock_run_process):
        mock_args = mock.MagicMock()
        mock_args.coverage = False
        mock_args.coverage_html = False
        mock_args.file = None
        mock_args.unit = False
        mock_args.gui = False
        mock_args.verbosity = "2"
        mock_get_manage_path.return_value = "/foo/manage.py"
        mock_run_process.return_value = 0

        self.assertRaises(SystemExit, _test_command, mock_args)
        mock_get_manage_path.assert_called()
        mock_run_process.assert_called_with(
            [sys.executable, "/foo/manage.py", "test", "-v", "2"]
        )

    @mock.patch("tethys_cli.test_command.write_error")
    @mock.patch("tethys_cli.test_command.check_and_install_prereqs")
    @mock.patch("tethys_cli.test_command.get_manage_path")
    def test_test_command_not_installed(
        self,
        mock_get_manage_path,
        mock_check_and_install_prereqs,
        mock_write_error,
    ):
        mock_args = mock.MagicMock()
        mock_args.coverage = False
        mock_args.coverage_html = False
        mock_args.file = None
        mock_args.unit = True
        mock_args.gui = False
        mock_args.verbosity = None
        mock_get_manage_path.return_value = "/foo/manage.py"
        mock_check_and_install_prereqs.side_effect = FileNotFoundError

        self.assertRaises(SystemExit, _test_command, mock_args)
        mock_write_error.assert_called()
