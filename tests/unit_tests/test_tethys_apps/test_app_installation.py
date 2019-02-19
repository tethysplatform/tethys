import unittest
import mock
import os
import sys
import tethys_apps.app_installation as tethys_app_installation

if sys.version_info[0] < 3:
    callable_mock_path = '__builtin__.callable'
else:
    callable_mock_path = 'builtins.callable'


class TestAppInstallation(unittest.TestCase):
    def setUp(self):
        self.src_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.root = os.path.join(self.src_dir, 'tethys_apps', 'tethysapp', 'test_app', 'public')

    def tearDown(self):
        pass

    def test_find_resource_files(self):
        ret = tethys_app_installation.find_resource_files(self.root)
        main_js = False
        icon_gif = False
        main_css = False
        if any('/js/main.js' in s for s in ret):
            main_js = True
        if any('/images/icon.gif' in s for s in ret):
            icon_gif = True
        if any('/css/main.css' in s for s in ret):
            main_css = True

        self.assertTrue(main_js)
        self.assertTrue(icon_gif)
        self.assertTrue(main_css)

    def test_get_tethysapp_directory(self):
        ret = tethys_app_installation.get_tethysapp_directory()
        self.assertIn('tethys_apps/tethysapp', ret)

    @mock.patch('tethys_apps.app_installation.install')
    @mock.patch('tethys_apps.app_installation.subprocess')
    @mock.patch('tethys_apps.app_installation.get_tethysapp_directory')
    @mock.patch('tethys_apps.app_installation.shutil')
    @mock.patch('tethys_apps.app_installation.pretty_output')
    @mock.patch('tethys_apps.app_installation.os.path.join')
    def test__run_install(self, mock_os_path_join, mock_pretty_output, mock_shutil, mock_getdir,
                          mock_subprocess, mock_install):
        # mock the self input
        mock_self = mock.MagicMock(app_package='tethys_apps', app_package_dir='/test_app/', dependencies=['foo'])

        # call the method for testing
        tethys_app_installation._run_install(self=mock_self)

        # check the method call
        mock_getdir.assert_called()

        # check the user notification
        mock_pretty_output.assert_called()

        # check the input arguments for shutil.copytree method
        shutil_call_args = mock_shutil.copytree.call_args_list
        self.assertEquals('/test_app/', shutil_call_args[0][0][0])

        # check the input arguments for subprocess.call method
        process_call_args = mock_subprocess.call.call_args_list
        self.assertEquals('pip', process_call_args[0][0][0][0])
        self.assertEquals('install', process_call_args[0][0][0][1])
        self.assertEquals('foo', process_call_args[0][0][0][2])

        # check the install call
        mock_install.run.assert_called_with(mock_self)
        mock_os_path_join.assert_called()

    @mock.patch('tethys_apps.app_installation.develop')
    @mock.patch('tethys_apps.app_installation.subprocess')
    @mock.patch('tethys_apps.app_installation.os')
    @mock.patch(callable_mock_path)
    @mock.patch('tethys_apps.app_installation.pretty_output')
    @mock.patch('tethys_apps.app_installation.get_tethysapp_directory')
    def test__run_develop(self, mock_getdir, mock_pretty_output, mock_callable, mock_os, mock_subprocess,
                          mock_develop):

        # mock the self input
        mock_self = mock.MagicMock(app_package='tethys_apps', app_package_dir='/test_app/', dependencies=['foo'])

        # call the method for testing
        tethys_app_installation._run_develop(self=mock_self)

        # check the method call
        mock_getdir.assert_called()

        # check the user notification
        mock_pretty_output.assert_called()

        # mock callable method
        mock_callable.return_value = True

        # check the input arguments for os.symlink method
        symlink_call_args = mock_os.symlink.call_args_list
        self.assertEquals('/test_app/', symlink_call_args[0][0][0])

        # check the input arguments for subprocess.call method
        process_call_args = mock_subprocess.call.call_args_list
        self.assertEquals('pip', process_call_args[0][0][0][0])
        self.assertEquals('install', process_call_args[0][0][0][1])
        self.assertEquals('foo', process_call_args[0][0][0][2])

        # check the develop call
        mock_develop.run.assert_called_with(mock_self)

    def test_custom_install_command(self):
        app_package = 'tethys_apps'
        app_package_dir = '/test_app/'
        dependencies = 'foo'

        ret = tethys_app_installation.custom_install_command(app_package, app_package_dir, dependencies)

        self.assertEquals('tethys_apps', ret.app_package)
        self.assertEquals('/test_app/', ret.app_package_dir)
        self.assertEquals('foo', ret.dependencies)
        self.assertEquals('tethys_apps.app_installation', ret.__module__)

    def test_custom_develop_command(self):
        app_package = 'tethys_apps1'
        app_package_dir = '/test_app/'
        dependencies = 'foo'

        ret = tethys_app_installation.custom_develop_command(app_package, app_package_dir, dependencies)

        self.assertEquals('tethys_apps1', ret.app_package)
        self.assertEquals('/test_app/', ret.app_package_dir)
        self.assertEquals('foo', ret.dependencies)
        self.assertEquals('tethys_apps.app_installation', ret.__module__)

    @mock.patch('tethys_apps.app_installation.shutil.copytree')
    @mock.patch('tethys_apps.app_installation.install')
    @mock.patch('tethys_apps.app_installation.subprocess')
    @mock.patch('tethys_apps.app_installation.get_tethysapp_directory', return_value='')
    @mock.patch('tethys_apps.app_installation.shutil')
    @mock.patch('tethys_apps.app_installation.pretty_output')
    def test__run_install_exception(self, mock_pretty_output, mock_shutil, mock_getdir, mock_subprocess, mock_install,
                                    mock_copy_tree):
        # mock the self input
        mock_self = mock.MagicMock(app_package='tethys_apps', app_package_dir='/test_app/', dependencies=['foo'])

        mock_copy_tree.side_effect = Exception, True

        # call the method for testing
        tethys_app_installation._run_install(self=mock_self)

        # check the method call
        mock_getdir.assert_called()

        # check the user notification
        mock_pretty_output.assert_called()

        # check the input arguments for shutil.copytree method
        shutil_call_args = mock_shutil.copytree.call_args_list
        self.assertEquals('/test_app/', shutil_call_args[0][0][0])

        mock_shutil.rmtree.assert_called()

        mock_shutil.copytree.assert_called()

        # check the input arguments for subprocess.call method
        process_call_args = mock_subprocess.call.call_args_list
        self.assertEquals('pip', process_call_args[0][0][0][0])
        self.assertEquals('install', process_call_args[0][0][0][1])
        self.assertEquals('foo', process_call_args[0][0][0][2])

        # check the install call
        mock_install.run.assert_called_with(mock_self)

    @mock.patch('tethys_apps.app_installation.os.remove')
    @mock.patch('tethys_apps.app_installation.shutil.rmtree')
    @mock.patch('tethys_apps.app_installation.shutil.copytree')
    @mock.patch('tethys_apps.app_installation.install')
    @mock.patch('tethys_apps.app_installation.subprocess')
    @mock.patch('tethys_apps.app_installation.get_tethysapp_directory', return_value='')
    @mock.patch('tethys_apps.app_installation.shutil')
    @mock.patch('tethys_apps.app_installation.pretty_output')
    def test__run_install_exception_rm_tree_exception(self, mock_pretty_output, mock_shutil, mock_getdir,
                                                      mock_subprocess, mock_install, mock_copy_tree, mock_remove_tree,
                                                      mock_os_remove_tree):
        # mock the self input
        mock_self = mock.MagicMock(app_package='tethys_apps', app_package_dir='/test_app/', dependencies=['foo'])

        mock_copy_tree.side_effect = Exception, True

        mock_remove_tree.side_effect = Exception

        # call the method for testing
        tethys_app_installation._run_install(self=mock_self)

        # check the method call
        mock_getdir.assert_called()

        # check the user notification
        mock_pretty_output.assert_called()

        # check the input arguments for shutil.copytree method
        shutil_call_args = mock_shutil.copytree.call_args_list
        self.assertEquals('/test_app/', shutil_call_args[0][0][0])

        mock_os_remove_tree.assert_called()

        mock_shutil.copytree.assert_called()

        # check the input arguments for subprocess.call method
        process_call_args = mock_subprocess.call.call_args_list
        self.assertEquals('pip', process_call_args[0][0][0][0])
        self.assertEquals('install', process_call_args[0][0][0][1])
        self.assertEquals('foo', process_call_args[0][0][0][2])

        # check the install call
        mock_install.run.assert_called_with(mock_self)

    @mock.patch('tethys_apps.app_installation.ctypes')
    @mock.patch('tethys_apps.app_installation.os.path.isdir')
    @mock.patch(callable_mock_path)
    @mock.patch('tethys_apps.app_installation.pretty_output')
    @mock.patch('tethys_apps.app_installation.get_tethysapp_directory')
    @mock.patch('tethys_apps.app_installation.os.path.join')
    def test_run_develop_windows(self, mock_os_path_join, mock_getdir, mock_pretty_output, mock_callable,
                                 mock_os_path_isdir, mock_ctypes):
        # mock the self input
        mock_self = mock.MagicMock(app_package='tethys_apps', app_package_dir='/test_app/', dependencies=['foo'])

        # mock callable method
        mock_callable.return_value = False

        mock_csl = mock.MagicMock(argtypes=mock.MagicMock(), restype=mock.MagicMock())

        mock_ctypes.windll.kernel32.CreateSymbolicLinkW = mock_csl

        mock_os_path_isdir.return_value = True

        mock_csl.return_value = 0
        mock_ctypes.WinError = Exception

        # call the method for testing
        self.assertRaises(Exception, tethys_app_installation._run_develop, mock_self)

        # check the method call
        mock_getdir.assert_called()
        mock_os_path_join.assert_called()

        # check the user notification
        mock_pretty_output.assert_called()

    @mock.patch('tethys_apps.app_installation.shutil.rmtree')
    @mock.patch('tethys_apps.app_installation.getattr')
    @mock.patch('tethys_apps.app_installation.develop')
    @mock.patch('tethys_apps.app_installation.subprocess')
    @mock.patch('tethys_apps.app_installation.os')
    @mock.patch('tethys_apps.app_installation.pretty_output')
    @mock.patch('tethys_apps.app_installation.get_tethysapp_directory')
    def test__run_develop_exception(self, mock_getdir, mock_pretty_output, mock_os, mock_subprocess,
                                    mock_develop, mock_getattr, mock_rm_tree):

        mock_destination = mock.MagicMock()
        mock_os.path.join.return_value = mock_destination

        # mock the self input
        mock_self = mock.MagicMock(app_package='tethys_apps', app_package_dir='/test_app/', dependencies=['foo'])

        mock_getattr.side_effect = Exception

        mock_rm_tree.side_effect = Exception

        # call the method for testing
        tethys_app_installation._run_develop(self=mock_self)

        # check the method call
        mock_getdir.assert_called()

        # check the user notification
        mock_pretty_output.assert_called()

        mock_rm_tree.assert_called_with(mock_destination)

        mock_os.remove.assert_called_with(mock_destination)

        # check the input arguments for os.symlink method
        symlink_call_args = mock_os.symlink.call_args_list
        self.assertEquals('/test_app/', symlink_call_args[0][0][0])

        # check the input arguments for subprocess.call method
        process_call_args = mock_subprocess.call.call_args_list
        self.assertEquals('pip', process_call_args[0][0][0][0])
        self.assertEquals('install', process_call_args[0][0][0][1])
        self.assertEquals('foo', process_call_args[0][0][0][2])

        # check the develop call
        mock_develop.run.assert_called_with(mock_self)
