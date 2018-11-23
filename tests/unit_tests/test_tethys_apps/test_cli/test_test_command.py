import unittest
import mock

from tethys_apps.cli.test_command import test_command


class TestCommandTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('tethys_apps.cli.test_command.run_process')
    @mock.patch('tethys_apps.cli.test_command.os.path.join')
    @mock.patch('tethys_apps.cli.test_command.get_manage_path')
    def test_test_command_no_coverage_file(self, mock_get_manage_path, mock_join, mock_run_process):
        mock_args = mock.MagicMock()
        mock_args.coverage = False
        mock_args.coverage_html = False
        mock_args.file = 'foo_file'
        mock_args.unit = False
        mock_args.gui = False
        mock_get_manage_path.return_value = '/foo/manage.py'
        mock_join.return_value = '/foo'
        mock_run_process.return_value = 0

        self.assertRaises(SystemExit, test_command, mock_args)
        mock_get_manage_path.assert_called()
        mock_join.assert_called()
        mock_run_process.assert_called_once()
        mock_run_process.assert_called_with(['python', '/foo/manage.py', 'test', 'foo_file'])

    @mock.patch('tethys_apps.cli.test_command.run_process')
    @mock.patch('tethys_apps.cli.test_command.os.path.join')
    @mock.patch('tethys_apps.cli.test_command.get_manage_path')
    def test_test_command_coverage_unit(self, mock_get_manage_path, mock_join, mock_run_process):
        mock_args = mock.MagicMock()
        mock_args.coverage = True
        mock_args.coverage_html = False
        mock_args.file = None
        mock_args.unit = True
        mock_args.gui = False
        mock_get_manage_path.return_value = '/foo/manage.py'
        mock_join.return_value = '/foo'
        mock_run_process.return_value = 0

        self.assertRaises(SystemExit, test_command, mock_args)
        mock_get_manage_path.assert_called()
        mock_join.assert_called()
        mock_run_process.assert_called()
        mock_run_process.assert_any_call(['coverage', 'run', '--rcfile=/foo', '/foo/manage.py', 'test', '/foo'])
        mock_run_process.assert_called_with(['coverage', 'report', '--rcfile=/foo'])

    @mock.patch('tethys_apps.cli.test_command.run_process')
    @mock.patch('tethys_apps.cli.test_command.os.path.join')
    @mock.patch('tethys_apps.cli.test_command.get_manage_path')
    def test_test_command_coverage_unit_file_app_package(self, mock_get_manage_path, mock_join, mock_run_process):
        mock_args = mock.MagicMock()
        mock_args.coverage = True
        mock_args.coverage_html = False
        mock_args.file = '/foo/tethys_apps.tethysapp.foo'
        mock_args.unit = True
        mock_args.gui = False
        mock_get_manage_path.return_value = '/foo/manage.py'
        mock_join.return_value = '/foo'
        mock_run_process.return_value = 0

        self.assertRaises(SystemExit, test_command, mock_args)
        mock_get_manage_path.assert_called()
        mock_join.assert_called()
        mock_run_process.assert_called()
        mock_run_process.assert_any_call(['coverage', 'run', '--source=tethys_apps.tethysapp.foo,tethysapp.foo',
                                          '/foo/manage.py', 'test', '/foo/tethys_apps.tethysapp.foo'])
        mock_run_process.assert_called_with(['coverage', 'report'])

    @mock.patch('tethys_apps.cli.test_command.run_process')
    @mock.patch('tethys_apps.cli.test_command.os.path.join')
    @mock.patch('tethys_apps.cli.test_command.get_manage_path')
    def test_test_command_coverage_html_unit_file_app_package(self, mock_get_manage_path, mock_join, mock_run_process):
        mock_args = mock.MagicMock()
        mock_args.coverage = False
        mock_args.coverage_html = True
        mock_args.file = '/foo/tethys_apps.tethysapp.foo'
        mock_args.unit = True
        mock_args.gui = False
        mock_get_manage_path.return_value = '/foo/manage.py'
        mock_join.return_value = '/foo'
        mock_run_process.return_value = 0

        self.assertRaises(SystemExit, test_command, mock_args)
        mock_get_manage_path.assert_called()
        mock_join.assert_called()
        mock_run_process.assert_called()
        mock_run_process.assert_any_call(['coverage', 'run', '--source=tethys_apps.tethysapp.foo,tethysapp.foo',
                                          '/foo/manage.py', 'test', '/foo/tethys_apps.tethysapp.foo'])
        mock_run_process.assert_any_call(['coverage', 'html', '--directory=/foo'])
        mock_run_process.assert_called_with(['open', '/foo'])

    @mock.patch('tethys_apps.cli.test_command.run_process')
    @mock.patch('tethys_apps.cli.test_command.os.path.join')
    @mock.patch('tethys_apps.cli.test_command.get_manage_path')
    def test_test_command_coverage_unit_file_extension_package(self, mock_get_manage_path, mock_join, mock_run_process):
        mock_args = mock.MagicMock()
        mock_args.coverage = True
        mock_args.coverage_html = False
        mock_args.file = '/foo/tethysext.foo'
        mock_args.unit = True
        mock_args.gui = False
        mock_get_manage_path.return_value = '/foo/manage.py'
        mock_join.return_value = '/foo'
        mock_run_process.return_value = 0

        self.assertRaises(SystemExit, test_command, mock_args)
        mock_get_manage_path.assert_called()
        mock_join.assert_called()
        mock_run_process.assert_called()
        mock_run_process.assert_any_call(['coverage', 'run', '--source=tethysext.foo,tethysext.foo', '/foo/manage.py',
                                          'test', '/foo/tethysext.foo'])
        mock_run_process.assert_called_with(['coverage', 'report'])

    @mock.patch('tethys_apps.cli.test_command.run_process')
    @mock.patch('tethys_apps.cli.test_command.os.path.join')
    @mock.patch('tethys_apps.cli.test_command.get_manage_path')
    def test_test_command_coverage_html_gui_file(self, mock_get_manage_path, mock_join, mock_run_process):
        mock_args = mock.MagicMock()
        mock_args.coverage = False
        mock_args.coverage_html = True
        mock_args.file = 'foo_file'
        mock_args.unit = False
        mock_args.gui = True
        mock_get_manage_path.return_value = '/foo/manage.py'
        mock_join.return_value = '/foo/bar'
        mock_run_process.return_value = 0

        self.assertRaises(SystemExit, test_command, mock_args)
        mock_get_manage_path.assert_called()
        mock_join.assert_called()
        mock_run_process.assert_called()
        mock_run_process.assert_any_call(['coverage', 'run', '--rcfile=/foo/bar', '/foo/manage.py', 'test', 'foo_file'])
        mock_run_process.assert_any_call(['coverage', 'html', '--rcfile=/foo/bar'])
        mock_run_process.assert_called_with(['open', '/foo/bar'])

    @mock.patch('tethys_apps.cli.test_command.webbrowser.open_new_tab')
    @mock.patch('tethys_apps.cli.test_command.run_process')
    @mock.patch('tethys_apps.cli.test_command.os.path.join')
    @mock.patch('tethys_apps.cli.test_command.get_manage_path')
    def test_test_command_coverage_html_gui_file_exception(self, mock_get_manage_path, mock_join, mock_run_process,
                                                           mock_open_new_tab):
        mock_args = mock.MagicMock()
        mock_args.coverage = False
        mock_args.coverage_html = True
        mock_args.file = 'foo_file'
        mock_args.unit = False
        mock_args.gui = True
        mock_get_manage_path.return_value = '/foo/manage.py'
        mock_join.side_effect = ['/foo/bar', '/foo/bar2', '/foo/bar3', '/foo/bar4', '/foo/bar5', '/foo/bar6']
        mock_run_process.side_effect = [0, 0, 1]
        mock_open_new_tab.return_value = 1

        self.assertRaises(SystemExit, test_command, mock_args)
        mock_get_manage_path.assert_called()
        mock_join.assert_called()
        mock_run_process.assert_called()
        mock_run_process.assert_any_call(['coverage', 'run', '--rcfile=/foo/bar2', '/foo/manage.py',
                                          'test', 'foo_file'])
        mock_run_process.assert_any_call(['coverage', 'html', '--rcfile=/foo/bar2'])
        mock_run_process.assert_called_with(['open', '/foo/bar3'])
        mock_open_new_tab.assert_called_once()
        mock_open_new_tab.assert_called_with('/foo/bar4')

    @mock.patch('tethys_apps.cli.test_command.run_process')
    @mock.patch('tethys_apps.cli.test_command.os.path.join')
    @mock.patch('tethys_apps.cli.test_command.get_manage_path')
    def test_test_command_unit_no_file(self, mock_get_manage_path, mock_join, mock_run_process):
        mock_args = mock.MagicMock()
        mock_args.coverage = False
        mock_args.coverage_html = False
        mock_args.file = None
        mock_args.unit = True
        mock_args.gui = False
        mock_get_manage_path.return_value = '/foo/manage.py'
        mock_join.return_value = '/foo'
        mock_run_process.return_value = 0

        self.assertRaises(SystemExit, test_command, mock_args)

        mock_get_manage_path.assert_called()
        mock_join.assert_called()
        mock_run_process.assert_called_once()
        mock_run_process.assert_called_with(['python', '/foo/manage.py', 'test', '/foo'])

    @mock.patch('tethys_apps.cli.test_command.run_process')
    @mock.patch('tethys_apps.cli.test_command.os.path.join')
    @mock.patch('tethys_apps.cli.test_command.get_manage_path')
    def test_test_command_gui_no_file(self, mock_get_manage_path, mock_join, mock_run_process):
        mock_args = mock.MagicMock()
        mock_args.coverage = False
        mock_args.coverage_html = False
        mock_args.file = None
        mock_args.unit = False
        mock_args.gui = True
        mock_get_manage_path.return_value = '/foo/manage.py'
        mock_join.return_value = '/foo'
        mock_run_process.return_value = 0

        self.assertRaises(SystemExit, test_command, mock_args)
        mock_get_manage_path.assert_called()
        mock_join.assert_called()
        mock_run_process.assert_called_once()
        mock_run_process.assert_called_with(['python', '/foo/manage.py', 'test', '/foo'])
