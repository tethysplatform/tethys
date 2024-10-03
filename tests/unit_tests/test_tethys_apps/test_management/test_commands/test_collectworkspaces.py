import unittest
from unittest import mock
from pathlib import Path

from tethys_apps.management.commands import collectworkspaces


class ManagementCommandsCollectWorkspacesTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_collectworkspaces_add_arguments(self):
        from argparse import ArgumentParser

        parser = ArgumentParser()
        cmd = collectworkspaces.Command()
        cmd.add_arguments(parser)

        self.assertIn("[-f]", parser.format_usage())
        self.assertIn("--force", parser.format_help())
        self.assertIn("Force the overwrite the app directory", parser.format_help())

    @mock.patch("tethys_apps.management.commands.collectworkspaces.print")
    @mock.patch("tethys_apps.management.commands.pre_collectstatic.exit")
    @mock.patch("tethys_apps.management.commands.collectworkspaces.settings")
    def test_collectworkspaces_handle_no_atts(
        self, mock_settings, mock_exit, mock_print
    ):
        mock_settings.TETHYS_WORKSPACES_ROOT = None
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        cmd = collectworkspaces.Command()
        self.assertRaises(SystemExit, cmd.handle)

        check_msg = (
            "WARNING: Cannot find the TETHYS_WORKSPACES_ROOT setting. "
            "Please provide the path to the static directory using the TETHYS_WORKSPACES_ROOT "
            "setting in the portal_config.yml file and try again."
        )

        mock_print.assert_called_with(check_msg)

    @mock.patch("tethys_apps.management.commands.collectworkspaces.print")
    @mock.patch("tethys_apps.management.commands.pre_collectstatic.shutil.move")
    @mock.patch("tethys_apps.management.commands.pre_collectstatic.Path.mkdir")
    @mock.patch("tethys_apps.management.commands.pre_collectstatic.Path.is_dir")
    @mock.patch(
        "tethys_apps.management.commands.collectworkspaces.get_installed_tethys_items"
    )
    @mock.patch("tethys_apps.management.commands.collectworkspaces.settings")
    def test_collectworkspaces_handle_no_force_not_dir(
        self,
        mock_settings,
        mock_get_apps,
        mock_is_dir,
        mock_mkdir,
        mock_shutil_move,
        mock_print,
    ):
        mock_settings.TETHYS_WORKSPACES_ROOT = Path.home() / "foo" / "workspace"
        mock_get_apps.return_value = {
            "foo_app": Path.home() / "foo" / "testing" / "tests" / "foo_app"
        }
        mock_is_dir.return_value = False

        cmd = collectworkspaces.Command()
        cmd.handle(force=False)

        mock_get_apps.assert_called_once()
        mock_is_dir.assert_called()
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_shutil_move.assert_called_once_with(
            Path.home() / "foo" / "testing" / "tests" / "foo_app" / "workspaces",
            Path.home() / "foo" / "workspace" / "foo_app",
        )

        msg_info = f'INFO: Moving workspace directories of apps to "{Path.home() / "foo" / "workspace"}" and linking back.'

        msg_warning = 'WARNING: The workspace_path for app "foo_app" is not a directory. Making workspace directory...'

        print_call_args = mock_print.call_args_list

        self.assertEqual(msg_info, print_call_args[0][0][0])

        self.assertEqual(msg_warning, print_call_args[1][0][0])

    @mock.patch("tethys_apps.management.commands.collectworkspaces.print")
    @mock.patch("tethys_apps.management.commands.pre_collectstatic.Path.is_symlink")
    @mock.patch("tethys_apps.management.commands.pre_collectstatic.Path.is_dir")
    @mock.patch(
        "tethys_apps.management.commands.collectworkspaces.get_installed_tethys_items"
    )
    @mock.patch("tethys_apps.management.commands.collectworkspaces.settings")
    def test_collectworkspaces_handle_no_force_is_link(
        self,
        mock_settings,
        mock_get_apps,
        mock_is_dir,
        mock_is_symlink,
        mock_print,
    ):
        mock_settings.TETHYS_WORKSPACES_ROOT = Path.home() / "foo" / "workspace"
        mock_get_apps.return_value = {
            "foo_app": Path.home() / "foo" / "testing" / "tests" / "foo_app"
        }
        mock_is_dir.return_value = True
        mock_is_symlink.return_value = True

        cmd = collectworkspaces.Command()
        cmd.handle(force=False)

        mock_get_apps.assert_called_once()
        mock_is_dir.assert_called_once()
        mock_is_symlink.assert_called_once()
        msg_in = f'INFO: Moving workspace directories of apps to "{Path.home() / "foo" / "workspace"}" and linking back.'
        mock_print.assert_called_with(msg_in)

    @mock.patch("tethys_apps.management.commands.collectworkspaces.print")
    @mock.patch("tethys_apps.management.commands.pre_collectstatic.Path.symlink_to")
    @mock.patch("tethys_apps.management.commands.pre_collectstatic.shutil.move")
    @mock.patch("tethys_apps.management.commands.pre_collectstatic.Path.exists")
    @mock.patch("tethys_apps.management.commands.pre_collectstatic.Path.is_symlink")
    @mock.patch("tethys_apps.management.commands.pre_collectstatic.Path.is_dir")
    @mock.patch(
        "tethys_apps.management.commands.collectworkspaces.get_installed_tethys_items"
    )
    @mock.patch("tethys_apps.management.commands.collectworkspaces.settings")
    def test_collectworkspaces_handle_not_exists(
        self,
        mock_settings,
        mock_get_apps,
        mock_is_dir,
        mock_is_symlink,
        mock_path_exists,
        mock_shutil_move,
        mock_symlink_to,
        mock_print,
    ):
        mock_settings.TETHYS_WORKSPACES_ROOT = Path.home() / "foo" / "workspace"
        mock_get_apps.return_value = {
            "foo_app": Path.home() / "foo" / "testing" / "tests" / "foo_app"
        }
        mock_is_dir.side_effect = [True, True]
        mock_is_symlink.return_value = False
        mock_path_exists.return_value = False
        mock_shutil_move.return_value = True
        mock_symlink_to.return_value = True

        cmd = collectworkspaces.Command()
        cmd.handle(force=True)

        mock_get_apps.assert_called_once()
        self.assertEqual(mock_is_dir.call_count, 2)
        mock_is_symlink.assert_called_once()
        mock_path_exists.assert_called_once()
        mock_shutil_move.assert_called_once_with(
            Path.home() / "foo" / "testing" / "tests" / "foo_app" / "workspaces",
            Path.home() / "foo" / "workspace" / "foo_app",
        )
        msg_first_info = f'INFO: Moving workspace directories of apps to "{Path.home() / "foo" / "workspace"}" and linking back.'
        msg_second_info = (
            'INFO: Successfully linked "workspaces" directory to '
            'TETHYS_WORKSPACES_ROOT for app "foo_app".'
        )

        print_call_args = mock_print.call_args_list

        self.assertEqual(msg_first_info, print_call_args[0][0][0])

        self.assertEqual(msg_second_info, print_call_args[1][0][0])

    @mock.patch("tethys_apps.management.commands.collectworkspaces.print")
    @mock.patch("tethys_apps.management.commands.pre_collectstatic.shutil.rmtree")
    @mock.patch("tethys_apps.management.commands.pre_collectstatic.Path.symlink_to")
    @mock.patch("tethys_apps.management.commands.pre_collectstatic.shutil.move")
    @mock.patch("tethys_apps.management.commands.pre_collectstatic.Path.exists")
    @mock.patch("tethys_apps.management.commands.pre_collectstatic.Path.is_symlink")
    @mock.patch("tethys_apps.management.commands.pre_collectstatic.Path.is_dir")
    @mock.patch(
        "tethys_apps.management.commands.collectworkspaces.get_installed_tethys_items"
    )
    @mock.patch("tethys_apps.management.commands.collectworkspaces.settings")
    def test_collectworkspaces_handle_exists_no_force(
        self,
        mock_settings,
        mock_get_apps,
        mock_is_dir,
        mock_is_symlink,
        mock_path_exists,
        mock_shutil_move,
        mock_symlink_to,
        mock_shutil_rmtree,
        mock_print,
    ):
        app_name = "foo_app"
        app_path = Path.home() / "foo" / "testing" / "tests" / app_name
        app_ws_path = app_path / "workspaces"
        tethys_workspaces_root = Path.home() / "foo" / "workspace"
        mock_settings.TETHYS_WORKSPACES_ROOT = tethys_workspaces_root
        mock_get_apps.return_value = {app_name: app_path}
        mock_is_dir.side_effect = [True, True]
        mock_is_symlink.return_value = False
        mock_path_exists.return_value = True
        mock_shutil_move.return_value = True
        mock_symlink_to.return_value = True
        mock_shutil_rmtree.return_value = True

        cmd = collectworkspaces.Command()
        cmd.handle(force=False)

        mock_get_apps.assert_called_once()
        self.assertEqual(mock_is_dir.call_count, 2)
        mock_is_symlink.assert_called_once()
        mock_path_exists.assert_called_once()
        mock_shutil_move.assert_not_called()
        mock_shutil_rmtree.assert_called_once_with(app_ws_path, ignore_errors=True)

        msg_first_info = f'INFO: Moving workspace directories of apps to "{Path.home() / "foo" / "workspace"}" and linking back.'

        msg_warning = (
            'WARNING: Workspace directory for app "foo_app" already exists in the '
            "TETHYS_WORKSPACES_ROOT directory. A symbolic link is being created to the existing directory. "
            'To force overwrite the existing directory, re-run the command with the "-f" argument.'
        )
        msg_second_info = (
            'INFO: Successfully linked "workspaces" directory to '
            'TETHYS_WORKSPACES_ROOT for app "foo_app".'
        )

        print_call_args = mock_print.call_args_list

        self.assertEqual(msg_first_info, print_call_args[0][0][0])

        self.assertEqual(msg_warning, print_call_args[1][0][0])

        self.assertEqual(msg_second_info, print_call_args[2][0][0])

    @mock.patch("tethys_apps.management.commands.collectworkspaces.print")
    @mock.patch("tethys_apps.management.commands.pre_collectstatic.Path.unlink")
    @mock.patch("tethys_apps.management.commands.pre_collectstatic.shutil.rmtree")
    @mock.patch("tethys_apps.management.commands.pre_collectstatic.Path.symlink_to")
    @mock.patch("tethys_apps.management.commands.pre_collectstatic.shutil.move")
    @mock.patch("tethys_apps.management.commands.pre_collectstatic.Path.exists")
    @mock.patch("tethys_apps.management.commands.pre_collectstatic.Path.is_symlink")
    @mock.patch("tethys_apps.management.commands.pre_collectstatic.Path.is_dir")
    @mock.patch(
        "tethys_apps.management.commands.collectworkspaces.get_installed_tethys_items"
    )
    @mock.patch("tethys_apps.management.commands.collectworkspaces.settings")
    def test_collectworkspaces_handle_exists_force_exception(
        self,
        mock_settings,
        mock_get_apps,
        mock_is_dir,
        mock_is_symlink,
        mock_path_exists,
        mock_shutil_move,
        mock_symlink_to,
        mock_shutil_rmtree,
        mock_unlink,
        mock_print,
    ):
        app_name = "foo_app"
        app_path = Path.home() / "foo" / "testing" / "tests" / app_name
        app_ws_path = app_path / "workspaces"
        tethys_workspaces_root = Path.home() / "foo" / "workspace"
        app_workspaces_root = tethys_workspaces_root / app_name
        mock_settings.TETHYS_WORKSPACES_ROOT = tethys_workspaces_root
        mock_get_apps.return_value = {app_name: app_path}
        mock_is_dir.side_effect = [True, True]
        mock_is_symlink.return_value = False
        mock_path_exists.return_value = True
        mock_shutil_move.return_value = True
        mock_symlink_to.return_value = True
        mock_shutil_rmtree.return_value = True
        mock_unlink.side_effect = OSError

        cmd = collectworkspaces.Command()
        cmd.handle(force=True)

        mock_get_apps.assert_called_once()
        self.assertEqual(mock_is_dir.call_count, 2)
        mock_is_symlink.assert_called_once()
        mock_path_exists.assert_called_once()
        mock_shutil_move.assert_called_once_with(app_ws_path, app_workspaces_root)
        mock_shutil_rmtree.assert_called_once_with(
            app_workspaces_root, ignore_errors=True
        )
        mock_unlink.assert_called_once()

        msg_first_info = f'INFO: Moving workspace directories of apps to "{Path.home() / "foo" / "workspace"}" and linking back.'

        msg_second_info = (
            'INFO: Successfully linked "workspaces" directory to '
            'TETHYS_WORKSPACES_ROOT for app "foo_app".'
        )

        msg_warning = (
            'WARNING: Workspace directory for app "foo_app" already exists in the TETHYS_WORKSPACES_ROOT '
            "directory. A symbolic link is being created to the existing directory. To force overwrite "
            'the existing directory, re-run the command with the "-f" argument.'
        )

        print_call_args = mock_print.call_args_list

        self.assertEqual(msg_first_info, print_call_args[0][0][0])

        self.assertEqual(msg_second_info, print_call_args[1][0][0])

        for i in range(len(print_call_args)):
            self.assertNotEqual(msg_warning, print_call_args[i][0][0])
