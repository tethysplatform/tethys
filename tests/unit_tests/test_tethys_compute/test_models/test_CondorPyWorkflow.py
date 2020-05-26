from tethys_sdk.testing import TethysTestCase
from tethys_compute.models.condor.condor_scheduler import CondorScheduler
from tethys_compute.models.condor.condor_py_workflow import CondorPyWorkflow
from tethys_compute.models.condor.condor_workflow_job_node import CondorWorkflowJobNode
from tethys_compute.models.condor.condor_workflow import CondorWorkflow
from django.contrib.auth.models import User
from unittest import mock
import os
import os.path


class CondorPyWorkflowTest(TethysTestCase):
    def set_up(self):
        test_models_dir = os.path.dirname(__file__)
        self.workspace_dir = os.path.join(test_models_dir, 'workspace')

        files_dir = os.path.join(os.path.dirname(test_models_dir), 'files')
        self.private_key = os.path.join(files_dir, 'keys', 'testkey')
        self.private_key_pass = 'password'

        self.user = User.objects.create_user('tethys_super', 'user@example.com', 'pass')

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
        self.condorpyworkflow.condor_object = mock.MagicMock()

        self.condorworkflowjobnode_a = CondorWorkflowJobNode(
            name='Job1_a',
            workflow=self.condorpyworkflow,
            _attributes={'foo': 'one'},
            _num_jobs=1,
            _remote_input_files=['test1.txt'],
        )

        self.condorworkflowjobnode_a.save()

        self.condorworkflowjobnode_a1 = CondorWorkflowJobNode(
            name='Job1_a1',
            workflow=self.condorpyworkflow,
            _attributes={'foo': 'one'},
            _num_jobs=1,
            _remote_input_files=['test1.txt'],
        )

        self.condorworkflowjobnode_a1.save()

        # Django model many to many relationship add method
        # self.condorworkflowjobnode.parent_nodes.add(self.condorworkflowjobnode_job)

    def tear_down(self):
        self.scheduler.delete()
        self.condorworkflow.delete()
        self.condorworkflowjobnode_a.delete()
        self.condorworkflowjobnode_a1.delete()

        # pass

    def test_condorpy_workflow_prop(self):
        ret = self.condorworkflow.condorpy_workflow

        # Check Result
        self.assertEqual('<DAG: test_name>', repr(ret))
        self.assertEqual(self.workspace_dir, ret._cwd)
        self.assertEqual('test_config', ret.config)

    @mock.patch('tethys_compute.models.condor.condor_py_workflow.Workflow')
    def test_max_jobs(self, mock_wf):
        max_jobs = {'foo': 5}
        self.condorpyworkflow.name = 'test_name'
        self.condorpyworkflow.workspace = 'test_dict'

        self.condorpyworkflow.max_jobs = max_jobs
        ret = self.condorpyworkflow.max_jobs

        # Check result
        self.assertEqual(5, ret['foo'])
        mock_wf.assert_called_with(config='test_config', max_jobs={'foo': 10},
                                   name='test_name', working_directory='test_dict')

    @mock.patch('tethys_compute.models.condor.condor_py_workflow.CondorPyWorkflow.condorpy_workflow')
    def test_config(self, mock_cw):
        test_config_value = 'test_config2'

        # Mock condorpy_workflow.config = test_config_value. We have already tested condorpy_workflow.
        mock_cw.config = test_config_value

        # Setter
        self.condorpyworkflow.config = test_config_value

        # Property
        ret = self.condorpyworkflow.config

        # Check result
        self.assertEqual('test_config2', ret)

    def test_nodes(self):
        ret = self.condorworkflow.nodes
        # Check result after loading nodes
        # self.assertEqual('Node_1', ret[0].name)

        # Check result in CondorPyWorkflow object
        self.assertEqual({'foo': 10}, ret[0].workflow.max_jobs)
        self.assertEqual('test_config', ret[0].workflow.config)

    def test_load_nodes(self):
        # Before load nodes. Set should be empty
        ret_before = self.condorworkflow.condorpy_workflow.node_set
        list_before = []

        list_after = []
        for e in ret_before:
            list_before.append(e)

        # Check list_before is empty
        self.assertFalse(list_before)

        # Add parent
        self.condorworkflowjobnode_a1.add_parent(self.condorworkflowjobnode_a)

        # Execute load nodes
        self.condorworkflow.load_nodes()

        # After load nodes, Set should have two elements. One parent and one child
        ret_after = self.condorworkflow.condorpy_workflow.node_set
        # Convert to list for checking result
        for e in ret_after:
            list_after.append(e)

        # Check list_after is not empty
        self.assertTrue(list_after)

        # sort list and compare result
        list_after.sort(key=lambda node: node.job.name)
        self.assertEqual('Job1_a', list_after[0].job.name)
        self.assertEqual('Job1_a1', list_after[1].job.name)

        # Check returns None if nodes are already loaded
        ret_after_load = self.condorworkflow.load_nodes()
        self.assertEqual(ret_after_load, None)

    def test_add_max_jobs_throttle(self):
        # Set max_jobs
        self.condorworkflow.add_max_jobs_throttle('foo1', 20)

        # Get return value
        ret = self.condorworkflow.condorpy_workflow

        # Check result
        self.assertEqual(20, ret.max_jobs['foo1'])

    @mock.patch('tethys_compute.models.condor.condor_workflow_job_node.CondorWorkflowJobNode.update_database_fields')
    def test_update_database_fields(self, mock_update):
        # Set attribute for node
        self.condorpyworkflow.update_database_fields()

        # Check if mock is called twice for node and child node
        self.assertTrue(mock_update.call_count == 2)

    @mock.patch('tethys_compute.models.condor.condor_py_workflow.CondorPyWorkflow.condorpy_workflow')
    def test_num_jobs(self, mock_condorpy_workflow_prop):
        ret = self.condorpyworkflow.num_jobs
        self.assertEqual(mock_condorpy_workflow_prop.num_jobs, ret)
