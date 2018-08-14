import unittest
import mock
import tethys_apps.cli.manage_commands as manage_commands
from tethys_apps.cli.manage_commands import MANAGE_START, MANAGE_SYNCDB, MANAGE_COLLECTSTATIC, \
    MANAGE_COLLECTWORKSPACES, MANAGE_COLLECT, MANAGE_CREATESUPERUSER, MANAGE_SYNC


class TestManageCommands(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_manage_path(self):
        # mock the input args with manage attribute
        args = mock.MagicMock(manage='')

        # call the method
        ret = manage_commands.get_manage_path(args=args)

        # check whether the response has manage
        self.assertIn('manage.py', ret)

    @mock.patch('tethys_apps.cli.manage_commands.pretty_output')
    @mock.patch('tethys_apps.cli.manage_commands.exit')
    def test_get_manage_path_error(self, mock_exit, mock_pretty_output):
        # mock the system exit
        mock_exit.side_effect = SystemExit

        # mock the input args with manage attribute
        args = mock.MagicMock(manage='foo')

        self.assertRaises(SystemExit, manage_commands.get_manage_path, args=args)

        # check the mock exit value
        mock_exit.assert_called_with(1)
        mock_pretty_output.assert_called()

    @mock.patch('tethys_apps.cli.manage_commands.run_process')
    def test_manage_command_manage_start(self, mock_run_process):
        # mock the input args
        args = mock.MagicMock(manage='', command=MANAGE_START, port='8080')

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # check the values from the argument list
        self.assertEquals('python', process_call_args[0][0][0][0])
        self.assertIn('manage.py', process_call_args[0][0][0][1])
        self.assertEquals('runserver', process_call_args[0][0][0][2])
        self.assertEquals('8080', process_call_args[0][0][0][3])

    @mock.patch('tethys_apps.cli.manage_commands.run_process')
    def test_manage_command_manage_start_with_no_port(self, mock_run_process):
        # mock the input args
        args = mock.MagicMock(manage='', command=MANAGE_START, port='')

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # check the values from the argument list
        self.assertEquals('python', process_call_args[0][0][0][0])
        self.assertIn('manage.py', process_call_args[0][0][0][1])
        self.assertEquals('runserver', process_call_args[0][0][0][2])

    @mock.patch('tethys_apps.cli.manage_commands.run_process')
    def test_manage_command_manage_syncdb(self, mock_run_process):
        # mock the input args
        args = mock.MagicMock(manage='', command=MANAGE_SYNCDB, port='8080')

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # intermediate process
        self.assertEquals('python', process_call_args[0][0][0][0])
        self.assertIn('manage.py', process_call_args[0][0][0][1])
        self.assertEquals('makemigrations', process_call_args[0][0][0][2])

        # primary process
        self.assertEquals('python', process_call_args[1][0][0][0])
        self.assertIn('manage.py', process_call_args[1][0][0][1])
        self.assertEquals('migrate', process_call_args[1][0][0][2])

    @mock.patch('tethys_apps.cli.manage_commands.run_process')
    def test_manage_command_manage_manage_collectstatic(self, mock_run_process):
        # mock the input args
        args = mock.MagicMock(manage='', command=MANAGE_COLLECTSTATIC, port='8080', noinput=False)

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # intermediate process
        self.assertEquals('python', process_call_args[0][0][0][0])
        self.assertIn('manage.py', process_call_args[0][0][0][1])
        self.assertEquals('pre_collectstatic', process_call_args[0][0][0][2])

        # primary process
        self.assertEquals('python', process_call_args[1][0][0][0])
        self.assertIn('manage.py', process_call_args[1][0][0][1])
        self.assertEquals('collectstatic', process_call_args[1][0][0][2])
        self.assertNotIn('--noinput', process_call_args[1][0][0])

    @mock.patch('tethys_apps.cli.manage_commands.run_process')
    def test_manage_command_manage_manage_collectstatic_with_no_input(self, mock_run_process):
        # mock the input args
        args = mock.MagicMock(manage='', command=MANAGE_COLLECTSTATIC, port='8080', noinput=True)

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # intermediate process
        self.assertEquals('python', process_call_args[0][0][0][0])
        self.assertIn('manage.py', process_call_args[0][0][0][1])
        self.assertEquals('pre_collectstatic', process_call_args[0][0][0][2])

        # primary process
        self.assertEquals('python', process_call_args[1][0][0][0])
        self.assertIn('manage.py', process_call_args[1][0][0][1])
        self.assertEquals('collectstatic', process_call_args[1][0][0][2])
        self.assertEquals('--noinput', process_call_args[1][0][0][3])

    @mock.patch('tethys_apps.cli.manage_commands.run_process')
    def test_manage_command_manage_manage_collect_workspace(self, mock_run_process):
        # mock the input args
        args = mock.MagicMock(manage='', command=MANAGE_COLLECTWORKSPACES, port='8080', force=True)

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # check the values from the argument list
        self.assertEquals('python', process_call_args[0][0][0][0])
        self.assertIn('manage.py', process_call_args[0][0][0][1])
        self.assertEquals('collectworkspaces', process_call_args[0][0][0][2])
        self.assertEquals('--force', process_call_args[0][0][0][3])

    @mock.patch('tethys_apps.cli.manage_commands.run_process')
    def test_manage_command_manage_manage_collect_workspace_with_no_force(self, mock_run_process):
        # mock the input args
        args = mock.MagicMock(manage='', command=MANAGE_COLLECTWORKSPACES, force=False)

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # check the values from the argument list
        self.assertEquals('python', process_call_args[0][0][0][0])
        self.assertIn('manage.py', process_call_args[0][0][0][1])
        self.assertEquals('collectworkspaces', process_call_args[0][0][0][2])
        self.assertNotIn('--force', process_call_args[0][0][0])

    @mock.patch('tethys_apps.cli.manage_commands.run_process')
    def test_manage_command_manage_manage_collect(self, mock_run_process):
        # mock the input args
        args = mock.MagicMock(manage='', command=MANAGE_COLLECT, port='8080', noinput=False)

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # pre_collectstatic
        self.assertEquals('python', process_call_args[0][0][0][0])
        self.assertIn('manage.py', process_call_args[0][0][0][1])
        self.assertEquals('pre_collectstatic', process_call_args[0][0][0][2])

        # collectstatic
        self.assertEquals('python', process_call_args[1][0][0][0])
        self.assertIn('manage.py', process_call_args[1][0][0][1])
        self.assertEquals('collectstatic', process_call_args[1][0][0][2])
        self.assertNotIn('--noinput', process_call_args[1][0][0])

        # collectworkspaces
        self.assertEquals('python', process_call_args[2][0][0][0])
        self.assertIn('manage.py', process_call_args[2][0][0][1])
        self.assertEquals('collectworkspaces', process_call_args[2][0][0][2])

    @mock.patch('tethys_apps.cli.manage_commands.run_process')
    def test_manage_command_manage_manage_collect_no_input(self, mock_run_process):
        # mock the input args
        args = mock.MagicMock(manage='', command=MANAGE_COLLECT, port='8080', noinput=True)

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # pre_collectstatic
        self.assertEquals('python', process_call_args[0][0][0][0])
        self.assertIn('manage.py', process_call_args[0][0][0][1])
        self.assertEquals('pre_collectstatic', process_call_args[0][0][0][2])

        # collectstatic
        self.assertEquals('python', process_call_args[1][0][0][0])
        self.assertIn('manage.py', process_call_args[1][0][0][1])
        self.assertEquals('collectstatic', process_call_args[1][0][0][2])
        self.assertEquals('--noinput', process_call_args[1][0][0][3])

        # collectworkspaces
        self.assertEquals('python', process_call_args[2][0][0][0])
        self.assertIn('manage.py', process_call_args[2][0][0][1])
        self.assertEquals('collectworkspaces', process_call_args[2][0][0][2])

    @mock.patch('tethys_apps.cli.manage_commands.run_process')
    def test_manage_command_manage_manage_create_super_user(self, mock_run_process):
        # mock the input args
        args = mock.MagicMock(manage='', command=MANAGE_CREATESUPERUSER, port='8080')

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # check the values from the argument list
        self.assertEquals('python', process_call_args[0][0][0][0])
        self.assertIn('manage.py', process_call_args[0][0][0][1])
        self.assertEquals('createsuperuser', process_call_args[0][0][0][2])

    @mock.patch('tethys_apps.harvester.SingletonHarvester')
    def test_manage_command_manage_manage_sync(self, MockSingletonHarvester):
        # mock the input args
        args = mock.MagicMock(manage='', command=MANAGE_SYNC, port='8080')

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # mock the singleton harvester
        MockSingletonHarvester.assert_called()
        MockSingletonHarvester().harvest.assert_called()

    @mock.patch('tethys_apps.cli.manage_commands.subprocess.call')
    @mock.patch('tethys_apps.cli.manage_commands.set_testing_environment')
    def test_run_process(self, mock_te_call, mock_subprocess_call):

        # mock the process
        mock_process = ['test']

        manage_commands.run_process(mock_process)

        self.assertEqual(2, len(mock_te_call.call_args_list))

        mock_subprocess_call.assert_called_with(mock_process)

    @mock.patch('tethys_apps.cli.manage_commands.subprocess.call')
    @mock.patch('tethys_apps.cli.manage_commands.set_testing_environment')
    def test_run_process_keyboardinterrupt(self, mock_te_call, mock_subprocess_call):

        # mock the process
        mock_process = ['foo']

        mock_subprocess_call.side_effect = KeyboardInterrupt

        manage_commands.run_process(mock_process)
        mock_subprocess_call.assert_called_with(mock_process)
        mock_te_call.assert_called_once()
