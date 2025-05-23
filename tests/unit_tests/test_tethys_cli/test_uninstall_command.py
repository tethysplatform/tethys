import sys
import unittest
from unittest import mock

from tethys_cli.uninstall_command import uninstall_command


class UninstallCommandTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch("tethys_cli.uninstall_command.subprocess.call")
    @mock.patch("tethys_cli.uninstall_command.get_manage_path")
    def test_uninstall_command(self, mock_get_manage_path, mock_subprocess_call):
        mock_args = mock.MagicMock()
        mock_args.is_extension = True
        mock_args.is_forced = False
        mock_args.app_or_extension = "foo_ext"
        mock_get_manage_path.return_value = "/foo/manage.py"
        mock_subprocess_call.return_value = True

        uninstall_command(mock_args)

        mock_get_manage_path.assert_called_once()
        mock_subprocess_call.assert_called_once()
        mock_subprocess_call.assert_called_with(
            [sys.executable, "/foo/manage.py", "tethys_app_uninstall", "foo_ext", "-e"]
        )

    @mock.patch("tethys_cli.uninstall_command.subprocess.call")
    @mock.patch("tethys_cli.uninstall_command.get_manage_path")
    def test_uninstall_command_no_extension(
        self, mock_get_manage_path, mock_subprocess_call
    ):
        mock_args = mock.MagicMock()
        mock_args.is_extension = False
        mock_args.is_forced = False

        mock_args.app_or_extension = "foo_app"
        mock_get_manage_path.return_value = "/foo/manage.py"
        mock_subprocess_call.return_value = True

        uninstall_command(mock_args)

        mock_get_manage_path.assert_called_once()
        mock_subprocess_call.assert_called_once()
        mock_subprocess_call.assert_called_with(
            [sys.executable, "/foo/manage.py", "tethys_app_uninstall", "foo_app"]
        )

    @mock.patch("tethys_cli.uninstall_command.subprocess.call")
    @mock.patch("tethys_cli.uninstall_command.get_manage_path")
    def test_uninstall_command_assert(self, mock_get_manage_path, mock_subprocess_call):
        mock_args = mock.MagicMock()
        mock_args.is_extension = False
        mock_args.is_forced = True

        mock_args.app_or_extension = "foo_ext"
        mock_get_manage_path.return_value = "/foo/manage.py"
        mock_subprocess_call.side_effect = KeyboardInterrupt

        uninstall_command(mock_args)

        mock_get_manage_path.assert_called_once()
        mock_subprocess_call.assert_called_once()
        mock_subprocess_call.assert_called_with(
            [sys.executable, "/foo/manage.py", "tethys_app_uninstall", "foo_ext", "-f"]
        )
