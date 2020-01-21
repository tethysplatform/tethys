import unittest
from unittest import mock

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

        self.assertIn('[-f]', parser.format_usage())
        self.assertIn('--force', parser.format_help())
        self.assertIn('Force the overwrite the app directory', parser.format_help())

    @mock.patch('tethys_apps.management.commands.collectworkspaces.print')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.exit')
    @mock.patch('tethys_apps.management.commands.collectworkspaces.settings')
    def test_collectworkspaces_handle_no_atts(self, mock_settings, mock_exit, mock_print):
        mock_settings.TETHYS_WORKSPACES_ROOT = None
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        cmd = collectworkspaces.Command()
        self.assertRaises(SystemExit, cmd.handle)

        check_msg = 'WARNING: Cannot find the TETHYS_WORKSPACES_ROOT setting. ' \
                    'Please provide the path to the static directory using the TETHYS_WORKSPACES_ROOT ' \
                    'setting in the portal_config.yml file and try again.'

        mock_print.assert_called_with(check_msg)

    @mock.patch('tethys_apps.management.commands.collectworkspaces.print')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.shutil.move')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.makedirs')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.path.isdir')
    @mock.patch('tethys_apps.management.commands.collectworkspaces.get_installed_tethys_apps')
    @mock.patch('tethys_apps.management.commands.collectworkspaces.settings')
    def test_collectworkspaces_handle_no_force_not_dir(self, mock_settings, mock_get_apps, mock_os_path_isdir,
                                                       mock_os_makedirs, mock_shutil_move, mock_print):
        mock_settings.TETHYS_WORKSPACES_ROOT = '/foo/workspace'
        mock_get_apps.return_value = {'foo_app': '/foo/testing/tests/foo_app'}
        mock_os_path_isdir.return_value = False

        cmd = collectworkspaces.Command()
        cmd.handle(force=False)

        mock_get_apps.assert_called_once()
        mock_os_path_isdir.assert_called()
        mock_os_makedirs.assert_called_once_with('/foo/testing/tests/foo_app/workspaces', exist_ok=True)
        mock_shutil_move.assert_called_once_with('/foo/testing/tests/foo_app/workspaces', '/foo/workspace/foo_app')

        msg_info = 'INFO: Moving workspace directories of apps to "/foo/workspace" and linking back.'

        msg_warning = 'WARNING: The workspace_path for app "foo_app" is not a directory. Making workspace directory...'

        print_call_args = mock_print.call_args_list

        self.assertEqual(msg_info, print_call_args[0][0][0])

        self.assertEqual(msg_warning, print_call_args[1][0][0])

    @mock.patch('tethys_apps.management.commands.collectworkspaces.print')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.path.islink')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.path.isdir')
    @mock.patch('tethys_apps.management.commands.collectworkspaces.get_installed_tethys_apps')
    @mock.patch('tethys_apps.management.commands.collectworkspaces.settings')
    def test_collectworkspaces_handle_no_force_is_link(self, mock_settings, mock_get_apps, mock_os_path_isdir,
                                                       mock_os_path_islink, mock_print):
        mock_settings.TETHYS_WORKSPACES_ROOT = '/foo/workspace'
        mock_get_apps.return_value = {'foo_app': '/foo/testing/tests/foo_app'}
        mock_os_path_isdir.return_value = True
        mock_os_path_islink.return_value = True

        cmd = collectworkspaces.Command()
        cmd.handle(force=False)

        mock_get_apps.assert_called_once()
        mock_os_path_isdir.assert_called_once_with('/foo/testing/tests/foo_app/workspaces')
        mock_os_path_islink.assert_called_once_with('/foo/testing/tests/foo_app/workspaces')
        msg_in = 'INFO: Moving workspace directories of apps to "/foo/workspace" and linking back.'
        mock_print.assert_called_with(msg_in)

    @mock.patch('tethys_apps.management.commands.collectworkspaces.print')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.symlink')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.shutil.move')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.path.exists')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.path.islink')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.path.isdir')
    @mock.patch('tethys_apps.management.commands.collectworkspaces.get_installed_tethys_apps')
    @mock.patch('tethys_apps.management.commands.collectworkspaces.settings')
    def test_collectworkspaces_handle_not_exists(self, mock_settings, mock_get_apps, mock_os_path_isdir,
                                                 mock_os_path_islink, mock_os_path_exists, mock_shutil_move,
                                                 mock_os_symlink, mock_print):
        mock_settings.TETHYS_WORKSPACES_ROOT = '/foo/workspace'
        mock_get_apps.return_value = {'foo_app': '/foo/testing/tests/foo_app'}
        mock_os_path_isdir.side_effect = [True, True]
        mock_os_path_islink.return_value = False
        mock_os_path_exists.return_value = False
        mock_shutil_move.return_value = True
        mock_os_symlink.return_value = True

        cmd = collectworkspaces.Command()
        cmd.handle(force=True)

        mock_get_apps.assert_called_once()
        mock_os_path_isdir.assert_any_call('/foo/testing/tests/foo_app/workspaces')
        mock_os_path_isdir.assert_called_with('/foo/workspace/foo_app')
        mock_os_path_islink.assert_called_once_with('/foo/testing/tests/foo_app/workspaces')
        mock_os_path_exists.assert_called_once_with('/foo/workspace/foo_app')
        mock_shutil_move.assert_called_once_with('/foo/testing/tests/foo_app/workspaces', '/foo/workspace/foo_app')
        msg_first_info = 'INFO: Moving workspace directories of apps to "/foo/workspace" and linking back.'
        msg_second_info = 'INFO: Successfully linked "workspaces" directory to ' \
                          'TETHYS_WORKSPACES_ROOT for app "foo_app".'

        print_call_args = mock_print.call_args_list

        self.assertEqual(msg_first_info, print_call_args[0][0][0])

        self.assertEqual(msg_second_info, print_call_args[1][0][0])

    @mock.patch('tethys_apps.management.commands.collectworkspaces.print')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.shutil.rmtree')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.symlink')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.shutil.move')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.path.exists')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.path.islink')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.path.isdir')
    @mock.patch('tethys_apps.management.commands.collectworkspaces.get_installed_tethys_apps')
    @mock.patch('tethys_apps.management.commands.collectworkspaces.settings')
    def test_collectworkspaces_handle_exists_no_force(self, mock_settings, mock_get_apps, mock_os_path_isdir,
                                                      mock_os_path_islink, mock_os_path_exists, mock_shutil_move,
                                                      mock_os_symlink, mock_shutil_rmtree, mock_print):
        mock_settings.TETHYS_WORKSPACES_ROOT = '/foo/workspace'
        mock_get_apps.return_value = {'foo_app': '/foo/testing/tests/foo_app'}
        mock_os_path_isdir.side_effect = [True, True]
        mock_os_path_islink.return_value = False
        mock_os_path_exists.return_value = True
        mock_shutil_move.return_value = True
        mock_os_symlink.return_value = True
        mock_shutil_rmtree.return_value = True

        cmd = collectworkspaces.Command()
        cmd.handle(force=False)

        mock_get_apps.assert_called_once()
        mock_os_path_isdir.assert_any_call('/foo/testing/tests/foo_app/workspaces')
        mock_os_path_isdir.assert_called_with('/foo/workspace/foo_app')
        mock_os_path_islink.assert_called_once_with('/foo/testing/tests/foo_app/workspaces')
        mock_os_path_exists.assert_called_once_with('/foo/workspace/foo_app')
        mock_shutil_move.assert_not_called()
        mock_shutil_rmtree.called_once_with('/foo/workspace/foo_app', ignore_errors=True)

        msg_first_info = 'INFO: Moving workspace directories of apps to "/foo/workspace" and linking back.'

        msg_warning = 'WARNING: Workspace directory for app "foo_app" already exists in the ' \
                      'TETHYS_WORKSPACES_ROOT directory. A symbolic link is being created to the existing directory. ' \
                      'To force overwrite the existing directory, re-run the command with the "-f" argument.'
        msg_second_info = 'INFO: Successfully linked "workspaces" directory to ' \
                          'TETHYS_WORKSPACES_ROOT for app "foo_app".'

        print_call_args = mock_print.call_args_list

        self.assertEqual(msg_first_info, print_call_args[0][0][0])

        self.assertEqual(msg_warning, print_call_args[1][0][0])

        self.assertEqual(msg_second_info, print_call_args[2][0][0])

    @mock.patch('tethys_apps.management.commands.collectworkspaces.print')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.remove')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.shutil.rmtree')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.symlink')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.shutil.move')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.path.exists')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.path.islink')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.path.isdir')
    @mock.patch('tethys_apps.management.commands.collectworkspaces.get_installed_tethys_apps')
    @mock.patch('tethys_apps.management.commands.collectworkspaces.settings')
    def test_collectworkspaces_handle_exists_force_exception(self, mock_settings, mock_get_apps, mock_os_path_isdir,
                                                             mock_os_path_islink, mock_os_path_exists, mock_shutil_move,
                                                             mock_os_symlink, mock_shutil_rmtree, mock_os_remove,
                                                             mock_print):
        mock_settings.TETHYS_WORKSPACES_ROOT = '/foo/workspace'
        mock_get_apps.return_value = {'foo_app': '/foo/testing/tests/foo_app'}
        mock_os_path_isdir.side_effect = [True, True]
        mock_os_path_islink.return_value = False
        mock_os_path_exists.return_value = True
        mock_shutil_move.return_value = True
        mock_os_symlink.return_value = True
        mock_shutil_rmtree.return_value = True
        mock_os_remove.side_effect = OSError

        cmd = collectworkspaces.Command()
        cmd.handle(force=True)

        mock_get_apps.assert_called_once()
        mock_os_path_isdir.assert_any_call('/foo/testing/tests/foo_app/workspaces')
        mock_os_path_isdir.assert_called_with('/foo/workspace/foo_app')
        mock_os_path_islink.assert_called_once_with('/foo/testing/tests/foo_app/workspaces')
        mock_os_path_exists.assert_called_once_with('/foo/workspace/foo_app')
        mock_shutil_move.assert_called_once_with('/foo/testing/tests/foo_app/workspaces', '/foo/workspace/foo_app')
        mock_shutil_rmtree.called_once_with('/foo/testing/tests/foo_app/workspaces', ignore_errors=True)
        mock_os_remove.assert_called_once_with('/foo/workspace/foo_app')

        msg_first_info = 'INFO: Moving workspace directories of apps to "/foo/workspace" and linking back.'

        msg_second_info = 'INFO: Successfully linked "workspaces" directory to ' \
                          'TETHYS_WORKSPACES_ROOT for app "foo_app".'

        msg_warning = 'WARNING: Workspace directory for app "foo_app" already exists in the TETHYS_WORKSPACES_ROOT ' \
                      'directory. A symbolic link is being created to the existing directory. To force overwrite ' \
                      'the existing directory, re-run the command with the "-f" argument.'

        print_call_args = mock_print.call_args_list

        self.assertEqual(msg_first_info, print_call_args[0][0][0])

        self.assertEqual(msg_second_info, print_call_args[1][0][0])

        for i in range(len(print_call_args)):
            self.assertNotEqual(msg_warning, print_call_args[i][0][0])
