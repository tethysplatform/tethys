from tethys_sdk.testing import TethysTestCase
from tethys_compute.models import Scheduler, CondorBase
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone
import mock


class CondorBaseTest(TethysTestCase):
    def set_up(self):
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

        self.condorbase = CondorBase(
            name='test_condorbase',
            description='test_description',
            user=self.user,
            label='test_label',
            cluster_id='1',
            remote_id='test_machine',
            scheduler=self.scheduler
        )
        self.condorbase.save()

        self.condorbase_exe = CondorBase(
            name='test_condorbase_exe',
            description='test_description',
            user=self.user,
            label='test_label',
            execute_time=timezone.now(),
            cluster_id='1',
            remote_id='test_machine',
            scheduler=self.scheduler
        )
        self.condorbase_exe.save()

    def tear_down(self):
        self.scheduler.delete()
        self.condorbase.delete()
        self.condorbase_exe.delete()

    @mock.patch('tethys_compute.models.CondorBase._condor_object')
    def test_condor_object_pro(self, mock_co):
        ret = CondorBase.objects.get(name='test_condorbase')
        mock_co.return_value = ret

        ret.condor_object

        # Check result
        self.assertEqual(mock_co, ret.condor_object)
        self.assertEqual(1, ret.condor_object._cluster_id)
        self.assertEqual('test_machine', ret.condor_object._remote_id)
        mock_co.set_scheduler.assert_called_with('localhost', 'tethys_super', 'pass', 'test_path', 'test_pass')

    def test_condor_obj_abs(self):
        ret = CondorBase.objects.get(name='test_condorbase')._condor_object()

        # Check result.
        self.assertIsNone(ret)

    @mock.patch('tethys_compute.models.CondorBase.condor_object')
    def test_statuses_prop(self, mock_co):
        mock_co.statuses = 'test_statuses'

        condor_obj = CondorBase.objects.get(name='test_condorbase')

        # to set updated inside if statement = False
        d = datetime.now() - timedelta(days=1)
        condor_obj._last_status_update = d

        # Execute
        ret = condor_obj.statuses

        # Check result
        self.assertEqual('test_statuses', ret)

        # to set updated inside if statement = True
        d = datetime.now()
        condor_obj._last_status_update = d

        mock_co.statuses = 'test_statuses2'
        ret = condor_obj.statuses

        # Check result, should not set statuses from condor_object again. Same ret as previous.
        self.assertEqual('test_statuses', ret)

    @mock.patch('tethys_compute.models.CondorBase.condor_object')
    def test_execute_abs(self, mock_co):
        mock_co.submit.return_value = 111

        # Execute
        CondorBase.objects.get(name='test_condorbase')._execute()

        ret = CondorBase.objects.get(name='test_condorbase')

        # Check result
        self.assertEqual(111, ret.cluster_id)

    def test_update_status_not_execute_time(self):
        ret = CondorBase.objects.get(name='test_condorbase')._update_status()

        # Check result
        self.assertEqual('PEN', ret)

    @mock.patch('tethys_compute.models.CondorBase.condor_object')
    def test_update_status(self, mock_co):
        mock_co.status = 'Various'
        mock_co.statuses = {'Unexpanded': '', 'Idle': '', 'Running': ''}
        CondorBase.objects.get(name='test_condorbase_exe')._update_status()

        ret = CondorBase.objects.get(name='test_condorbase_exe')._status

        # Check result
        self.assertEqual('VCP', ret)

    @mock.patch('tethys_compute.models.CondorBase.condor_object')
    def test_update_status_exception(self, mock_co):
        mock_co.status = 'Various'
        mock_co.statuses = {}
        CondorBase.objects.get(name='test_condorbase_exe')._update_status()

        ret = CondorBase.objects.get(name='test_condorbase_exe')._status

        # Check result
        self.assertEqual('ERR', ret)

    @mock.patch('tethys_compute.models.CondorBase.condor_object')
    def test_process_results(self, mock_co):
        CondorBase.objects.get(name='test_condorbase_exe')._process_results()

        # Check result
        mock_co.sync_remote_output.assert_called()
        mock_co.close_remote.assert_called()

    @mock.patch('tethys_compute.models.CondorBase.condor_object')
    def test_stop(self, mock_co):
        CondorBase.objects.get(name='test_condorbase_exe').stop()

        # Check result
        mock_co.remove.assert_called()

    def test_pause(self):
        ret = CondorBase.objects.get(name='test_condorbase_exe').pause()

        # Check result
        self.assertIsNone(ret)

    def test_resume(self):
        ret = CondorBase.objects.get(name='test_condorbase_exe').resume()

        # Check result
        self.assertIsNone(ret)

    @mock.patch('tethys_compute.models.CondorBase._condor_object')
    def test_update_database_fields(self, mock_co):
        mock_co._remote_id = 'test_update_remote_id'
        ret = CondorBase.objects.get(name='test_condorbase_exe')

        # _condor_object is an abstract method returning a condorpyjob or condorpyworkflow.
        #  We'll test condor_object.remote_id in condorpyjob test
        ret.update_database_fields()

        # Check result
        self.assertEqual('test_update_remote_id', ret.remote_id)
