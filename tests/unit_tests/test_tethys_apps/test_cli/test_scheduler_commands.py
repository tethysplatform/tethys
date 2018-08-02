import unittest
import mock

from tethys_apps.cli.scheduler_commands import scheduler_create_command, schedulers_list_command, \
    schedulers_remove_command
from django.core.exceptions import ObjectDoesNotExist


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

        mock_scheduler.objects.filter.assert_called()
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn('already exists', po_call_args[0][0][0])
        mock_exit.assert_called_with(0)

    @mock.patch('tethys_apps.cli.scheduler_commands.pretty_output')
    @mock.patch('tethys_compute.models.Scheduler')
    def test_schedulers_list_command(self, mock_scheduler, mock_pretty_output):
        mock_scheduler.objects.all.return_value = [mock.MagicMock(), mock.MagicMock()]
        mock_args = mock.MagicMock()
        schedulers_list_command(mock_args)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(3, len(po_call_args))
        self.assertIn('Name', po_call_args[0][0][0])
        self.assertIn('Host', po_call_args[0][0][0])
        self.assertIn('Username', po_call_args[0][0][0])
        self.assertIn('Password', po_call_args[0][0][0])
        self.assertIn('Private Key Path', po_call_args[0][0][0])
        self.assertIn('Private Key Pass', po_call_args[0][0][0])

    @mock.patch('tethys_apps.cli.scheduler_commands.pretty_output')
    @mock.patch('tethys_compute.models.Scheduler')
    def test_schedulers_list_command_no_schedulers(self, mock_scheduler, mock_pretty_output):
        mock_scheduler.objects.all.return_value = []
        mock_args = mock.MagicMock()
        schedulers_list_command(mock_args)

        mock_scheduler.objects.all.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual('There are no Schedulers registered in Tethys.', po_call_args[0][0][0])

    @mock.patch('tethys_apps.cli.scheduler_commands.pretty_output')
    @mock.patch('tethys_apps.cli.scheduler_commands.exit')
    @mock.patch('tethys_compute.models.Scheduler')
    def test_schedulers_remove_command_force(self, mock_scheduler, mock_exit, mock_pretty_output):
        mock_args = mock.MagicMock()
        mock_args.force = True
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, schedulers_remove_command, mock_args)

        mock_scheduler.objects.get.assert_called()
        mock_scheduler.objects.get().delete.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('Successfully removed Scheduler', po_call_args[0][0][0])

    @mock.patch('__builtin__.raw_input')
    @mock.patch('tethys_apps.cli.scheduler_commands.pretty_output')
    @mock.patch('tethys_apps.cli.scheduler_commands.exit')
    @mock.patch('tethys_compute.models.Scheduler')
    def test_schedulers_remove_command_force_invalid_proceed_char(self, mock_scheduler, mock_exit, mock_pretty_output,
                                                                  mock_input):
        mock_args = mock.MagicMock()
        mock_args.force = False
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit
        mock_input.side_effect = ['foo', 'N']

        self.assertRaises(SystemExit, schedulers_remove_command, mock_args)

        mock_scheduler.objects.get.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual('Aborted. Scheduler not removed.', po_call_args[0][0][0])

        po_call_args = mock_input.call_args_list
        self.assertEqual(2, len(po_call_args))
        self.assertEqual('Are you sure you want to delete this Scheduler? [y/n]: ', po_call_args[0][0][0])
        self.assertEqual('Please enter either "y" or "n": ', po_call_args[1][0][0])

    @mock.patch('__builtin__.raw_input')
    @mock.patch('tethys_apps.cli.scheduler_commands.pretty_output')
    @mock.patch('tethys_apps.cli.scheduler_commands.exit')
    @mock.patch('tethys_compute.models.Scheduler')
    def test_schedulers_remove_command_no_force_proceed(self, mock_scheduler, mock_exit, mock_pretty_output,
                                                        mock_input):
        mock_args = mock.MagicMock()
        mock_args.force = False
        mock_input.side_effect = ['Y']
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, schedulers_remove_command, mock_args)

        mock_scheduler.objects.get.assert_called()
        mock_scheduler.objects.get().delete.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('Successfully removed Scheduler', po_call_args[0][0][0])

        po_call_args = mock_input.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual('Are you sure you want to delete this Scheduler? [y/n]: ', po_call_args[0][0][0])

    @mock.patch('__builtin__.raw_input')
    @mock.patch('tethys_apps.cli.scheduler_commands.pretty_output')
    @mock.patch('tethys_apps.cli.scheduler_commands.exit')
    @mock.patch('tethys_compute.models.Scheduler')
    def test_schedulers_remove_command_no_force_no_proceed(self, mock_scheduler, mock_exit, mock_pretty_output,
                                                           mock_input):
        mock_args = mock.MagicMock()
        mock_args.force = False
        mock_input.side_effect = ['N']
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, schedulers_remove_command, mock_args)

        mock_scheduler.objects.get.assert_called()
        mock_scheduler.objects.get().delete.assert_not_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual('Aborted. Scheduler not removed.', po_call_args[0][0][0])

        po_call_args = mock_input.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual('Are you sure you want to delete this Scheduler? [y/n]: ', po_call_args[0][0][0])

    @mock.patch('tethys_apps.cli.scheduler_commands.pretty_output')
    @mock.patch('tethys_apps.cli.scheduler_commands.exit')
    @mock.patch('tethys_compute.models.Scheduler')
    def test_schedulers_remove_command_does_not_exist(self, mock_scheduler, mock_exit, mock_pretty_output):
        mock_args = mock.MagicMock()
        mock_scheduler.objects.get.side_effect = ObjectDoesNotExist
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, schedulers_remove_command, mock_args)

        mock_scheduler.objects.get.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('Command aborted.', po_call_args[0][0][0])
