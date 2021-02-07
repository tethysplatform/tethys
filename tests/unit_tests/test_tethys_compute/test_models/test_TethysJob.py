from tethys_sdk.testing import TethysTestCase
from tethys_compute.models.tethys_job import TethysJob
from tethys_compute.models.condor.condor_base import CondorBase
from tethys_compute.models.condor.condor_scheduler import CondorScheduler
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from pytz import timezone as pytz_timezone
from django.utils import timezone as django_timezone
from unittest import mock


def test_function():
    pass


class TethysJobTest(TethysTestCase):
    def set_up(self):
        self.tz = pytz_timezone('America/Denver')

        self.user = User.objects.create_user('tethys_super', 'user@example.com', 'pass')

        self.scheduler = CondorScheduler(
            name='test_scheduler',
            host='localhost',
        )

        self.scheduler.save()

        self.tethysjob = TethysJob(
            name='test_tethysjob',
            description='test_description',
            user=self.user,
            label='test_label',
        )
        self.tethysjob.save()

        self.tethysjob_execute_time = TethysJob(
            name='test_tethysjob_execute_time',
            description='test_description',
            user=self.user,
            label='test_label',
            execute_time=datetime(year=2018, month=1, day=1, tzinfo=self.tz),
            completion_time=datetime(year=2018, month=1, day=1, hour=1, tzinfo=self.tz),
            _status='VAR',
            _process_results_function=test_function

        )
        self.tethysjob_execute_time.save()

    def tear_down(self):
        self.tethysjob.delete()
        self.tethysjob_execute_time.delete()
        self.scheduler.delete()

    def test_type(self):
        ret = self.tethysjob.type
        self.assertEqual('TethysJob', ret)

    def test_update_status_interval_prop(self):
        ret = TethysJob.objects.get(name='test_tethysjob').update_status_interval

        # Check result
        self.assertIsInstance(ret, timedelta)
        self.assertEqual(timedelta(0, 10), ret)

    def test_last_status_update_prop(self):
        ret = TethysJob.objects.get(name='test_tethysjob')
        check_date = datetime(year=2018, month=1, day=1, tzinfo=self.tz)
        ret._last_status_update = check_date

        # Check result
        self.assertEqual(check_date, ret.last_status_update)

    def test_status_prop(self):
        ret = TethysJob.objects.get(name='test_tethysjob').status

        # Check result
        self.assertEqual('Pending', ret)

    def test_status_setter_prop(self):
        ret = TethysJob.objects.get(name='test_tethysjob_execute_time').status

        # Check result
        self.assertEqual('Various', ret)

    @mock.patch('tethys_compute.models.tethys_job.TethysJob.update_status')
    def test_status_setter(self, mock_update):
        tethys_job = TethysJob.objects.get(name='test_tethysjob')

        tethys_job.status = 'test_status'

        # Check result
        mock_update.assert_called_with(status='test_status')

    def test_run_time_execute_time_prop(self):
        ret = TethysJob.objects.get(name='test_tethysjob_execute_time').run_time

        # Check result
        self.assertIsInstance(ret, timedelta)
        self.assertEqual(timedelta(0, 3600), ret)

    def test_run_time_execute_time_prop_with_start_time(self):
        ret = TethysJob.objects.get(name='test_tethysjob').run_time

        # Check result
        self.assertEqual('', ret)

    def test_run_time_execute_time_no_start_time_prop(self):
        ret = TethysJob.objects.get(name='test_tethysjob').run_time

        # Check result
        self.assertEqual("", ret)

    def test_execute(self):
        ret_old = TethysJob.objects.get(name='test_tethysjob_execute_time')
        TethysJob.objects.get(name='test_tethysjob_execute_time').execute()
        ret_new = TethysJob.objects.get(name='test_tethysjob_execute_time')

        self.assertNotEqual(ret_old.execute_time, ret_new.execute_time)
        self.assertEqual('Various', ret_old.status)
        self.assertEqual('Submitted', ret_new.status)

    @mock.patch('tethys_compute.models.tethys_job.TethysJob._execute')
    def test_execute_with_error(self, mock__execute):
        mock__execute.side_effect = Exception
        TethysJob.objects.get(name='test_tethysjob_execute_time').execute()
        status = TethysJob.objects.get(name='test_tethysjob_execute_time').status

        self.assertEqual('Error', status)

    @mock.patch('tethys_compute.models.tethys_job.log')
    def test_update_status_invalid(self, mock_log):
        tethysjob = TethysJob(
            name='test_tethysjob',
            description='test_description',
            user=self.user,
            label='test_label',
            execute_time=django_timezone.now(),
        )
        tethysjob._status = ''

        # Check result
        self.assertIsNone(tethysjob.update_status('Test'))
        mock_log.error.assert_called_with('Invalid status given: Test')

    @mock.patch('tethys_compute.models.tethys_job.TethysJob.is_time_to_update')
    @mock.patch('tethys_compute.models.condor.condor_base.CondorBase.condor_object')
    def test_update_status_run(self, mock_co, mock_tup):
        tethysjob = CondorBase(
            name='test_tethysjob',
            description='test_description',
            user=self.user,
            label='test_label',
            scheduler=self.scheduler,
            execute_time=django_timezone.now(),
        )
        mock_tup.return_value = True
        mock_co.status = 'Running'
        tethysjob.update_status()

        # Check result
        self.assertIsNotNone(tethysjob.last_status_update)
        self.assertIsInstance(tethysjob.last_status_update, datetime)
        self.assertIsNotNone(tethysjob.start_time)
        self.assertIsInstance(tethysjob.start_time, datetime)

    @mock.patch('tethys_compute.models.tethys_job.log')
    def test_update_bad_status(self, mock_log):
        tethys_job = TethysJob.objects.get(name='test_tethysjob')
        tethys_job.update_status(status='test')

        mock_log.error.assert_called_with('Invalid status given: test')

    @mock.patch('django.db.models.base.Model.save')
    def test_update_valid_status(self, mock_save):
        tethys_job = TethysJob.objects.get(name='test_tethysjob')
        tethys_job.update_status(status='PEN')
        mock_save.assert_called()

    @mock.patch('tethys_compute.models.tethys_job.TethysJob.is_time_to_update')
    @mock.patch('tethys_compute.models.condor.condor_base.CondorBase.condor_object')
    def test_update_status_com(self, mock_co, mock_tup):
        tethysjob = CondorBase(
            name='test_tethysjob',
            description='test_description',
            user=self.user,
            label='test_label',
            scheduler=self.scheduler,
            execute_time=django_timezone.now(),
        )

        mock_tup.return_value = True
        mock_co.status = 'Completed'
        tethysjob.update_status()

        # Check result
        self.assertIsNotNone(tethysjob.last_status_update)
        self.assertIsInstance(tethysjob.last_status_update, datetime)
        self.assertIsNotNone(tethysjob.completion_time)
        self.assertIsInstance(tethysjob.completion_time, datetime)

    @mock.patch('tethys_compute.models.tethys_job.TethysJob.is_time_to_update')
    @mock.patch('tethys_compute.models.condor.condor_base.CondorBase.condor_object')
    def test_update_status_vcp(self, mock_co, mock_tup):
        tethysjob = CondorBase(
            name='test_tethysjob',
            description='test_description',
            user=self.user,
            label='test_label',
            scheduler=self.scheduler,
            execute_time=django_timezone.now(),
        )
        mock_tup.return_value = True
        mock_co.status = 'Various-Complete'
        tethysjob.update_status()

        # Check result
        self.assertIsNotNone(tethysjob.last_status_update)
        self.assertIsInstance(tethysjob.last_status_update, datetime)
        self.assertIsNotNone(tethysjob.completion_time)
        self.assertIsInstance(tethysjob.completion_time, datetime)

    @mock.patch('tethys_compute.models.tethys_job.TethysJob.is_time_to_update')
    @mock.patch('tethys_compute.models.condor.condor_base.CondorBase.condor_object')
    def test_update_status_err(self, mock_co, mock_tup):
        tethysjob = CondorBase(
            name='test_tethysjob',
            description='test_description',
            user=self.user,
            label='test_label',
            scheduler=self.scheduler,
            execute_time=django_timezone.now(),
        )

        mock_co.status = 'Held'
        mock_tup.return_value = True
        tethysjob.update_status()

        # Check result
        self.assertIsNotNone(tethysjob.last_status_update)
        self.assertIsInstance(tethysjob.last_status_update, datetime)
        self.assertIsNotNone(tethysjob.completion_time)
        self.assertIsInstance(tethysjob.completion_time, datetime)

    @mock.patch('tethys_compute.models.tethys_job.TethysJob.is_time_to_update')
    @mock.patch('tethys_compute.models.condor.condor_base.CondorBase.condor_object')
    def test_update_status_abt(self, mock_co, mock_tup):
        tethysjob = CondorBase(
            name='test_tethysjob',
            description='test_description',
            user=self.user,
            label='test_label',
            scheduler=self.scheduler,
            execute_time=django_timezone.now(),
        )
        mock_tup.return_value = True

        mock_co.status = 'Removed'
        tethysjob.update_status()

        # Check result
        self.assertIsNotNone(tethysjob.last_status_update)
        self.assertIsInstance(tethysjob.last_status_update, datetime)
        self.assertIsNotNone(tethysjob.completion_time)
        self.assertIsInstance(tethysjob.completion_time, datetime)

    @mock.patch('tethys_compute.models.tethys_job.TethysFunctionExtractor')
    def test_process_results_function(self, mock_tfe):
        mock_tfe().valid = True
        mock_tfe().function = 'test_function_return'

        # Setter
        TethysJob.objects.get(name='test_tethysjob_execute_time').process_results_function = test_function

        # Property
        ret = TethysJob.objects.get(name='test_tethysjob_execute_time').process_results_function

        # Check result
        self.assertEqual(ret, 'test_function_return')
        mock_tfe.assert_called_with(str(test_function), None)

    @mock.patch('tethys_compute.models.tethys_job.TethysFunctionExtractor')
    def test_process_results_function_string_input(self, mock_tfe):
        mock_tfe().valid = True
        mock_tfe().function = 'test_function_return'

        # Setter
        TethysJob.objects.get(name='test_tethysjob_execute_time').process_results_function = 'tests.unit_tests.' \
                                                                                             'test_tethys_compute.' \
                                                                                             'test_models.' \
                                                                                             'test_TethysJob.' \
                                                                                             'test_function'

        # Property
        ret = TethysJob.objects.get(name='test_tethysjob_execute_time').process_results_function

        # Check result
        self.assertEqual(ret, 'test_function_return')
        mock_tfe.assert_called_with(str(test_function), None)

    def test_process_results(self):
        ret = TethysJob.objects.get(name='test_tethysjob')

        ret.process_results('test', name='test_name')

        # Check result
        self.assertIsInstance(ret.completion_time, datetime)
        self.assertIsNotNone(ret.completion_time)

    @mock.patch('tethys_compute.models.tethys_job.TethysJob._resubmit')
    def test_resubmit(self, mock__resubmit):
        ret = TethysJob.objects.get(name='test_tethysjob')

        ret.resubmit()

        # Check result
        mock__resubmit.assert_called()

    @mock.patch('tethys_compute.models.tethys_job.TethysJob._get_logs')
    def test_get_logs(self, mock__get_logs):
        ret = TethysJob.objects.get(name='test_tethysjob')

        ret.get_logs()

        # Check result
        mock__get_logs.assert_called()

    def test_abs_method(self):
        # Resubmit
        ret = TethysJob.objects.get(name='test_tethysjob')._resubmit()

        # Check result
        self.assertIsNone(ret)

        # Execute
        ret = TethysJob.objects.get(name='test_tethysjob')._execute()

        # Check result
        self.assertIsNone(ret)

        # Update Status
        ret = TethysJob.objects.get(name='test_tethysjob')._update_status()

        # Check result
        self.assertIsNone(ret)

        # Execute
        ret = TethysJob.objects.get(name='test_tethysjob')._process_results()

        # Check result
        self.assertIsNone(ret)

        # Check get logs
        ret = TethysJob.objects.get(name='test_tethysjob')._get_logs()

        # Check result
        self.assertIsNone(ret)

        self.assertRaises(NotImplementedError, TethysJob.objects.get(name='test_tethysjob').stop)

        self.assertRaises(NotImplementedError, TethysJob.objects.get(name='test_tethysjob').pause)

        self.assertRaises(NotImplementedError, TethysJob.objects.get(name='test_tethysjob').resume)

    def test_is_time_to_update(self):
        ret = TethysJob.objects.get(name='test_tethysjob')
        ret._update_status_interval = timedelta(seconds=0)

        fifteen_ago = django_timezone.now() - timedelta(minutes=15)
        ret._last_status_update = fifteen_ago

        time_to_update_status = ret.is_time_to_update()

        self.assertTrue(time_to_update_status)

    def test_is_time_to_update_false(self):
        ret = TethysJob.objects.get(name='test_tethysjob')
        ret._update_status_interval = timedelta(minutes=15)

        fifteen_ago = django_timezone.now() - timedelta(minutes=5)
        ret._last_status_update = fifteen_ago

        time_to_update_status = ret.is_time_to_update()

        self.assertFalse(time_to_update_status)

    def test_lt(self):
        ret = sorted((self.tethysjob, self.tethysjob_execute_time))
        expected_value = [self.tethysjob, self.tethysjob_execute_time]
        self.assertListEqual(ret, expected_value)
