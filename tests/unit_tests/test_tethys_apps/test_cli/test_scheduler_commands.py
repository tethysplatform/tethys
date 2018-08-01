import unittest
import mock

from tethys_apps.cli.scheduler_commands import scheduler_create_command, schedulers_list_command, \
    schedulers_remove_command


class SchedulerCommandsTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('tethys_apps.cli.scheduler_commands.pretty_output')
    @mock.patch('tethys_apps.cli.scheduler_commands.exit')
    @mock.patch('tethys_compute.models.Scheduler')
    def test_scheduler_create_command(self, mock_scheduler, mock_exit, mock_pretty_output):
        mock_args = mock.MagicMock()
        mock_scheduler.objects.filter().first.return_value = False
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, scheduler_create_command, mock_args)

        mock_scheduler.assert_called_with(
            name=mock_args.name,
            host=mock_args.endpoint,
            username=mock_args.username,
            password=mock_args.password,
            private_key_path=mock_args.private_key_path,
            private_key_pass=mock_args.private_key_pass
        )
        mock_scheduler().save.assert_called()
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual('Scheduler created successfully!', po_call_args[0][0][0])
        mock_exit.assert_called_with(0)

    @mock.patch('tethys_apps.cli.scheduler_commands.pretty_output')
    @mock.patch('tethys_apps.cli.scheduler_commands.exit')
    @mock.patch('tethys_compute.models.Scheduler')
    def test_scheduler_create_command_existing_scheduler(self, mock_scheduler, mock_exit, mock_pretty_output):
        mock_args = mock.MagicMock()
        mock_scheduler.objects.filter().first.return_value = True
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, scheduler_create_command, mock_args)

        mock_scheduler.assert_not_called()
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn('already exists', po_call_args[0][0][0])
        mock_exit.assert_called_with(0)

    def test_schedulers_list_command(self):
        pass

    def test_schedulers_list_command_no_schedulers(self):
        pass

    def test_schedulers_remove_command_force(self):
        pass

    def test_schedulers_remove_command_force_invalid_proceed_char(self):
        pass

    def test_schedulers_remove_command_no_force_proceed(self):
        pass

    def test_schedulers_remove_command_no_force_no_proceed(self):
        pass

    def test_schedulers_remove_command_does_not_exist(self):
        pass

