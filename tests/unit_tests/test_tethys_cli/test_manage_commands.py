import unittest
from unittest import mock

import tethys_cli.manage_commands as manage_commands
from tethys_cli.manage_commands import (
    MANAGE_START,
    MANAGE_COLLECTSTATIC,
    MANAGE_COLLECTWORKSPACES,
    MANAGE_COLLECT,
    MANAGE_CREATESUPERUSER
)


class TestManageCommands(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('tethys_cli.manage_commands.run_process')
    def test_manage_command_manage_start(self, mock_run_process):
        # mock the input args
        args = mock.MagicMock(manage='', command=MANAGE_START, port='8080')

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # check the values from the argument list
        self.assertEqual('python', process_call_args[0][0][0][0])
        self.assertIn('manage.py', process_call_args[0][0][0][1])
        self.assertEqual('runserver', process_call_args[0][0][0][2])
        self.assertEqual('8080', process_call_args[0][0][0][3])

    @mock.patch('tethys_cli.manage_commands.run_process')
    def test_manage_command_manage_start_with_no_port(self, mock_run_process):
        # mock the input args
        args = mock.MagicMock(manage='', command=MANAGE_START, port='')

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # check the values from the argument list
        self.assertEqual('python', process_call_args[0][0][0][0])
        self.assertIn('manage.py', process_call_args[0][0][0][1])
        self.assertEqual('runserver', process_call_args[0][0][0][2])

    @mock.patch('tethys_cli.manage_commands.run_process')
    def test_manage_command_manage_manage_collectstatic(self, mock_run_process):
        # mock the input args
        args = mock.MagicMock(manage='', command=MANAGE_COLLECTSTATIC, port='8080', noinput=False)

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # intermediate process
        self.assertEqual('python', process_call_args[0][0][0][0])
        self.assertIn('manage.py', process_call_args[0][0][0][1])
        self.assertEqual('pre_collectstatic', process_call_args[0][0][0][2])

        # primary process
        self.assertEqual('python', process_call_args[1][0][0][0])
        self.assertIn('manage.py', process_call_args[1][0][0][1])
        self.assertEqual('collectstatic', process_call_args[1][0][0][2])
        self.assertNotIn('--noinput', process_call_args[1][0][0])

    @mock.patch('tethys_cli.manage_commands.run_process')
    def test_manage_command_manage_manage_collectstatic_with_no_input(self, mock_run_process):
        # mock the input args
        args = mock.MagicMock(manage='', command=MANAGE_COLLECTSTATIC, port='8080', noinput=True)

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # intermediate process
        self.assertEqual('python', process_call_args[0][0][0][0])
        self.assertIn('manage.py', process_call_args[0][0][0][1])
        self.assertEqual('pre_collectstatic', process_call_args[0][0][0][2])

        # primary process
        self.assertEqual('python', process_call_args[1][0][0][0])
        self.assertIn('manage.py', process_call_args[1][0][0][1])
        self.assertEqual('collectstatic', process_call_args[1][0][0][2])
        self.assertEqual('--noinput', process_call_args[1][0][0][3])

    @mock.patch('tethys_cli.manage_commands.run_process')
    def test_manage_command_manage_manage_collect_workspace(self, mock_run_process):
        # mock the input args
        args = mock.MagicMock(manage='', command=MANAGE_COLLECTWORKSPACES, port='8080', force=True)

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # check the values from the argument list
        self.assertEqual('python', process_call_args[0][0][0][0])
        self.assertIn('manage.py', process_call_args[0][0][0][1])
        self.assertEqual('collectworkspaces', process_call_args[0][0][0][2])
        self.assertEqual('--force', process_call_args[0][0][0][3])

    @mock.patch('tethys_cli.manage_commands.run_process')
    def test_manage_command_manage_manage_collect_workspace_with_no_force(self, mock_run_process):
        # mock the input args
        args = mock.MagicMock(manage='', command=MANAGE_COLLECTWORKSPACES, force=False)

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # check the values from the argument list
        self.assertEqual('python', process_call_args[0][0][0][0])
        self.assertIn('manage.py', process_call_args[0][0][0][1])
        self.assertEqual('collectworkspaces', process_call_args[0][0][0][2])
        self.assertNotIn('--force', process_call_args[0][0][0])

    @mock.patch('tethys_cli.manage_commands.run_process')
    def test_manage_command_manage_manage_collect(self, mock_run_process):
        # mock the input args
        args = mock.MagicMock(manage='', command=MANAGE_COLLECT, port='8080', noinput=False)

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # pre_collectstatic
        self.assertEqual('python', process_call_args[0][0][0][0])
        self.assertIn('manage.py', process_call_args[0][0][0][1])
        self.assertEqual('pre_collectstatic', process_call_args[0][0][0][2])

        # collectstatic
        self.assertEqual('python', process_call_args[1][0][0][0])
        self.assertIn('manage.py', process_call_args[1][0][0][1])
        self.assertEqual('collectstatic', process_call_args[1][0][0][2])
        self.assertNotIn('--noinput', process_call_args[1][0][0])

        # collectworkspaces
        self.assertEqual('python', process_call_args[2][0][0][0])
        self.assertIn('manage.py', process_call_args[2][0][0][1])
        self.assertEqual('collectworkspaces', process_call_args[2][0][0][2])

    @mock.patch('tethys_cli.manage_commands.run_process')
    def test_manage_command_manage_manage_collect_no_input(self, mock_run_process):
        # mock the input args
        args = mock.MagicMock(manage='', command=MANAGE_COLLECT, port='8080', noinput=True)

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # pre_collectstatic
        self.assertEqual('python', process_call_args[0][0][0][0])
        self.assertIn('manage.py', process_call_args[0][0][0][1])
        self.assertEqual('pre_collectstatic', process_call_args[0][0][0][2])

        # collectstatic
        self.assertEqual('python', process_call_args[1][0][0][0])
        self.assertIn('manage.py', process_call_args[1][0][0][1])
        self.assertEqual('collectstatic', process_call_args[1][0][0][2])
        self.assertEqual('--noinput', process_call_args[1][0][0][3])

        # collectworkspaces
        self.assertEqual('python', process_call_args[2][0][0][0])
        self.assertIn('manage.py', process_call_args[2][0][0][1])
        self.assertEqual('collectworkspaces', process_call_args[2][0][0][2])

    @mock.patch('tethys_cli.manage_commands.run_process')
    def test_manage_command_manage_manage_create_super_user(self, mock_run_process):
        # mock the input args
        args = mock.MagicMock(manage='', command=MANAGE_CREATESUPERUSER, port='8080')

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # check the values from the argument list
        self.assertEqual('python', process_call_args[0][0][0][0])
        self.assertIn('manage.py', process_call_args[0][0][0][1])
        self.assertEqual('createsuperuser', process_call_args[0][0][0][2])
