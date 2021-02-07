from tethys_sdk.testing import TethysTestCase
from tethys_compute.models.condor.condor_scheduler import CondorScheduler
from tethys_compute.models.condor.condor_base import CondorBase
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from unittest import mock


class CondorBaseTest(TethysTestCase):
    def set_up(self):
        self.user = User.objects.create_user('tethys_super', 'user@example.com', 'pass')

        self.scheduler = CondorScheduler(
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

    @mock.patch('tethys_compute.models.condor.condor_base.CondorBase._condor_object')
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

    @mock.patch('tethys_compute.models.condor.condor_base.CondorBase.condor_object')
    def test_statuses_prop(self, mock_co):
        mock_co.statuses = 'test_statuses'

        condor_obj = CondorBase.objects.get(name='test_condorbase')

        # to set updated inside if statement = False
        d = timezone.now() - timedelta(days=1)
        condor_obj._last_status_update = d

        # Execute
        ret = condor_obj.statuses

        # Check result
        self.assertEqual('test_statuses', ret)

        # to set updated inside if statement = True
        d = timezone.now()
        condor_obj._last_status_update = d

        mock_co.statuses = 'test_statuses2'
        ret = condor_obj.statuses

        # Check result, should not set statuses from condor_object again. Same ret as previous.
        self.assertEqual('test_statuses', ret)

    @mock.patch('tethys_compute.models.condor.condor_base.CondorBase.condor_object')
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

    @mock.patch('tethys_compute.models.condor.condor_base.CondorBase.condor_object')
    def test_update_status(self, mock_co):
        mock_co.status = 'Various'
        mock_co.statuses = {'Unexpanded': '', 'Idle': '', 'Running': ''}
        CondorBase.objects.get(name='test_condorbase_exe')._update_status()

        ret = CondorBase.objects.get(name='test_condorbase_exe')._status

        # Check result
        self.assertEqual('VCP', ret)

    @mock.patch('tethys_compute.models.condor.condor_base.CondorBase.condor_object')
    def test_update_status_exception(self, mock_co):
        mock_co.status = 'Various'
        mock_co.statuses = {}
        CondorBase.objects.get(name='test_condorbase_exe')._update_status()

        ret = CondorBase.objects.get(name='test_condorbase_exe')._status

        # Check result
        self.assertEqual('ERR', ret)

    @mock.patch('tethys_compute.models.condor.condor_base.CondorBase.condor_object')
    def test_process_results(self, mock_co):
        CondorBase.objects.get(name='test_condorbase_exe')._process_results()

        # Check result
        mock_co.sync_remote_output.assert_called()
        mock_co.close_remote.assert_called()

    @mock.patch('tethys_compute.models.condor.condor_base.CondorBase.condor_object')
    def test_stop(self, mock_co):
        CondorBase.objects.get(name='test_condorbase_exe').stop()

        # Check result
        mock_co.remove.assert_called()

    @mock.patch('tethys_compute.models.condor.condor_base.CondorBase.save')
    @mock.patch('tethys_compute.models.condor.condor_base.CondorBase.condor_object')
    def test_resubmit(self, mock_co, _):
        CondorBase.objects.get(name='test_condorbase')._resubmit()

        # Check result
        mock_co.close_remote.assert_called()

    @mock.patch('tethys_compute.models.condor.condor_base.Path')
    def test_read_file(self, mock_path):
        mock_path().is_file.return_value = True
        read_result = mock.MagicMock()
        mock_path().open().__enter__().read.return_value = read_result
        log_content = CondorBase.read_file('File')
        mock_path().open().__enter__().read.assert_called_once()
        self.assertEqual(log_content, read_result)

    @mock.patch('tethys_compute.models.condor.condor_base.Path')
    def test_read_file_no_file(self, mock_path):
        mock_path().is_file.return_value = False
        log_content = CondorBase.read_file('File')
        expected_result = 'File does not exist'
        self.assertEqual(expected_result, log_content)

    @mock.patch('tethys_compute.models.condor.condor_base.log')
    @mock.patch('tethys_compute.models.condor.condor_base.Path')
    def test_read_file_exception(self, mock_path, mock_log):
        mock_path().is_file.side_effect = Exception()
        log_content = CondorBase.read_file('File')
        expected_result = 'There was an error while reading File'
        self.assertEqual(expected_result, log_content)
        mock_log.exception.assert_called_once()

    @mock.patch('tethys_compute.models.condor.condor_base.CondorBase._get_logs_from_workspace')
    @mock.patch('tethys_compute.models.condor.condor_base.CondorBase._get_logs_from_remote')
    @mock.patch('tethys_compute.models.condor.condor_base.CondorBase._log_files')
    def test_get_logs_no_remote(self, mock_log_files, mock_log_remote, mock_log_workspace):
        logs_file = {'workflow': 'Model_Run.dag.dagman.out',
                     'test_job': {'log': 'test_job/logs/*.log',
                                  'error': 'test_job/logs/*.err',
                                  'output': 'test_job/logs/*.out'}
                     }
        logs_file_contents = {'workspace': '', 'test_job': {'log': '', 'error': '', 'output': ''}}
        mock_log_files.return_value = logs_file
        mock_log_remote.return_value = logs_file_contents
        expected_return = 'log_from_workspace'
        mock_log_workspace.return_value = expected_return

        logs = CondorBase.objects.get(name='test_condorbase')._get_logs()
        self.assertEqual(expected_return, logs)

    @mock.patch('tethys_compute.models.condor.condor_base.partial')
    def test_get_logs_from_remote(self, mock_partial):
        mock_func = mock.MagicMock()
        mock_partial.return_value = mock_func
        log_files = {'workflow': 'test_name.dag.dagman.out',
                     'test_job1': {'log': 'test_job1/logs/*.log',
                                   'error': 'test_job1/logs/*.err',
                                   'output': 'test_job1/logs/*.out'}}
        expected_value = {'workflow': mock_func,
                          'test_job1': {
                              'log': mock_func,
                              'error': mock_func,
                              'output': mock_func
                          }}
        # Execute
        ret = self.condorbase._get_logs_from_remote(log_files)
        self.assertEqual(expected_value, ret)

    @mock.patch('tethys_compute.models.condor.condor_base.CondorBase._get_logs_from_workspace')
    @mock.patch('tethys_compute.models.condor.condor_base.CondorBase._get_logs_from_remote')
    @mock.patch('tethys_compute.models.condor.condor_base.CondorBase._log_files')
    def test_get_logs_remote(self, mock_log_files, mock_log_remote, mock_log_workspace):
        logs_file = {'workflow': 'Model_Run.dag.dagman.out',
                     'test_job': {'log': 'test_job/logs/*.log',
                                  'error': 'test_job/logs/*.err',
                                  'output': 'test_job/logs/*.out'}
                     }
        logs_file_contents = {'workspace': 'has_content', 'test_job': {'log': '', 'error': '', 'output': ''}}
        mock_log_files.return_value = logs_file
        mock_log_remote.return_value = logs_file_contents
        mock_log_workspace.return_value = 'log_from_workspace'

        logs = CondorBase.objects.get(name='test_condorbase')._get_logs()

        self.assertEqual(logs_file_contents, logs)

    @mock.patch('tethys_compute.models.condor.condor_base.CondorBase._get_logs_from_workspace')
    @mock.patch('tethys_compute.models.condor.condor_base.CondorBase._get_logs_from_remote')
    @mock.patch('tethys_compute.models.condor.condor_base.CondorBase._log_files')
    def test_get_logs_remote_check_child(self, mock_log_files, mock_log_remote, mock_log_workspace):
        logs_file = {'workflow': 'Model_Run.dag.dagman.out',
                     'test_job': {'log': 'test_job/logs/*.log',
                                  'error': 'test_job/logs/*.err',
                                  'output': 'test_job/logs/*.out'}
                     }
        logs_file_contents = {'workspace': '', 'test_job': {'log': 'has_content', 'error': '', 'output': ''}}
        mock_log_files.return_value = logs_file
        mock_log_remote.return_value = logs_file_contents
        mock_log_workspace.return_value = 'log_from_workspace'

        logs = CondorBase.objects.get(name='test_condorbase')._get_logs()

        self.assertEqual(logs_file_contents, logs)

    @mock.patch('builtins.open')
    @mock.patch('tethys_compute.models.condor.condor_base.os.listdir')
    @mock.patch('tethys_compute.models.condor.condor_base.os.path.isdir')
    @mock.patch('tethys_compute.models.condor.condor_base.os.path.isfile')
    def test_get_logs_from_workspace_mock_file(self, mock_isfile, mock_isdir, mock_list_dir, mock_open):
        mock_isfile.return_value = True
        mock_isdir.return_value = True
        mock_list_dir.return_value = ['file1.log', 'file2.err', 'file3.out']
        logs_file = {'workflow': 'Model_Run.dag.dagman.out',
                     'test_job': {'log': 'test_job/logs/*.log',
                                  'error': 'test_job/logs/*.err',
                                  'output': 'test_job/logs/*.out'}
                     }
        logs = CondorBase.objects.get(name='test_condorbase')._get_logs_from_workspace(logs_file)

        self.assertIsNotNone(logs['workflow'])
        self.assertIsNotNone(logs['test_job']['log'])
        self.assertIsNotNone(logs['test_job']['error'])
        self.assertIsNotNone(logs['test_job']['output'])

    def test_pause(self):
        ret = CondorBase.objects.get(name='test_condorbase_exe').pause()

        # Check result
        self.assertIsNone(ret)

    def test_resume(self):
        ret = CondorBase.objects.get(name='test_condorbase_exe').resume()

        # Check result
        self.assertIsNone(ret)

    @mock.patch('tethys_compute.models.condor.condor_base.CondorBase._condor_object')
    def test_update_database_fields(self, mock_co):
        mock_co._remote_id = 'test_update_remote_id'
        ret = CondorBase.objects.get(name='test_condorbase_exe')
        ret.remote_id = None

        # _condor_object is an abstract method returning a condorpyjob or condorpyworkflow.
        #  We'll test condor_object.remote_id in condorpyjob test
        ret.update_database_fields()

        # Check result
        self.assertEqual('test_update_remote_id', ret.remote_id)

    def test_abs_method(self):
        # Resubmit
        ret = CondorBase.objects.get(name='test_condorbase')._log_files()

        # Check result
        self.assertIsNone(ret)

    @mock.patch('tethys_compute.models.condor.condor_base.CondorBase.condor_object')
    def test_get_log_content(self, mock_co):
        mock_co._execute.return_value = ('test_out', 'test_err')
        self.condorbase.get_log_content('log_file')
        mock_co._execute.assert_called_with(['cat', 'log_file'])
