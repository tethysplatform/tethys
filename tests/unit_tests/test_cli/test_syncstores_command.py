import unittest
from unittest import mock

from tethys_cli.syncstores_command import syncstores_command


class SyncstoresCommandTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('tethys_cli.syncstores_command.subprocess.call')
    @mock.patch('tethys_cli.syncstores_command.get_manage_path')
    def test_syncstores_command_no_args(self, mock_get_manage_path, mock_subprocess_call):
        mock_args = mock.MagicMock()
        mock_args.refresh = False
        mock_args.firsttime = False
        mock_args.database = False
        mock_args.app = False
        mock_get_manage_path.return_value = '/foo/manage.py'
        mock_subprocess_call.return_value = True

        syncstores_command(mock_args)

        mock_get_manage_path.assert_called_once()
        mock_subprocess_call.assert_called_once()
        mock_subprocess_call.assert_called_with(['python', '/foo/manage.py', 'syncstores'])

    @mock.patch('tethys_cli.syncstores_command.subprocess.call')
    @mock.patch('tethys_cli.syncstores_command.get_manage_path')
    def test_syncstores_command_args_no_refresh(self, mock_get_manage_path, mock_subprocess_call):
        mock_args = mock.MagicMock()
        mock_args.refresh = False
        mock_args.firsttime = True
        mock_args.database = 'foo_db'
        mock_args.app = ['foo_app']
        mock_get_manage_path.return_value = '/foo/manage.py'
        mock_subprocess_call.return_value = True

        syncstores_command(mock_args)

        mock_get_manage_path.assert_called_once()
        mock_subprocess_call.assert_called_once()
        mock_subprocess_call.assert_called_with(['python', '/foo/manage.py', 'syncstores', '-f', '-d', 'foo_db',
                                                 'foo_app'])

    @mock.patch('tethys_cli.syncstores_command.subprocess.call')
    @mock.patch('tethys_cli.syncstores_command.get_manage_path')
    def test_syncstores_command_no_args_assert(self, mock_get_manage_path, mock_subprocess_call):
        mock_args = mock.MagicMock()
        mock_args.refresh = False
        mock_args.firsttime = False
        mock_args.database = False
        mock_args.app = False
        mock_get_manage_path.return_value = '/foo/manage.py'
        mock_subprocess_call.side_effect = KeyboardInterrupt

        syncstores_command(mock_args)

        mock_get_manage_path.assert_called_once()
        mock_subprocess_call.assert_called_once()
        mock_subprocess_call.assert_called_with(['python', '/foo/manage.py', 'syncstores'])

    @mock.patch('tethys_cli.syncstores_command.input')
    @mock.patch('tethys_cli.syncstores_command.subprocess.call')
    @mock.patch('tethys_cli.syncstores_command.get_manage_path')
    def test_syncstores_command_refresh_continue(self, mock_get_manage_path, mock_subprocess_call, mock_input):
        mock_args = mock.MagicMock()
        mock_args.refresh = True
        mock_args.firsttime = False
        mock_args.database = False
        mock_args.app = ['foo_app']
        mock_get_manage_path.return_value = '/foo/manage.py'
        mock_subprocess_call.return_value = True
        mock_input.side_effect = ['foo', 'y']

        syncstores_command(mock_args)

        mock_get_manage_path.assert_called_once()
        mock_subprocess_call.assert_called_once()
        mock_subprocess_call.assert_called_with(['python', '/foo/manage.py', 'syncstores', '-r', 'foo_app'])
        po_call_args = mock_input.call_args_list
        self.assertEqual(2, len(po_call_args))
        self.assertIn('WARNING', po_call_args[0][0][0])
        self.assertIn('Invalid option. Do you wish to continue?', po_call_args[1][0][0])

    @mock.patch('tethys_cli.syncstores_command.print')
    @mock.patch('tethys_cli.syncstores_command.exit')
    @mock.patch('tethys_cli.syncstores_command.input')
    @mock.patch('tethys_cli.syncstores_command.subprocess.call')
    @mock.patch('tethys_cli.syncstores_command.get_manage_path')
    def test_syncstores_command_refresh_exit(self, mock_get_manage_path, mock_subprocess_call, mock_input, mock_exit,
                                             mock_print):
        mock_args = mock.MagicMock()
        mock_args.refresh = True
        mock_args.firsttime = False
        mock_args.database = False
        mock_args.app = ['foo_app']
        mock_get_manage_path.return_value = '/foo/manage.py'
        mock_subprocess_call.return_value = True
        mock_input.side_effect = ['n']
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, syncstores_command, mock_args)
        mock_exit.assert_called_with(0)

        mock_get_manage_path.assert_called_once()
        mock_subprocess_call.assert_not_called()

        po_call_args = mock_input.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('WARNING', po_call_args[0][0][0])

        # Check print statement
        rts_call_args = mock_print.call_args_list
        self.assertIn('Operation cancelled by user.', rts_call_args[0][0][0])
