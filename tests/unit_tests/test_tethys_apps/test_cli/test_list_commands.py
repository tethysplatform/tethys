import cStringIO
import unittest
import mock

from tethys_apps.cli.list_command import list_command


class ListCommandTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('sys.stdout', new_callable=cStringIO.StringIO)
    @mock.patch('tethys_apps.cli.list_command.get_installed_tethys_extensions')
    @mock.patch('tethys_apps.cli.list_command.get_installed_tethys_apps')
    def test_list_command_installed_apps(self, mock_installed_apps, mock_installed_extensions, mock_stdout):
        mock_args = mock.MagicMock()
        mock_installed_apps.return_value = {'foo': '/foo', 'bar': "/bar"}
        mock_installed_extensions.return_value = {}

        list_command(mock_args)

        mock_installed_apps.assert_called_once()
        self.assertIn('Apps:', mock_stdout.getvalue())
        self.assertIn('foo', mock_stdout.getvalue())
        self.assertIn('bar', mock_stdout.getvalue())
        self.assertNotIn('Extensions:', mock_stdout.getvalue())
        self.assertNotIn('baz', mock_stdout.getvalue())

    @mock.patch('sys.stdout', new_callable=cStringIO.StringIO)
    @mock.patch('tethys_apps.cli.list_command.get_installed_tethys_extensions')
    @mock.patch('tethys_apps.cli.list_command.get_installed_tethys_apps')
    def test_list_command_installed_extensions(self, mock_installed_apps, mock_installed_extensions, mock_stdout):
        mock_args = mock.MagicMock()
        mock_installed_apps.return_value = {}
        mock_installed_extensions.return_value = {'baz': '/baz'}

        list_command(mock_args)

        self.assertNotIn('Apps:', mock_stdout.getvalue())
        self.assertNotIn('foo', mock_stdout.getvalue())
        self.assertNotIn('bar', mock_stdout.getvalue())
        self.assertIn('Extensions:', mock_stdout.getvalue())
        self.assertIn('baz', mock_stdout.getvalue())

    @mock.patch('sys.stdout', new_callable=cStringIO.StringIO)
    @mock.patch('tethys_apps.cli.list_command.get_installed_tethys_extensions')
    @mock.patch('tethys_apps.cli.list_command.get_installed_tethys_apps')
    def test_list_command_installed_both(self, mock_installed_apps, mock_installed_extensions, mock_stdout):
        mock_args = mock.MagicMock()
        mock_installed_apps.return_value = {'foo': '/foo', 'bar': "/bar"}
        mock_installed_extensions.return_value = {'baz': '/baz'}

        list_command(mock_args)

        self.assertIn('Apps:', mock_stdout.getvalue())
        self.assertIn('foo', mock_stdout.getvalue())
        self.assertIn('bar', mock_stdout.getvalue())
        self.assertIn('Extensions:', mock_stdout.getvalue())
        self.assertIn('baz', mock_stdout.getvalue())