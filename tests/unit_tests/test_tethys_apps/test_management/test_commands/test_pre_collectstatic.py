import cStringIO
import unittest
import mock

from tethys_apps.management.commands import pre_collectstatic


class ManagementCommandsPreCollectStaticTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('sys.stdout', new_callable=cStringIO.StringIO)
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.exit')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.settings')
    def test_handle_no_static_root(self, mock_settings, mock_exit, mock_stdout):
        mock_settings.STATIC_ROOT = None
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        cmd = pre_collectstatic.Command()
        self.assertRaises(SystemExit, cmd.handle)

        self.assertIn('WARNING: Cannot find the STATIC_ROOT setting', mock_stdout.getvalue())
        self.assertIn('Please provide the path to the static directory', mock_stdout.getvalue())

    @mock.patch('sys.stdout', new_callable=cStringIO.StringIO)
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.symlink')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.path.isdir')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.remove')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.get_installed_tethys_extensions')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.get_installed_tethys_apps')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.settings')
    def test_handle_public_not_static(self, mock_settings, mock_get_apps, mock_get_extensions, mock_os_remove,
                                      mock_os_path_isdir, mock_os_symlink, mock_stdout):
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
        mock_os_remove.assert_called_with('/foo/testing/tests/foo_extension')
        mock_os_path_isdir.assert_any_call('/foo/testing/tests/foo_app/public')
        mock_os_path_isdir.assert_called_with('/foo/testing/tests/foo_extension/public')
        mock_os_symlink.assert_any_call('/foo/testing/tests/foo_app/public', '/foo/testing/tests/foo_app')
        mock_os_symlink.assert_called_with('/foo/testing/tests/foo_extension/public',
                                           '/foo/testing/tests/foo_extension')
        self.assertNotIn('WARNING: Cannot find the STATIC_ROOT setting', mock_stdout.getvalue())
        self.assertNotIn('Please provide the path to the static directory', mock_stdout.getvalue())
        self.assertIn('INFO: Linking static and public directories of apps and extensions to "{0}".'.
                      format(mock_settings.STATIC_ROOT), mock_stdout.getvalue())
        self.assertIn('INFO: Successfully linked public directory to STATIC_ROOT for app "foo_app".',
                      mock_stdout.getvalue())
        self.assertIn('INFO: Successfully linked public directory to STATIC_ROOT for app "foo_extension".',
                      mock_stdout.getvalue())
        self.assertNotIn('INFO: Successfully linked static directory to STATIC_ROOT for app "foo_app".',
                         mock_stdout.getvalue())
        self.assertNotIn('INFO: Successfully linked static directory to STATIC_ROOT for app "foo_extension".',
                         mock_stdout.getvalue())

    @mock.patch('sys.stdout', new_callable=cStringIO.StringIO)
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.symlink')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.path.isdir')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.shutil.rmtree')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.remove')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.get_installed_tethys_extensions')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.get_installed_tethys_apps')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.settings')
    def test_handle_public_not_static_Exceptions(self, mock_settings, mock_get_apps, mock_get_extensions,
                                                 mock_os_remove, mock_shutil_rmtree, mock_os_path_isdir,
                                                 mock_os_symlink, mock_stdout):
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
        mock_os_remove.assert_called_with('/foo/testing/tests/foo_extension')
        mock_shutil_rmtree.assert_any_call('/foo/testing/tests/foo_app')
        mock_shutil_rmtree.assert_called_with('/foo/testing/tests/foo_extension')
        mock_os_path_isdir.assert_any_call('/foo/testing/tests/foo_app/public')
        mock_os_path_isdir.assert_called_with('/foo/testing/tests/foo_extension/public')
        mock_os_symlink.assert_any_call('/foo/testing/tests/foo_app/public', '/foo/testing/tests/foo_app')
        mock_os_symlink.assert_called_with('/foo/testing/tests/foo_extension/public',
                                           '/foo/testing/tests/foo_extension')
        self.assertNotIn('WARNING: Cannot find the STATIC_ROOT setting', mock_stdout.getvalue())
        self.assertNotIn('Please provide the path to the static directory', mock_stdout.getvalue())
        self.assertIn('INFO: Linking static and public directories of apps and extensions to "{0}".'.
                      format(mock_settings.STATIC_ROOT), mock_stdout.getvalue())
        self.assertIn('INFO: Successfully linked public directory to STATIC_ROOT for app "foo_app".',
                      mock_stdout.getvalue())
        self.assertIn('INFO: Successfully linked public directory to STATIC_ROOT for app "foo_extension".',
                      mock_stdout.getvalue())
        self.assertNotIn('INFO: Successfully linked static directory to STATIC_ROOT for app "foo_app".',
                         mock_stdout.getvalue())
        self.assertNotIn('INFO: Successfully linked static directory to STATIC_ROOT for app "foo_extension".',
                         mock_stdout.getvalue())

    @mock.patch('sys.stdout', new_callable=cStringIO.StringIO)
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.symlink')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.path.isdir')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.remove')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.get_installed_tethys_extensions')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.get_installed_tethys_apps')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.settings')
    def test_handle_not_public_static(self, mock_settings, mock_get_apps, mock_get_extensions, mock_os_remove,
                                      mock_os_path_isdir, mock_os_symlink, mock_stdout):
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
        mock_os_remove.assert_called_with('/foo/testing/tests/foo_extension')
        mock_os_path_isdir.assert_any_call('/foo/testing/tests/foo_app/static')
        mock_os_path_isdir.assert_called_with('/foo/testing/tests/foo_extension/static')
        mock_os_symlink.assert_any_call('/foo/testing/tests/foo_app/static', '/foo/testing/tests/foo_app')
        mock_os_symlink.assert_called_with('/foo/testing/tests/foo_extension/static',
                                           '/foo/testing/tests/foo_extension')
        self.assertNotIn('WARNING: Cannot find the STATIC_ROOT setting', mock_stdout.getvalue())
        self.assertNotIn('Please provide the path to the static directory', mock_stdout.getvalue())
        self.assertIn('INFO: Linking static and public directories of apps and extensions to "{0}".'.
                      format(mock_settings.STATIC_ROOT), mock_stdout.getvalue())
        self.assertNotIn('INFO: Successfully linked public directory to STATIC_ROOT for app "foo_app".',
                         mock_stdout.getvalue())
        self.assertNotIn('INFO: Successfully linked public directory to STATIC_ROOT for app "foo_extension".',
                         mock_stdout.getvalue())
        self.assertIn('INFO: Successfully linked static directory to STATIC_ROOT for app "foo_app".',
                      mock_stdout.getvalue())
        self.assertIn('INFO: Successfully linked static directory to STATIC_ROOT for app "foo_extension".',
                      mock_stdout.getvalue())

    @mock.patch('sys.stdout', new_callable=cStringIO.StringIO)
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.symlink')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.path.isdir')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.os.remove')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.get_installed_tethys_extensions')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.get_installed_tethys_apps')
    @mock.patch('tethys_apps.management.commands.pre_collectstatic.settings')
    def test_handle_not_public_not_static(self, mock_settings, mock_get_apps, mock_get_extensions, mock_os_remove,
                                          mock_os_path_isdir, mock_os_symlink, mock_stdout):
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
        mock_os_remove.assert_called_with('/foo/testing/tests/foo_extension')
        mock_os_path_isdir.assert_any_call('/foo/testing/tests/foo_app/static')
        mock_os_path_isdir.assert_called_with('/foo/testing/tests/foo_extension/static')
        mock_os_symlink.assert_not_called()
        self.assertNotIn('WARNING: Cannot find the STATIC_ROOT setting', mock_stdout.getvalue())
        self.assertNotIn('Please provide the path to the static directory', mock_stdout.getvalue())
        self.assertIn('INFO: Linking static and public directories of apps and extensions to "{0}".'.
                      format(mock_settings.STATIC_ROOT), mock_stdout.getvalue())
        self.assertNotIn('INFO: Successfully linked public directory to STATIC_ROOT for app "foo_app".',
                         mock_stdout.getvalue())
        self.assertNotIn('INFO: Successfully linked public directory to STATIC_ROOT for app "foo_extension".',
                         mock_stdout.getvalue())
        self.assertNotIn('INFO: Successfully linked static directory to STATIC_ROOT for app "foo_app".',
                         mock_stdout.getvalue())
        self.assertNotIn('INFO: Successfully linked static directory to STATIC_ROOT for app "foo_extension".',
                         mock_stdout.getvalue())
