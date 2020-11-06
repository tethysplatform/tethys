from tethys_sdk.testing import TethysTestCase
from tethys_compute.models.condor.condor_scheduler import CondorScheduler
from tethys_compute.models.condor.condor_py_workflow import CondorPyWorkflow
from tethys_compute.models.condor.condor_workflow_job_node import CondorWorkflowJobNode
from tethys_compute.models.condor.condor_workflow import CondorWorkflow
from django.contrib.auth.models import User
from django.utils import timezone as tz
from unittest import mock
import os
import shutil
import os.path


class CondorWorkflowTest(TethysTestCase):
    mock_nodes = mock.MagicMock()
    mock_nodes.name = 'test_job1'

    mock_condor_workflow = mock.MagicMock()
    mock_condor_workflow._execute.return_value = 'out', 'err'

    def set_up(self):
        test_models_dir = os.path.dirname(__file__)
        self.workspace_dir = os.path.join(test_models_dir, 'workspace')
        self.user = User.objects.create_user('tethys_super', 'user@example.com', 'pass')

        files_dir = os.path.join(os.path.dirname(test_models_dir), 'files')
        self.private_key = os.path.join(files_dir, 'keys', 'testkey')
        self.private_key_pass = 'password'

        self.scheduler = CondorScheduler(
            name='test_scheduler',
            host='localhost',
            username='tethys_super',
            password='pass',
            private_key_path=self.private_key,
            private_key_pass=self.private_key_pass
        )
        self.scheduler.save()

        self.condorworkflow = CondorWorkflow(
            _max_jobs={'foo': 10},
            _config='test_config',
            name='test name',
            workspace=self.workspace_dir,
            user=self.user,
            scheduler=self.scheduler,
        )
        self.condorworkflow.save()

        self.id_value = CondorWorkflow.objects.get(name='test name').condorpyworkflow_ptr_id
        self.condorpyworkflow = CondorPyWorkflow.objects.get(condorpyworkflow_id=self.id_value)

        self.condorworkflowjobnode_child = CondorWorkflowJobNode(
            name='Node_child',
            workflow=self.condorpyworkflow,
            _attributes={'test': 'one'},
            _num_jobs=1,
            _remote_input_files=['test1.txt'],
        )
        self.condorworkflowjobnode_child.save()

        self.condorworkflowjobnode = CondorWorkflowJobNode(
            name='Node_1',
            workflow=self.condorpyworkflow,
            _attributes={'test': 'one'},
            _num_jobs=1,
            _remote_input_files=['test1.txt'],
        )
        self.condorworkflowjobnode.save()

        # Django model many to many relationship add method
        self.condorworkflowjobnode.parent_nodes.add(self.condorworkflowjobnode_child)

        self.condorbase_id = CondorWorkflow.objects.get(name='test name').condorbase_ptr_id
        self.condorpyworkflow_id = CondorWorkflow.objects.get(name='test name').condorpyworkflow_ptr_id

    def tear_down(self):
        self.scheduler.delete()

        if self.condorworkflow.condorbase_ptr_id == self.condorbase_id:
            self.condorworkflow.delete()

        if os.path.exists(self.workspace_dir):
            shutil.rmtree(self.workspace_dir)

    def test_type(self):
        ret = self.condorworkflow.type
        self.assertEqual('CondorWorkflow', ret)

    def test_condor_object_prop(self):
        ret = self.condorworkflow._condor_object

        # Check workflow return
        self.assertEqual({'foo': 10}, ret.max_jobs)
        self.assertEqual('test_config', ret.config)
        self.assertEqual('<DAG: test_name>', repr(ret))

    @mock.patch('tethys_compute.models.condor.condor_workflow.CondorPyWorkflow.load_nodes')
    @mock.patch('tethys_compute.models.condor.condor_workflow.CondorBase.condor_object')
    def test_execute(self, mock_co, mock_ln):
        # Mock submit to return a 111 cluster id
        mock_co.submit.return_value = 111

        # Execute
        self.condorworkflow._execute(options=['foo'])

        # We already tested load_nodes in CondorPyWorkflow, just mocked to make sure it's called here.
        mock_ln.assert_called()
        mock_co.submit.assert_called_with(options=['foo'])

        # Check cluster_id from _execute in condorbase
        self.assertEqual(111, self.condorworkflow.cluster_id)

    def test_get_job(self):
        ret = self.condorworkflow.get_job(job_name='Node_1')

        # Check result
        self.assertIsInstance(ret, CondorWorkflowJobNode)
        self.assertEqual('Node_1', ret.name)

    def test_get_job_does_not_exist(self):
        ret = self.condorworkflow.get_job(job_name='Node_2')
        # Check result
        self.assertIsNone(ret)

    @mock.patch('tethys_compute.models.condor.condor_workflow.CondorBase.update_database_fields')
    @mock.patch('tethys_compute.models.condor.condor_workflow.CondorPyWorkflow.update_database_fields')
    def test_update_database_fieds(self, mock_pw_update, mock_ba_update):
        # Execute
        self.condorworkflow.update_database_fields()

        # Check if mock is called
        mock_pw_update.assert_called()
        mock_ba_update.assert_called()

    @mock.patch('tethys_compute.models.condor.condor_workflow.CondorWorkflow.nodes',
                new_callable=mock.PropertyMock(return_value=[mock_nodes]))
    def test_log_files(self, _):
        expected_ret = {'workflow': 'test_name.dag.dagman.out',
                        'test_job1': {'log': 'test_job1/logs/*.log',
                                      'error': 'test_job1/logs/*.err',
                                      'output': 'test_job1/logs/*.out'}}
        # Execute
        ret = self.condorworkflow._log_files()

        self.assertEqual(expected_ret, ret)

    @mock.patch('tethys_compute.models.condor.condor_workflow.CondorWorkflow.update_database_fields')
    def test_condor_workflow_presave(self, mock_update):
        # Excute
        self.condorworkflow.save()

        # Check if update_database_fields is called
        mock_update.assert_called()

    @mock.patch('tethys_compute.models.condor.condor_workflow.CondorWorkflow.condor_object')
    def test_condor_job_pre_delete(self, mock_co):
        if not os.path.exists(self.workspace_dir):
            os.makedirs(self.workspace_dir)
            file_path = os.path.join(self.workspace_dir, 'test_file.txt')
            open(file_path, 'a').close()

        self.condorworkflow.delete()

        # Check if close_remote is called
        mock_co.close_remote.assert_called()

        # Check if file has been removed
        self.assertFalse(os.path.isfile(file_path))

    @mock.patch('tethys_compute.models.condor.condor_workflow.log')
    @mock.patch('tethys_compute.models.condor.condor_workflow.CondorWorkflow.condor_object')
    def test_condor_job_pre_delete_exception(self, mock_co, mock_log):
        mock_co.close_remote.side_effect = Exception('test error')
        self.condorworkflow.delete()

        # Check if close_remote is called
        mock_log.exception.assert_called_with('test error')

    def test__update_status_no_execute_time(self):
        self.condorworkflow.execute_time = None
        ret = self.condorworkflow._update_status()
        self.assertEqual('SUB', ret)

    @mock.patch('tethys_compute.models.condor.condor_workflow.CondorBase.condor_object')
    def test__update_status_not_Running(self, mock_co):
        self.condorworkflow.execute_time = tz.now()
        mock_co.status = 'Completed'

        self.condorworkflow._update_status()

        self.assertEqual('COM', self.condorworkflow._status)

    @mock.patch('tethys_compute.models.condor.condor_workflow.CondorBase.condor_object')
    def test__update_status_Running_not_running_statuses(self, mock_co):
        self.condorworkflow.execute_time = tz.now()
        mock_co.status = 'Running'
        mock_co.statuses = {'Unexpanded': 0, 'Idle': 0, 'Running': 0, 'Completed': 1}

        self.condorworkflow._update_status()

        self.assertEqual('VCP', self.condorworkflow._status)

    @mock.patch('tethys_compute.models.condor.condor_workflow.CondorBase.condor_object')
    def test__update_status_Running_no_statuses(self, mock_co):
        self.condorworkflow.execute_time = tz.now()
        mock_co.status = 'Running'
        mock_co.statuses = {'Unexpanded': 0, 'Idle': 0, 'Running': 0, 'Completed': 0}

        self.condorworkflow._update_status()

        self.assertEqual('SUB', self.condorworkflow._status)

    @mock.patch('tethys_compute.models.condor.condor_workflow.CondorBase.condor_object')
    def test__update_status_exception(self, mock_co):
        self.condorworkflow.execute_time = tz.now()
        type(mock_co).status = mock.PropertyMock(side_effect=Exception)

        self.condorworkflow._update_status()

        self.assertEqual('ERR', self.condorworkflow._status)
