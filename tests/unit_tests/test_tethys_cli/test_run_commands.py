import sys
import unittest
from argparse import Namespace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

import yaml

from tethys_cli.run_commands import run_command, write_portal_config

COMPONENT_APP_SOURCE = """
from tethys_sdk.components import ComponentBase


class App(ComponentBase):
    pass


@App.page
def home(lib):
    return None
"""


def make_args(**kwargs):
    defaults = dict(
        app_file="app.py",
        port=8000,
        host="127.0.0.1",
        no_browser=True,
        no_reload=False,
        clean=False,
    )
    defaults.update(kwargs)
    return Namespace(**defaults)


class TestRunCommand(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.app_file = self.temp_path / "test_dashboard.py"
        self.app_file.write_text(COMPONENT_APP_SOURCE)
        self.tethys_home = self.temp_path / "tethys_home"

        home_patcher = mock.patch(
            "tethys_apps.utilities.get_tethys_home_dir",
            return_value=str(self.tethys_home),
        )
        home_patcher.start()
        self.addCleanup(home_patcher.stop)

        manage_patcher = mock.patch(
            "tethys_cli.run_commands.get_manage_path",
            return_value="path/to/manage.py",
        )
        self.mock_get_manage_path = manage_patcher.start()
        self.addCleanup(manage_patcher.stop)

        subprocess_run_patcher = mock.patch("tethys_cli.run_commands.subprocess.run")
        self.mock_subprocess_run = subprocess_run_patcher.start()
        self.mock_subprocess_run.return_value = mock.MagicMock(returncode=0)
        self.addCleanup(subprocess_run_patcher.stop)

        subprocess_call_patcher = mock.patch("tethys_cli.run_commands.subprocess.call")
        self.mock_subprocess_call = subprocess_call_patcher.start()
        self.addCleanup(subprocess_call_patcher.stop)

        timer_patcher = mock.patch("tethys_cli.run_commands.threading.Timer")
        self.mock_timer = timer_patcher.start()
        self.addCleanup(timer_patcher.stop)

    def tearDown(self):
        self.temp_dir.cleanup()

    @property
    def express_home(self):
        express_dir = self.tethys_home / "express"
        homes = list(express_dir.glob("test_dashboard_*"))
        return homes[0] if homes else None

    @mock.patch("tethys_cli.run_commands.write_error")
    def test_missing_file(self, mock_write_error):
        args = make_args(app_file=str(self.temp_path / "does_not_exist.py"))
        with self.assertRaises(SystemExit):
            run_command(args)
        mock_write_error.assert_called_once()

    @mock.patch("tethys_cli.run_commands.write_error")
    def test_not_a_component_app(self, mock_write_error):
        self.app_file.write_text("x = 1\n")
        args = make_args(app_file=str(self.app_file))
        with self.assertRaises(SystemExit):
            run_command(args)
        mock_write_error.assert_called_once()

    def test_happy_path(self):
        args = make_args(app_file=str(self.app_file))
        run_command(args)

        # Express home created with generated portal config
        express_home = self.express_home
        self.assertIsNotNone(express_home)
        config = yaml.safe_load((express_home / "portal_config.yml").read_text())
        portal_config = config["settings"]["TETHYS_PORTAL_CONFIG"]
        self.assertFalse(portal_config["MULTIPLE_APP_MODE"])
        self.assertEqual("test_dashboard", portal_config["STANDALONE_APP"])
        self.assertTrue(portal_config["ENABLE_OPEN_PORTAL"])

        # Database migrated
        migrate_call = self.mock_subprocess_run.call_args
        self.assertEqual(
            [sys.executable, "path/to/manage.py", "migrate", "--no-input"],
            migrate_call.args[0],
        )
        migrate_env = migrate_call.kwargs["env"]
        self.assertEqual(str(express_home), migrate_env["TETHYS_HOME"])
        self.assertEqual(
            str(self.app_file.resolve()), migrate_env["TETHYS_EXPRESS_APP"]
        )

        # Server started
        server_call = self.mock_subprocess_call.call_args
        self.assertEqual(
            [sys.executable, "path/to/manage.py", "runserver", "127.0.0.1:8000"],
            server_call.args[0],
        )
        self.assertEqual(str(express_home), server_call.kwargs["env"]["TETHYS_HOME"])

        # No browser requested
        self.mock_timer.assert_not_called()

    def test_no_reload_and_custom_port(self):
        args = make_args(app_file=str(self.app_file), no_reload=True, port=8080)
        run_command(args)
        server_call = self.mock_subprocess_call.call_args
        self.assertEqual(
            [
                sys.executable,
                "path/to/manage.py",
                "runserver",
                "--noreload",
                "127.0.0.1:8080",
            ],
            server_call.args[0],
        )

    def test_opens_browser(self):
        args = make_args(app_file=str(self.app_file), no_browser=False)
        run_command(args)
        self.mock_timer.assert_called_once()
        self.assertEqual(
            ["http://127.0.0.1:8000/"], self.mock_timer.call_args.kwargs["args"]
        )

    def test_clean_removes_existing_state(self):
        args = make_args(app_file=str(self.app_file))
        run_command(args)
        express_home = self.express_home
        sentinel = express_home / "sentinel.txt"
        sentinel.write_text("stale")

        args = make_args(app_file=str(self.app_file), clean=True)
        run_command(args)
        self.assertFalse(sentinel.exists())

    @mock.patch("tethys_cli.run_commands.write_error")
    def test_migrate_failure(self, mock_write_error):
        self.mock_subprocess_run.return_value = mock.MagicMock(
            returncode=1, stdout="out", stderr="err"
        )
        args = make_args(app_file=str(self.app_file))
        with self.assertRaises(SystemExit):
            run_command(args)
        mock_write_error.assert_called_once()
        self.mock_subprocess_call.assert_not_called()

    def test_secret_key_preserved_across_runs(self):
        args = make_args(app_file=str(self.app_file))
        run_command(args)
        config_path = self.express_home / "portal_config.yml"
        first_key = yaml.safe_load(config_path.read_text())["settings"]["SECRET_KEY"]

        run_command(args)
        second_key = yaml.safe_load(config_path.read_text())["settings"]["SECRET_KEY"]
        self.assertEqual(first_key, second_key)


class TestWritePortalConfig(unittest.TestCase):
    def test_write_portal_config(self):
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "portal_config.yml"
            write_portal_config(config_path, "my_app")
            config = yaml.safe_load(config_path.read_text())
            self.assertEqual(
                "my_app",
                config["settings"]["TETHYS_PORTAL_CONFIG"]["STANDALONE_APP"],
            )
            self.assertTrue(config["settings"]["SECRET_KEY"])
            self.assertEqual(["*"], config["settings"]["ALLOWED_HOSTS"])
