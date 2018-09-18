import unittest
import mock

from tethys_apps.cli.list_command import list_command
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class ListCommandTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass


    @mock.patch('tethys_apps.cli.list_command.print')
    @mock.patch('tethys_apps.cli.list_command.get_installed_tethys_extensions')
    @mock.patch('tethys_apps.cli.list_command.get_installed_tethys_apps')
    def test_list_command_installed_apps(self, mock_installed_apps, mock_installed_extensions, mock_print):
        mock_args = mock.MagicMock()
        mock_installed_apps.return_value = {'foo': '/foo', 'bar': "/bar"}
        mock_installed_extensions.return_value = {}

        list_command(mock_args)

        mock_installed_apps.assert_called_once()

        # Check if print is called correctly
        rts_call_args = mock_print.call_args_list
        self.assertIn('Apps:', rts_call_args[0][0][0])
        self.assertIn('foo', rts_call_args[1][0][0])
        self.assertIn('bar', rts_call_args[2][0][0])

    @mock.patch('tethys_apps.cli.list_command.print')
    @mock.patch('tethys_apps.cli.list_command.get_installed_tethys_extensions')
    @mock.patch('tethys_apps.cli.list_command.get_installed_tethys_apps')
    def test_list_command_installed_extensions(self, mock_installed_apps, mock_installed_extensions, mock_print):
        mock_args = mock.MagicMock()
        mock_installed_apps.return_value = {}
        mock_installed_extensions.return_value = {'baz': '/baz'}

        list_command(mock_args)

        # Check if print is called correctly
        rts_call_args = mock_print.call_args_list
        self.assertIn('Extensions:', rts_call_args[0][0][0])
        self.assertIn('baz', rts_call_args[1][0][0])

    @mock.patch('tethys_apps.cli.list_command.print')
    @mock.patch('tethys_apps.cli.list_command.get_installed_tethys_extensions')
    @mock.patch('tethys_apps.cli.list_command.get_installed_tethys_apps')
    def test_list_command_installed_both(self, mock_installed_apps, mock_installed_extensions, mock_print):
        mock_args = mock.MagicMock()
        mock_installed_apps.return_value = {'foo': '/foo', 'bar': "/bar"}
        mock_installed_extensions.return_value = {'baz': '/baz'}

        list_command(mock_args)

        # Check if print is called correctly
        rts_call_args = mock_print.call_args_list
        self.assertIn('Apps:', rts_call_args[0][0][0])
        self.assertIn('foo', rts_call_args[1][0][0])
        self.assertIn('bar', rts_call_args[2][0][0])
        self.assertIn('Extensions:', rts_call_args[3][0][0])
        self.assertIn('baz', rts_call_args[4][0][0])
