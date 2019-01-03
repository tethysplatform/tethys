from tethys_sdk.testing import TethysTestCase
from tethys_compute.models import TethysJob, CondorBase, Scheduler
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from pytz import timezone
from django.utils import timezone as dt
import mock


def test_function():
    pass


class TethysJobTest(TethysTestCase):
    def set_up(self):
        self.tz = timezone('America/Denver')

        self.user = User.objects.create_user('tethys_super', 'user@example.com', 'pass')

        self.scheduler = Scheduler(
            name='test_scheduler',
            host='localhost',
            username='tethys_super',
            password='pass',
            private_key_path='test_path',
            private_key_pass='test_pass'
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

    def test_run_time_execute_time_prop(self):
        ret = TethysJob.objects.get(name='test_tethysjob_execute_time').run_time

        # Check result
        self.assertIsInstance(ret, timedelta)
        self.assertEqual(timedelta(0, 3600), ret)

        # TODO: How to get to inside the if self.completion_time and self.execute_time: statement

    def test_execute(self):
        ret_old = TethysJob.objects.get(name='test_tethysjob_execute_time')
        TethysJob.objects.get(name='test_tethysjob_execute_time').execute()
        ret_new = TethysJob.objects.get(name='test_tethysjob_execute_time')

        self.assertNotEqual(ret_old.execute_time, ret_new.execute_time)
        self.assertEqual('Various', ret_old.status)
        self.assertEqual('Pending', ret_new.status)

    @mock.patch('tethys_compute.models.CondorBase.condor_object')
    def test_update_status_run(self, mock_co):
        tethysjob = CondorBase(
            name='test_tethysjob',
            description='test_description',
            user=self.user,
            label='test_label',
            scheduler=self.scheduler,
            execute_time=dt.now(),
        )

        mock_co.status = 'Running'
        tethysjob.update_status()

        # Check result
        self.assertIsNotNone(tethysjob.last_status_update)
        self.assertIsInstance(tethysjob.last_status_update, datetime)
        self.assertIsNotNone(tethysjob.start_time)
        self.assertIsInstance(tethysjob.start_time, datetime)

    @mock.patch('tethys_compute.models.CondorBase.condor_object')
    def test_update_status_com(self, mock_co):
        tethysjob = CondorBase(
            name='test_tethysjob',
            description='test_description',
            user=self.user,
            label='test_label',
            scheduler=self.scheduler,
            execute_time=dt.now(),
        )

        mock_co.status = 'Completed'
        tethysjob.update_status()

        # Check result
        self.assertIsNotNone(tethysjob.last_status_update)
        self.assertIsInstance(tethysjob.last_status_update, datetime)
        self.assertIsNotNone(tethysjob.completion_time)
        self.assertIsInstance(tethysjob.completion_time, datetime)

    @mock.patch('tethys_compute.models.CondorBase.condor_object')
    def test_update_status_vcp(self, mock_co):
        tethysjob = CondorBase(
            name='test_tethysjob',
            description='test_description',
            user=self.user,
            label='test_label',
            scheduler=self.scheduler,
            execute_time=dt.now(),
        )

        mock_co.status = 'Various-Complete'
        tethysjob.update_status()

        # Check result
        self.assertIsNotNone(tethysjob.last_status_update)
        self.assertIsInstance(tethysjob.last_status_update, datetime)
        self.assertIsNotNone(tethysjob.completion_time)
        self.assertIsInstance(tethysjob.completion_time, datetime)

    @mock.patch('tethys_compute.models.CondorBase.condor_object')
    def test_update_status_err(self, mock_co):
        tethysjob = CondorBase(
            name='test_tethysjob',
            description='test_description',
            user=self.user,
            label='test_label',
            scheduler=self.scheduler,
            execute_time=dt.now(),
        )

        mock_co.status = 'Held'
        tethysjob.update_status()

        # Check result
        self.assertIsNotNone(tethysjob.last_status_update)
        self.assertIsInstance(tethysjob.last_status_update, datetime)
        self.assertIsNotNone(tethysjob.completion_time)
        self.assertIsInstance(tethysjob.completion_time, datetime)

    @mock.patch('tethys_compute.models.CondorBase.condor_object')
    def test_update_status_abt(self, mock_co):
        tethysjob = CondorBase(
            name='test_tethysjob',
            description='test_description',
            user=self.user,
            label='test_label',
            scheduler=self.scheduler,
            execute_time=dt.now(),
        )

        mock_co.status = 'Removed'
        tethysjob.update_status()

        # Check result
        self.assertIsNotNone(tethysjob.last_status_update)
        self.assertIsInstance(tethysjob.last_status_update, datetime)
        self.assertIsNotNone(tethysjob.completion_time)
        self.assertIsInstance(tethysjob.completion_time, datetime)

    @mock.patch('tethys_compute.models.TethysFunctionExtractor')
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

    def test_process_results(self):
        ret = TethysJob.objects.get(name='test_tethysjob')

        ret.process_results('test', name='test_name')

        # Check result
        self.assertIsInstance(ret.completion_time, datetime)
        self.assertIsNotNone(ret.completion_time)

    def test_abs_method(self):
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

        self.assertRaises(NotImplementedError, TethysJob.objects.get(name='test_tethysjob').stop)

        self.assertRaises(NotImplementedError, TethysJob.objects.get(name='test_tethysjob').pause)

        self.assertRaises(NotImplementedError, TethysJob.objects.get(name='test_tethysjob').resume)
