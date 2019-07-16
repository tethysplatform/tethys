import unittest
from unittest import mock

from tethys_cli.scheduler_commands import dask_scheduler_create_command, schedulers_list_command, \
    schedulers_remove_command, condor_scheduler_create_command

from django.core.exceptions import ObjectDoesNotExist


class SchedulerCommandsTest(unittest.TestCase):

    def setUp(self):
        load_apps_patcher = mock.patch('tethys_cli.scheduler_commands.load_apps')
        load_apps_patcher.start()
        self.addCleanup(load_apps_patcher.stop)

    def tearDown(self):
        pass

    @mock.patch('tethys_cli.scheduler_commands.pretty_output')
    @mock.patch('tethys_cli.scheduler_commands.exit')
    @mock.patch('tethys_compute.models.condor.condor_scheduler.CondorScheduler')
    def test_condor_scheduler_create_command(self, mock_scheduler, mock_exit, mock_pretty_output):
        """
        Test for condor_scheduler_create_command.
        Runs through and saves.
        :param mock_scheduler:  mock for Scheduler
        :param mock_exit:  mock for handling exit() code in function
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock()
        mock_scheduler.objects.filter().first.return_value = False
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, condor_scheduler_create_command, mock_args)

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
        self.assertEqual('Condor Scheduler created successfully!', po_call_args[0][0][0])
        mock_exit.assert_called_with(0)

    @mock.patch('tethys_cli.scheduler_commands.pretty_output')
    @mock.patch('tethys_cli.scheduler_commands.exit')
    @mock.patch('tethys_compute.models.condor.condor_scheduler.CondorScheduler')
    def test_condor_scheduler_create_command_existing_scheduler(self, mock_scheduler, mock_exit, mock_pretty_output):
        """
        Test for condor_scheduler_create_command.
        For when a scheduler already exists.
        :param mock_scheduler:  mock for Scheduler
        :param mock_exit:  mock for handling exit() code in function
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock()
        mock_scheduler.objects.filter().first.return_value = True
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, condor_scheduler_create_command, mock_args)

        mock_scheduler.objects.filter.assert_called()
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn('already exists', po_call_args[0][0][0])
        mock_exit.assert_called_with(0)

    @mock.patch('tethys_cli.scheduler_commands.pretty_output')
    @mock.patch('tethys_compute.models.condor.condor_scheduler.CondorScheduler')
    def test_condor_schedulers_list_command(self, mock_scheduler, mock_pretty_output):
        """
        Test for condor_schedulers_list_command.
        For use with multiple schedulers.
        :param mock_scheduler:  mock for Scheduler
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_scheduler1 = mock.MagicMock(name='test1')
        mock_scheduler1.name = 'test_name1'
        mock_scheduler1.host = 'test_host1'
        mock_scheduler1.username = 'test_user1'
        mock_scheduler1.private_key_path = 'test_path1'
        mock_scheduler1.private_key_pass = 'test_private_key_path1'
        mock_scheduler2 = mock.MagicMock()
        mock_scheduler2.name = 'test_name2'
        mock_scheduler2.host = 'test_host2'
        mock_scheduler2.username = 'test_user2'
        mock_scheduler2.private_key_path = 'test_path2'
        mock_scheduler2.private_key_pass = 'test_private_key_path2'
        mock_scheduler.objects.all.return_value = [mock_scheduler1, mock_scheduler2]

        mock_args = mock.MagicMock(type='condor')

        # Call the function
        schedulers_list_command(mock_args)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list

        self.assertEqual(3, len(po_call_args))
        self.assertIn('Name', po_call_args[0][0][0])
        self.assertIn('Host', po_call_args[0][0][0])
        self.assertIn('Username', po_call_args[0][0][0])
        self.assertIn('Password', po_call_args[0][0][0])
        self.assertIn('Private Key Path', po_call_args[0][0][0])
        self.assertIn('Private Key Pass', po_call_args[0][0][0])

    @mock.patch('tethys_cli.scheduler_commands.pretty_output')
    @mock.patch('tethys_compute.models.condor.condor_scheduler.CondorScheduler')
    def test_condor_schedulers_list_command_no_schedulers(self, mock_scheduler, mock_pretty_output):
        """
        Test for condor_schedulers_list_command.
        For use with no schedulers.
        :param mock_scheduler:  mock for Scheduler
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_scheduler.objects.all.return_value = []
        mock_args = mock.MagicMock(type='condor')

        schedulers_list_command(mock_args)

        mock_scheduler.objects.all.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual('There are no Condor Schedulers registered in Tethys.', po_call_args[0][0][0])

    @mock.patch('tethys_cli.scheduler_commands.pretty_output')
    @mock.patch('tethys_cli.scheduler_commands.exit')
    @mock.patch('tethys_compute.models.Scheduler')
    def test_schedulers_remove_command_force(self, mock_scheduler, mock_exit, mock_pretty_output):
        """
        Test for condor_schedulers_remove_command.
        Runs through, forcing a delete
        :param mock_scheduler:  mock for Scheduler
        :param mock_exit:  mock for handling exit() code in function
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
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

    @mock.patch('tethys_cli.scheduler_commands.input')
    @mock.patch('tethys_cli.scheduler_commands.pretty_output')
    @mock.patch('tethys_cli.scheduler_commands.exit')
    @mock.patch('tethys_compute.models.Scheduler')
    def test_schedulers_remove_command_force_invalid_proceed_char(self, mock_scheduler, mock_exit, mock_pretty_output,
                                                                  mock_input):
        """
        Test for schedulers_remove_command.
        Runs through, not forcing a delete, and when prompted to delete, gives an invalid answer
        :param mock_scheduler:  mock for Scheduler
        :param mock_exit:  mock for handling exit() code in function
        :param mock_pretty_output:  mock for pretty_output text
        :param mock_input:  mock for handling raw_input requests
        :return:
        """
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

    @mock.patch('tethys_cli.scheduler_commands.input')
    @mock.patch('tethys_cli.scheduler_commands.pretty_output')
    @mock.patch('tethys_cli.scheduler_commands.exit')
    @mock.patch('tethys_compute.models.Scheduler')
    def test_schedulers_remove_command_no_force_proceed(self, mock_scheduler, mock_exit, mock_pretty_output,
                                                        mock_input):
        """
        Test for schedulers_remove_command.
        Runs through, not forcing a delete, and when prompted to delete, gives a valid answer to delete
        :param mock_scheduler:  mock for Scheduler
        :param mock_exit:  mock for handling exit() code in function
        :param mock_pretty_output:  mock for pretty_output text
        :param mock_input:  mock for handling raw_input requests
        :return:
        """
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

    @mock.patch('tethys_cli.scheduler_commands.input')
    @mock.patch('tethys_cli.scheduler_commands.pretty_output')
    @mock.patch('tethys_cli.scheduler_commands.exit')
    @mock.patch('tethys_compute.models.Scheduler')
    def test_schedulers_remove_command_no_force_no_proceed(self, mock_scheduler, mock_exit, mock_pretty_output,
                                                           mock_input):
        """
        Test for schedulers_remove_command.
        Runs through, not forcing a delete, and when prompted to delete, gives a valid answer to not delete
        :param mock_scheduler:  mock for Scheduler
        :param mock_exit:  mock for handling exit() code in function
        :param mock_pretty_output:  mock for pretty_output text
        :param mock_input:  mock for handling raw_input requests
        :return:
        """
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

    @mock.patch('tethys_cli.scheduler_commands.pretty_output')
    @mock.patch('tethys_cli.scheduler_commands.exit')
    @mock.patch('tethys_compute.models.Scheduler')
    def test_schedulers_remove_command_does_not_exist(self, mock_scheduler, mock_exit, mock_pretty_output):
        """
        Test for schedulers_remove_command.
        For handling the Scheduler throwing ObjectDoesNotExist
        :param mock_scheduler:  mock for Scheduler
        :param mock_exit:  mock for handling exit() code in function
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
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

    @mock.patch('tethys_cli.scheduler_commands.pretty_output')
    @mock.patch('tethys_cli.scheduler_commands.exit')
    @mock.patch('tethys_compute.models.dask.dask_scheduler.DaskScheduler')
    def test_dask_scheduler_create_command(self, mock_scheduler, mock_exit, mock_pretty_output):
        """
        Test for condor_scheduler_create_command.
        Runs through and saves.
        :param mock_scheduler:  mock for Scheduler
        :param mock_exit:  mock for handling exit() code in function
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock()
        mock_scheduler.objects.filter().first.return_value = False
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, dask_scheduler_create_command, mock_args)

        mock_scheduler.assert_called_with(
            name=mock_args.name,
            host=mock_args.endpoint,
            timeout=mock_args.timeout,
            heartbeat_interval=mock_args.heartbeat_interval,
            dashboard=mock_args.dashboard,
        )

        mock_scheduler().save.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual('Dask Scheduler created successfully!', po_call_args[0][0][0])
        mock_exit.assert_called_with(0)

    @mock.patch('tethys_cli.scheduler_commands.pretty_output')
    @mock.patch('tethys_cli.scheduler_commands.exit')
    @mock.patch('tethys_compute.models.dask.dask_scheduler.DaskScheduler')
    def test_dask_scheduler_create_command_existing_scheduler(self, mock_scheduler, mock_exit, mock_pretty_output):
        """
        Test for dask_scheduler_create_command.
        For when a scheduler already exists.
        :param mock_scheduler:  mock for Scheduler
        :param mock_exit:  mock for handling exit() code in function
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock()
        mock_scheduler.objects.filter().first.return_value = True
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, dask_scheduler_create_command, mock_args)

        mock_scheduler.objects.filter.assert_called()
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn('already exists', po_call_args[0][0][0])
        mock_exit.assert_called_with(0)

    @mock.patch('tethys_cli.scheduler_commands.pretty_output')
    @mock.patch('tethys_compute.models.dask.dask_scheduler.DaskScheduler')
    def test_dask_schedulers_list_command(self, mock_scheduler, mock_pretty_output):
        """
        Test for dask_schedulers_list_command.
        For use with multiple schedulers.
        :param mock_scheduler:  mock for Scheduler
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_scheduler1 = mock.MagicMock(name='test1')
        mock_scheduler1.name = 'test_name1'
        mock_scheduler1.host = 'test_host1'
        mock_scheduler1.timeout = 10
        mock_scheduler1.heartbeat_interval = 5
        mock_scheduler1.dashboard = 'test_dashboard1'
        mock_scheduler.objects.all.return_value = [mock_scheduler1]

        mock_args = mock.MagicMock(type='dask')

        schedulers_list_command(mock_args)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list

        self.assertEqual(2, len(po_call_args))
        self.assertIn('Name', po_call_args[0][0][0])
        self.assertIn('Host', po_call_args[0][0][0])
        self.assertIn('Timeout', po_call_args[0][0][0])
        self.assertIn('Heartbeat Interval', po_call_args[0][0][0])
        self.assertIn('Dashboard', po_call_args[0][0][0])
        self.assertIn('test_name1', po_call_args[1][0][0])
        self.assertIn('test_host1', po_call_args[1][0][0])
        self.assertIn('10', po_call_args[1][0][0])
        self.assertIn('5', po_call_args[1][0][0])
        self.assertIn('test_dashboard1', po_call_args[1][0][0])

    @mock.patch('tethys_cli.scheduler_commands.pretty_output')
    @mock.patch('tethys_compute.models.dask.dask_scheduler.DaskScheduler')
    def test_dask_schedulers_list_command_no_schedulers(self, mock_scheduler, mock_pretty_output):
        """
        Test for dask_schedulers_list_command.
        For use with no schedulers.
        :param mock_scheduler:  mock for Scheduler
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_scheduler.objects.all.return_value = []

        mock_args = mock.MagicMock(type='dask')

        schedulers_list_command(mock_args)

        mock_scheduler.objects.all.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual('There are no Dask Schedulers registered in Tethys.', po_call_args[0][0][0])
