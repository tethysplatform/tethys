import sys
import unittest
from unittest import mock
from argparse import Namespace

from tethys_cli.start_commands import start_command, quickstart_command


class TestStartCommands(unittest.TestCase):
    @mock.patch("tethys_cli.start_commands.get_manage_path")
    @mock.patch("tethys_cli.start_commands.run_process")
    def test_start_command_without_port(self, mock_run_process, mock_get_manage_path):
        args = Namespace(port=None)
        mock_get_manage_path.return_value = "path/to/manage.py"
        start_command(args)
        mock_get_manage_path.assert_called_once_with(args)
        mock_run_process.assert_called_once_with(
            [sys.executable, "path/to/manage.py", "runserver"]
        )

    @mock.patch("tethys_cli.start_commands.get_manage_path")
    @mock.patch("tethys_cli.start_commands.run_process")
    def test_start_command_with_port(self, mock_run_process, mock_get_manage_path):
        args = Namespace(port="8000")
        mock_get_manage_path.return_value = "path/to/manage.py"
        start_command(args)
        mock_get_manage_path.assert_called_once_with(args)
        mock_run_process.assert_called_once_with(
            [sys.executable, "path/to/manage.py", "runserver", "8000"]
        )

    @mock.patch("tethys_cli.start_commands.start_command")
    @mock.patch("tethys_cli.start_commands.webbrowser")
    @mock.patch("tethys_cli.start_commands.configure_tethys_db")
    @mock.patch("tethys_cli.start_commands.process_args")
    @mock.patch("tethys_cli.start_commands.generate_command")
    @mock.patch("tethys_cli.start_commands.Path.exists")
    @mock.patch("tethys_cli.start_commands.get_destination_path")
    @mock.patch("tethys_cli.start_commands.Namespace")
    def test_quickstart_command_completely_fresh(
        self,
        mock_namespace,
        mock_get_destination_path,
        mock_path_exists,
        mock_generate_command,
        mock_process_args,
        mock_configure_tethys_db,
        mock_webbrowser,
        mock_start_command,
    ):
        mock_get_destination_path.return_value = "path/to/portal_config.yml"
        mock_path_exists.side_effect = [False, False]
        mock_namespace.side_effect = [
            "portal_config_args",
            "db_config_args",
            "start_args",
        ]

        args = Namespace()
        quickstart_command(args)

        mock_get_destination_path.assert_called_once_with(
            "portal_config_args", check_existence=False
        )
        mock_generate_command.assert_called_once_with("portal_config_args")
        mock_process_args.assert_called_once_with("db_config_args")
        mock_configure_tethys_db.assert_called_once_with(**mock_process_args())
        mock_webbrowser.open.assert_called_once_with("http://127.0.0.1:8000/")
        mock_start_command.assert_called_once_with("start_args")

    @mock.patch("tethys_cli.start_commands.write_warning")
    @mock.patch("tethys_cli.start_commands.exit")
    @mock.patch("tethys_cli.start_commands.Path.exists")
    @mock.patch("tethys_cli.start_commands.get_destination_path")
    @mock.patch("tethys_cli.start_commands.Namespace")
    def test_quickstart_command_portal_config_exists(
        self,
        mock_namespace,
        mock_get_destination_path,
        mock_path_exists,
        mock_exit,
        mock_write_warning,
    ):
        mock_get_destination_path.return_value = "path/to/portal_config.yml"
        mock_path_exists.return_value = True
        mock_namespace.side_effect = ["portal_config_args"]
        mock_exit.side_effect = SystemExit
        args = Namespace()

        self.assertRaises(SystemExit, quickstart_command, args)

        mock_get_destination_path.assert_called_once_with(
            "portal_config_args", check_existence=False
        )
        mock_write_warning.assert_called_once()
