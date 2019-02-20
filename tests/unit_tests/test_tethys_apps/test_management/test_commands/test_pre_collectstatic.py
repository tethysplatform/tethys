import unittest
from unittest import mock

from tethys_apps.management.commands import pre_collectstatic


class ManagementCommandsPreCollectStaticTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('tethys_apps.management.commands.pre_collectstatic.print')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.exit')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.settings')
    def test_handle_no_static_root(self, mock_settings, mock_exit, mock_print):
        mock_settings.STATIC_ROOT = None
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        cmd = pre_collectstatic.Command()
        self.assertRaises(SystemExit, cmd.handle)

        print_args = mock_print.call_args_list

        msg_warning = 'WARNING: Cannot find the STATIC_ROOT setting in the settings.py file. Please provide the ' \
                      'path to the static directory using the STATIC_ROOT setting and try again.'
        self.assertEqual(msg_warning, print_args[0][0][0])

    @mock.patch('tethys_apps.management.commands.pre_collectstatic.print')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.symlink')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.path.isdir')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.remove')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.get_installed_tethys_extensions')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.get_installed_tethys_apps')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.settings')
    def test_handle_public_not_static(self, mock_settings, mock_get_apps, mock_get_extensions, mock_os_remove,
                                      mock_os_path_isdir, mock_os_symlink, mock_print):
        mock_settings.STATIC_ROOT = '/foo/testing/tests'
        mock_get_apps.return_value = {'foo_app': '/foo/testing/tests/foo_app'}
        mock_get_extensions.return_value = {'foo_extension': '/foo/testing/tests/foo_extension'}
        mock_os_remove.return_value = True
        mock_os_path_isdir.return_value = True
        mock_os_symlink.return_value = True

        cmd = pre_collectstatic.Command()
        cmd.handle(options='foo')

        mock_get_apps.assert_called_once()
        mock_get_extensions.assert_called_once()
        mock_os_remove.assert_any_call('/foo/testing/tests/foo_app')
        mock_os_remove.assert_any_call('/foo/testing/tests/foo_extension')
        mock_os_path_isdir.assert_any_call('/foo/testing/tests/foo_app/public')
        mock_os_path_isdir.assert_any_call('/foo/testing/tests/foo_extension/public')
        mock_os_symlink.assert_any_call('/foo/testing/tests/foo_app/public', '/foo/testing/tests/foo_app')
        mock_os_symlink.assert_any_call('/foo/testing/tests/foo_extension/public',
                                        '/foo/testing/tests/foo_extension')
        print_args = mock_print.call_args_list

        msg = 'INFO: Linking static and public directories of apps and extensions to "{0}".'\
            . format(mock_settings.STATIC_ROOT)

        msg_info_first = 'INFO: Successfully linked public directory to STATIC_ROOT for app "foo_app".'

        msg_info_second = 'INFO: Successfully linked public directory to STATIC_ROOT for app "foo_extension".'

        check_list = []
        for i in range(len(print_args)):
            check_list.append(print_args[i][0][0])

        self.assertIn(msg, check_list)
        self.assertIn(msg_info_first, check_list)
        self.assertIn(msg_info_second, check_list)

        msg_warning_not_in = 'WARNING: Cannot find the STATIC_ROOT setting'
        msg_not_in = 'Please provide the path to the static directory'
        info_not_in_first = 'INFO: Successfully linked static directory to STATIC_ROOT for app "foo_app".'
        info_not_in_second = 'INFO: Successfully linked static directory to STATIC_ROOT for app "foo_extension".'

        for i in range(len(print_args)):
            self.assertNotEquals(msg_warning_not_in, print_args[i][0][0])
            self.assertNotEquals(msg_not_in, print_args[i][0][0])
            self.assertNotEquals(info_not_in_first, print_args[i][0][0])
            self.assertNotEquals(info_not_in_second, print_args[i][0][0])

    @mock.patch('tethys_apps.management.commands.pre_collectstatic.print')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.symlink')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.path.isdir')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.shutil.rmtree')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.remove')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.get_installed_tethys_extensions')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.get_installed_tethys_apps')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.settings')
    def test_handle_public_not_static_Exceptions(self, mock_settings, mock_get_apps, mock_get_extensions,
                                                 mock_os_remove, mock_shutil_rmtree, mock_os_path_isdir,
                                                 mock_os_symlink, mock_print):
        mock_settings.STATIC_ROOT = '/foo/testing/tests'
        mock_get_apps.return_value = {'foo_app': '/foo/testing/tests/foo_app'}
        mock_get_extensions.return_value = {'foo_extension': '/foo/testing/tests/foo_extension'}
        mock_os_remove.side_effect = OSError
        mock_shutil_rmtree.side_effect = OSError
        mock_os_path_isdir.return_value = True
        mock_os_symlink.return_value = True

        cmd = pre_collectstatic.Command()
        cmd.handle(options='foo')

        mock_get_apps.assert_called_once()
        mock_get_extensions.assert_called_once()
        mock_os_remove.assert_any_call('/foo/testing/tests/foo_app')
        mock_os_remove.assert_any_call('/foo/testing/tests/foo_extension')
        mock_shutil_rmtree.assert_any_call('/foo/testing/tests/foo_app')
        mock_shutil_rmtree.assert_any_call('/foo/testing/tests/foo_extension')
        mock_os_path_isdir.assert_any_call('/foo/testing/tests/foo_app/public')
        mock_os_path_isdir.assert_any_call('/foo/testing/tests/foo_extension/public')
        mock_os_symlink.assert_any_call('/foo/testing/tests/foo_app/public', '/foo/testing/tests/foo_app')
        mock_os_symlink.assert_any_call('/foo/testing/tests/foo_extension/public',
                                        '/foo/testing/tests/foo_extension')
        msg_infor_1 = 'INFO: Linking static and public directories of apps and extensions to "{0}".'\
            .format(mock_settings.STATIC_ROOT)
        msg_infor_2 = 'INFO: Successfully linked public directory to STATIC_ROOT for app "foo_app".'
        msg_infor_3 = 'INFO: Successfully linked public directory to STATIC_ROOT for app "foo_extension".'

        warn_not_in = 'WARNING: Cannot find the STATIC_ROOT setting'
        msg_not_in = 'Please provide the path to the static directory'
        info_not_in_first = 'INFO: Successfully linked static directory to STATIC_ROOT for app "foo_app".'
        info_not_in_second = 'INFO: Successfully linked static directory to STATIC_ROOT for app "foo_extension".'

        print_args = mock_print.call_args_list

        check_list = []
        for i in range(len(print_args)):
            check_list.append(print_args[i][0][0])

        self.assertIn(msg_infor_1, check_list)
        self.assertIn(msg_infor_2, check_list)
        self.assertIn(msg_infor_3, check_list)

        for i in range(len(print_args)):
            self.assertNotEquals(warn_not_in, print_args[i][0][0])
            self.assertNotEquals(msg_not_in, print_args[i][0][0])
            self.assertNotEquals(info_not_in_first, print_args[i][0][0])
            self.assertNotEquals(info_not_in_second, print_args[i][0][0])

    @mock.patch('tethys_apps.management.commands.pre_collectstatic.print')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.symlink')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.path.isdir')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.remove')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.get_installed_tethys_extensions')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.get_installed_tethys_apps')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.settings')
    def test_handle_not_public_static(self, mock_settings, mock_get_apps, mock_get_extensions, mock_os_remove,
                                      mock_os_path_isdir, mock_os_symlink, mock_print):
        mock_settings.STATIC_ROOT = '/foo/testing/tests'
        mock_get_apps.return_value = {'foo_app': '/foo/testing/tests/foo_app'}
        mock_get_extensions.return_value = {'foo_extension': '/foo/testing/tests/foo_extension'}
        mock_os_remove.return_value = True
        mock_os_path_isdir.side_effect = [False, True, False, True]
        mock_os_symlink.return_value = True

        cmd = pre_collectstatic.Command()
        cmd.handle(options='foo')

        mock_get_apps.assert_called_once()
        mock_get_extensions.assert_called_once()
        mock_os_remove.assert_any_call('/foo/testing/tests/foo_app')
        mock_os_remove.assert_any_call('/foo/testing/tests/foo_extension')
        mock_os_path_isdir.assert_any_call('/foo/testing/tests/foo_app/static')
        mock_os_path_isdir.assert_any_call('/foo/testing/tests/foo_extension/static')
        mock_os_symlink.assert_any_call('/foo/testing/tests/foo_app/static', '/foo/testing/tests/foo_app')
        mock_os_symlink.assert_any_call('/foo/testing/tests/foo_extension/static',
                                        '/foo/testing/tests/foo_extension')

        msg_info_one = 'INFO: Linking static and public directories of apps and extensions to "{0}".'\
            .format(mock_settings.STATIC_ROOT)
        msg_info_two = 'INFO: Successfully linked static directory to STATIC_ROOT for app "foo_app".'
        msg_info_three = 'INFO: Successfully linked static directory to STATIC_ROOT for app "foo_extension".'

        warn_not_in = 'WARNING: Cannot find the STATIC_ROOT setting'
        msg_not_in = 'Please provide the path to the static directory'
        info_not_in_first = 'INFO: Successfully linked public directory to STATIC_ROOT for app "foo_app".'
        info_not_in_second = 'INFO: Successfully linked public directory to STATIC_ROOT for app "foo_extension".'

        print_args = mock_print.call_args_list

        check_list = []
        for i in range(len(print_args)):
            check_list.append(print_args[i][0][0])

        self.assertIn(msg_info_one, check_list)
        self.assertIn(msg_info_two, check_list)
        self.assertIn(msg_info_three, check_list)

        for i in range(len(print_args)):
            self.assertNotEquals(warn_not_in, print_args[i][0][0])
            self.assertNotEquals(msg_not_in, print_args[i][0][0])
            self.assertNotEquals(info_not_in_first, print_args[i][0][0])
            self.assertNotEquals(info_not_in_second, print_args[i][0][0])

    @mock.patch('tethys_apps.management.commands.pre_collectstatic.print')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.symlink')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.path.isdir')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.remove')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.get_installed_tethys_extensions')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.get_installed_tethys_apps')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.settings')
    def test_handle_not_public_not_static(self, mock_settings, mock_get_apps, mock_get_extensions, mock_os_remove,
                                          mock_os_path_isdir, mock_os_symlink, mock_print):
        mock_settings.STATIC_ROOT = '/foo/testing/tests'
        mock_get_apps.return_value = {'foo_app': '/foo/testing/tests/foo_app'}
        mock_get_extensions.return_value = {'foo_extension': '/foo/testing/tests/foo_extension'}
        mock_os_remove.return_value = True
        mock_os_path_isdir.side_effect = [False, False, False, False]
        mock_os_symlink.return_value = True

        cmd = pre_collectstatic.Command()
        cmd.handle(options='foo')

        mock_get_apps.assert_called_once()
        mock_get_extensions.assert_called_once()
        mock_os_remove.assert_any_call('/foo/testing/tests/foo_app')
        mock_os_remove.assert_any_call('/foo/testing/tests/foo_extension')
        mock_os_path_isdir.assert_any_call('/foo/testing/tests/foo_app/static')
        mock_os_path_isdir.assert_any_call('/foo/testing/tests/foo_extension/static')
        mock_os_symlink.assert_not_called()
        msg_info = 'INFO: Linking static and public directories of apps and extensions to "{0}".'\
            .format(mock_settings.STATIC_ROOT)

        warn_not_in = 'WARNING: Cannot find the STATIC_ROOT setting'
        msg_not_in = 'Please provide the path to the static directory'
        info_not_in_first = 'INFO: Successfully linked public directory to STATIC_ROOT for app "foo_app".'
        info_not_in_second = 'INFO: Successfully linked public directory to STATIC_ROOT for app "foo_extension".'
        info_not_in_third = 'INFO: Successfully linked static directory to STATIC_ROOT for app "foo_app".'
        info_not_in_fourth = 'INFO: Successfully linked static directory to STATIC_ROOT for app "foo_extension".'

        print_args = mock_print.call_args_list
        self.assertEqual(msg_info, print_args[0][0][0])

        for i in range(len(print_args)):
            self.assertNotEquals(warn_not_in, print_args[i][0][0])
            self.assertNotEquals(msg_not_in, print_args[i][0][0])
            self.assertNotEquals(info_not_in_first, print_args[i][0][0])
            self.assertNotEquals(info_not_in_second, print_args[i][0][0])
            self.assertNotEquals(info_not_in_third, print_args[i][0][0])
            self.assertNotEquals(info_not_in_fourth, print_args[i][0][0])
