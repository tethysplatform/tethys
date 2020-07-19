import unittest
from unittest import mock

from tethys_apps.management.commands import pre_collectstatic


class ManagementCommandsPreCollectStaticTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_add_arguments(self):
        mock_parser = mock.MagicMock()

        cmd = pre_collectstatic.Command()
        cmd.add_arguments(mock_parser)

        add_arguments_calls = mock_parser.add_argument.call_args_list

        self.assertEqual(1, len(add_arguments_calls))
        self.assertIn('-l', add_arguments_calls[0][0])
        self.assertIn('--link', add_arguments_calls[0][0])

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

        msg_warning = 'WARNING: Cannot find the STATIC_ROOT setting. Please provide the ' \
                      'path to the static directory using the STATIC_ROOT setting in the portal_config.yml ' \
                      'file and try again.'
        self.assertEqual(msg_warning, print_args[0][0][0])

    @mock.patch('tethys_apps.management.commands.pre_collectstatic.print')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.shutil.copytree')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.path.isdir')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.remove')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.get_installed_tethys_extensions')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.get_installed_tethys_apps')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.settings')
    def test_handle__not_named_static_or_public(self, mock_settings, mock_get_apps, mock_get_extensions, mock_os_remove,
                                                mock_os_path_isdir, mock_shutil_copytree, mock_print):

        options = {'link': False}  # Don't create symbolic link (copy instead)
        static_root_dir = '/foo/static/root'
        app_source_dir = '/foo/sources/foo_app'
        ext_source_dir = '/foo/sources/foo_ext'
        app_public_dir = app_source_dir + '/public'
        ext_public_dir = ext_source_dir + '/public'
        app_static_dir = app_source_dir + '/static'
        ext_static_dir = ext_source_dir + '/static'

        mock_settings.STATIC_ROOT = static_root_dir
        mock_get_apps.return_value = {'foo_app': app_source_dir}
        mock_get_extensions.return_value = {'foo_ext': ext_source_dir}
        mock_os_remove.return_value = True  # Successfully remove old link or dir with os.remove
        mock_os_path_isdir.side_effect = (False, False, False, False)  # "public" and "static" path don't exist

        cmd = pre_collectstatic.Command()
        cmd.handle(**options)

        # Verify apps and extensions were gathered
        mock_get_apps.assert_called_once()
        mock_get_extensions.assert_called_once()

        # Verify check for public dir was performed for app and extension
        mock_os_path_isdir.assert_any_call(app_public_dir)
        mock_os_path_isdir.assert_any_call(ext_public_dir)
        mock_os_path_isdir.assert_any_call(app_static_dir)
        mock_os_path_isdir.assert_any_call(ext_static_dir)

        # Verify attempt to remove old dirs/links
        mock_os_remove.assert_not_called()

        # Verify attempt to copy public dir to static root location
        mock_shutil_copytree.assert_not_called()

        # Verify messages
        print_args = mock_print.call_args_list

        msg = 'INFO: Collecting static and public directories of apps and extensions to "{0}".' \
            .format(mock_settings.STATIC_ROOT)

        msg_info_first = 'WARNING: Cannot find a directory named "static" or "public" for app "foo_app". Skipping...'

        msg_info_second = 'WARNING: Cannot find a directory named "static" or "public" for app "foo_ext". Skipping...'

        check_list = []
        for i in range(len(print_args)):
            check_list.append(print_args[i][0][0])

        self.assertIn(msg, check_list)
        self.assertIn(msg_info_first, check_list)
        self.assertIn(msg_info_second, check_list)

        msg_warning_not_in = 'WARNING: Cannot find the STATIC_ROOT setting'
        msg_not_in = 'Please provide the path to the static directory'
        info_not_in_first = 'INFO: Successfully copied static directory to STATIC_ROOT for app "foo_app".'
        info_not_in_second = 'INFO: Successfully copied static directory to STATIC_ROOT for app "foo_ext".'

        for i in range(len(print_args)):
            self.assertNotEqual(msg_warning_not_in, print_args[i][0][0])
            self.assertNotEqual(msg_not_in, print_args[i][0][0])
            self.assertNotEqual(info_not_in_first, print_args[i][0][0])
            self.assertNotEqual(info_not_in_second, print_args[i][0][0])

    @mock.patch('tethys_apps.management.commands.pre_collectstatic.print')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.shutil.copytree')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.path.isdir')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.shutil.rmtree')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.remove')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.get_installed_tethys_extensions')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.get_installed_tethys_apps')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.settings')
    def test_handle__public__remove_fail__rmtree_fail(self, mock_settings, mock_get_apps, mock_get_extensions,
                                                      mock_os_remove, mock_shutil_rmtree, mock_os_path_isdir,
                                                      mock_shutil_copytree, mock_print):

        options = {'link': False}  # Don't create symbolic link (copy instead)
        static_root_dir = '/foo/static/root'
        app_source_dir = '/foo/sources/foo_app'
        ext_source_dir = '/foo/sources/foo_ext'
        app_public_dir = app_source_dir + '/public'
        ext_public_dir = ext_source_dir + '/public'
        app_static_root_dir = static_root_dir + '/foo_app'
        ext_static_root_dir = static_root_dir + '/foo_ext'

        mock_settings.STATIC_ROOT = static_root_dir
        mock_get_apps.return_value = {'foo_app': app_source_dir}
        mock_get_extensions.return_value = {'foo_ext': ext_source_dir}
        mock_os_remove.side_effect = OSError  # remove fails
        mock_shutil_rmtree.side_effect = OSError  # rmtree fails
        mock_os_path_isdir.side_effect = (True, True)  # "public" dir found

        cmd = pre_collectstatic.Command()
        cmd.handle(**options)

        # Verify apps and extensions were gathered
        mock_get_apps.assert_called_once()
        mock_get_extensions.assert_called_once()

        # Verify check for public dir was performed for app and extension
        mock_os_path_isdir.assert_any_call(app_public_dir)
        mock_os_path_isdir.assert_any_call(ext_public_dir)

        # Verify attempt to remove old dirs/links
        mock_os_remove.assert_any_call(app_static_root_dir)
        mock_os_remove.assert_any_call(ext_static_root_dir)
        mock_shutil_rmtree.assert_any_call(app_static_root_dir)
        mock_shutil_rmtree.assert_any_call(ext_static_root_dir)

        # Verify attempt to copy public dir to static root location
        mock_shutil_copytree.assert_any_call(app_public_dir, app_static_root_dir)
        mock_shutil_copytree.assert_any_call(ext_public_dir, ext_static_root_dir)

        # Verify messages
        print_args = mock_print.call_args_list

        msg = 'INFO: Collecting static and public directories of apps and extensions to "{0}".' \
            .format(mock_settings.STATIC_ROOT)

        msg_info_first = 'INFO: Successfully copied public directory to STATIC_ROOT for app "foo_app".'

        msg_info_second = 'INFO: Successfully copied public directory to STATIC_ROOT for app "foo_ext".'

        check_list = []
        for i in range(len(print_args)):
            check_list.append(print_args[i][0][0])

        self.assertIn(msg, check_list)
        self.assertIn(msg_info_first, check_list)
        self.assertIn(msg_info_second, check_list)

        msg_warning_not_in = 'WARNING: Cannot find the STATIC_ROOT setting'
        msg_not_in = 'Please provide the path to the static directory'
        info_not_in_first = 'INFO: Successfully linked static directory to STATIC_ROOT for app "foo_app".'
        info_not_in_second = 'INFO: Successfully linked static directory to STATIC_ROOT for app "foo_ext".'

        for i in range(len(print_args)):
            self.assertNotEqual(msg_warning_not_in, print_args[i][0][0])
            self.assertNotEqual(msg_not_in, print_args[i][0][0])
            self.assertNotEqual(info_not_in_first, print_args[i][0][0])
            self.assertNotEqual(info_not_in_second, print_args[i][0][0])

    @mock.patch('tethys_apps.management.commands.pre_collectstatic.print')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.shutil.copytree')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.path.isdir')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.remove')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.get_installed_tethys_extensions')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.get_installed_tethys_apps')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.settings')
    def test_handle__named_public__copy(self, mock_settings, mock_get_apps, mock_get_extensions, mock_os_remove,
                                        mock_os_path_isdir, mock_shutil_copytree, mock_print):
        options = {'link': False}  # Don't create symbolic link (copy instead)
        static_root_dir = '/foo/static/root'
        app_source_dir = '/foo/sources/foo_app'
        app_public_dir = app_source_dir + '/public'
        ext_source_dir = '/foo/sources/foo_ext'
        ext_public_dir = ext_source_dir + '/public'
        app_static_root_dir = static_root_dir + '/foo_app'
        ext_static_root_dir = static_root_dir + '/foo_ext'

        mock_settings.STATIC_ROOT = static_root_dir
        mock_get_apps.return_value = {'foo_app': app_source_dir}
        mock_get_extensions.return_value = {'foo_ext': ext_source_dir}
        mock_os_remove.return_value = True  # Successfully remove old link or dir with os.remove
        mock_os_path_isdir.side_effect = (True, True)  # "public" test path exists

        cmd = pre_collectstatic.Command()
        cmd.handle(**options)

        # Verify apps and extensions were gathered
        mock_get_apps.assert_called_once()
        mock_get_extensions.assert_called_once()

        # Verify check for public dir was performed for app and extension
        mock_os_path_isdir.assert_any_call(app_public_dir)
        mock_os_path_isdir.assert_any_call(ext_public_dir)

        # Verify attempt to remove old dirs/links
        mock_os_remove.assert_any_call(app_static_root_dir)
        mock_os_remove.assert_any_call(ext_static_root_dir)

        # Verify attempt to copy public dir to static root location
        mock_shutil_copytree.assert_any_call(app_public_dir, app_static_root_dir)
        mock_shutil_copytree.assert_any_call(ext_public_dir, ext_static_root_dir)

        # Verify messages
        print_args = mock_print.call_args_list

        msg = 'INFO: Collecting static and public directories of apps and extensions to "{0}".'\
            . format(mock_settings.STATIC_ROOT)

        msg_info_first = 'INFO: Successfully copied public directory to STATIC_ROOT for app "foo_app".'

        msg_info_second = 'INFO: Successfully copied public directory to STATIC_ROOT for app "foo_ext".'

        check_list = []
        for i in range(len(print_args)):
            check_list.append(print_args[i][0][0])

        self.assertIn(msg, check_list)
        self.assertIn(msg_info_first, check_list)
        self.assertIn(msg_info_second, check_list)

        msg_warning_not_in = 'WARNING: Cannot find the STATIC_ROOT setting'
        msg_not_in = 'Please provide the path to the static directory'
        info_not_in_first = 'INFO: Successfully linked static directory to STATIC_ROOT for app "foo_app".'
        info_not_in_second = 'INFO: Successfully linked static directory to STATIC_ROOT for app "foo_ext".'

        for i in range(len(print_args)):
            self.assertNotEqual(msg_warning_not_in, print_args[i][0][0])
            self.assertNotEqual(msg_not_in, print_args[i][0][0])
            self.assertNotEqual(info_not_in_first, print_args[i][0][0])
            self.assertNotEqual(info_not_in_second, print_args[i][0][0])

    @mock.patch('tethys_apps.management.commands.pre_collectstatic.print')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.symlink')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.path.isdir')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.remove')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.get_installed_tethys_extensions')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.get_installed_tethys_apps')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.settings')
    def test_handle__named_static__link(self, mock_settings, mock_get_apps, mock_get_extensions, mock_os_remove,
                                        mock_os_path_isdir, mock_os_symlink, mock_print):
        options = {'link': True}  # Create symbolic link (instead of copy)
        static_root_dir = '/foo/static/root'
        app_source_dir = '/foo/sources/foo_app'
        ext_source_dir = '/foo/sources/foo_ext'
        app_static_root_dir = static_root_dir + '/foo_app'
        ext_static_root_dir = static_root_dir + '/foo_ext'
        app_public_dir = app_source_dir + '/public'
        ext_public_dir = ext_source_dir + '/public'
        app_static_dir = app_source_dir + '/static'
        ext_static_dir = ext_source_dir + '/static'

        mock_settings.STATIC_ROOT = static_root_dir
        mock_get_apps.return_value = {'foo_app': app_source_dir}
        mock_get_extensions.return_value = {'foo_ext': ext_source_dir}
        mock_os_remove.return_value = True  # Successfully remove old link or dir with os.remove
        mock_os_path_isdir.side_effect = (False, True, False, True)  # "public" path doesn't exist, "static" path does

        cmd = pre_collectstatic.Command()
        cmd.handle(**options)

        # Verify apps and extensions were gathered
        mock_get_apps.assert_called_once()
        mock_get_extensions.assert_called_once()

        # Verify check for public dir was performed for app and extension
        mock_os_path_isdir.assert_any_call(app_public_dir)
        mock_os_path_isdir.assert_any_call(ext_public_dir)
        mock_os_path_isdir.assert_any_call(app_static_dir)
        mock_os_path_isdir.assert_any_call(ext_static_dir)

        # Verify attempt to remove old dirs/links
        mock_os_remove.assert_any_call(app_static_root_dir)
        mock_os_remove.assert_any_call(ext_static_root_dir)

        # Verify attempt to copy public dir to static root location
        mock_os_symlink.assert_any_call(app_static_dir, app_static_root_dir)
        mock_os_symlink.assert_any_call(ext_static_dir, ext_static_root_dir)

        # Verify messages
        print_args = mock_print.call_args_list

        msg = 'INFO: Collecting static and public directories of apps and extensions to "{0}".' \
            .format(mock_settings.STATIC_ROOT)

        msg_info_first = 'INFO: Successfully linked public directory to STATIC_ROOT for app "foo_app".'

        msg_info_second = 'INFO: Successfully linked public directory to STATIC_ROOT for app "foo_ext".'

        check_list = []
        for i in range(len(print_args)):
            check_list.append(print_args[i][0][0])

        self.assertIn(msg, check_list)
        self.assertIn(msg_info_first, check_list)
        self.assertIn(msg_info_second, check_list)

        msg_warning_not_in = 'WARNING: Cannot find the STATIC_ROOT setting'
        msg_not_in = 'Please provide the path to the static directory'
        info_not_in_first = 'INFO: Successfully copied static directory to STATIC_ROOT for app "foo_app".'
        info_not_in_second = 'INFO: Successfully copied static directory to STATIC_ROOT for app "foo_ext".'

        for i in range(len(print_args)):
            self.assertNotEqual(msg_warning_not_in, print_args[i][0][0])
            self.assertNotEqual(msg_not_in, print_args[i][0][0])
            self.assertNotEqual(info_not_in_first, print_args[i][0][0])
            self.assertNotEqual(info_not_in_second, print_args[i][0][0])
