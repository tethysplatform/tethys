from tethys_sdk.testing import TethysTestCase
from tethys_compute.models.condor.condor_scheduler import CondorScheduler
from tethys_compute.models.condor.condor_py_workflow import CondorPyWorkflow
from tethys_compute.models.condor.condor_workflow_node import CondorWorkflowNode
from tethys_compute.models.condor.condor_workflow_job_node import CondorWorkflowJobNode
from tethys_compute.models.condor.condor_workflow import CondorWorkflow
from django.contrib.auth.models import User
from condorpy import Job
from unittest import mock
from pathlib import Path


class CondorWorkflowNodeTest(TethysTestCase):
    def set_up(self):
        test_models_dir = Path(__file__).parent
        self.workspace_dir = test_models_dir / "workspace"
        self.private_key = test_models_dir.parent / "files" / "keys" / "testkey"
        self.private_key_pass = "password"

        self.user = User.objects.create_user("tethys_super", "user@example.com", "pass")

        self.scheduler = CondorScheduler(
            name="test_scheduler",
            host="localhost",
            username="tethys_super",
            password="pass",
            private_key_path=str(self.private_key),
            private_key_pass=self.private_key_pass,
        )
        self.scheduler.save()

        self.condorworkflow = CondorWorkflow(
            _max_jobs={"foo": 10},
            _config="test_config",
            name="test name",
            workspace=str(self.workspace_dir),
            user=self.user,
            scheduler=self.scheduler,
        )
        self.condorworkflow.save()

        self.id_value = CondorWorkflow.objects.get(
            name="test name"
        ).condorpyworkflow_ptr_id
        self.condorpyworkflow = CondorPyWorkflow.objects.get(
            condorpyworkflow_id=self.id_value
        )

        # One node can have many children nodes
        self.condorworkflowjobnode_child = CondorWorkflowJobNode(
            name="Job1",
            workflow=self.condorpyworkflow,
            _attributes={"test": "one"},
            _num_jobs=1,
            _remote_input_files=["test1.txt"],
        )
        self.condorworkflowjobnode_child.save()

        # One node can have many children nodes
        self.condorworkflowjobnode_child2 = CondorWorkflowJobNode(
            name="Job2",
            workflow=self.condorpyworkflow,
            _attributes={"test": "one"},
            _num_jobs=1,
            _remote_input_files=["test1.txt"],
        )
        self.condorworkflowjobnode_child2.save()

        self.condorworkflownode = CondorWorkflowNode(
            name="test_condorworkflownode",
            workflow=self.condorpyworkflow,
        )
        self.condorworkflownode.save()

    def tear_down(self):
        self.condorworkflow.delete()
        self.condorworkflowjobnode_child.delete()
        self.condorworkflowjobnode_child2.delete()

    def test_type_abs_prop(self):
        ret = self.condorworkflownode.type()

        # Check result
        self.assertIsNone(ret)

    def test_job_abs_prop(self):
        ret = self.condorworkflownode.job()

        # Check result
        self.assertIsNone(ret)

    @mock.patch(
        "tethys_compute.models.condor.condor_workflow_node.CondorWorkflowNode.job"
    )
    def test_condorpy_node(self, mock_job):
        mock_job_return = Job(
            name="test_job",
            attributes={"foo": "bar"},
            num_jobs=1,
            remote_input_files=["test_file.txt"],
            working_directory=str(self.workspace_dir),
        )
        mock_job.return_value = mock_job_return

        self.condorworkflownode.job = mock_job_return
        ret = self.condorworkflownode.condorpy_node

        # Check result
        self.assertEqual("<Node: test_job parents() children()>", repr(ret))

    def test_add_parents_and_parents_prop(self):
        # Add parent should add parent to condorwoflownode
        self.condorworkflownode.add_parent(self.condorworkflowjobnode_child)
        self.condorworkflownode.add_parent(self.condorworkflowjobnode_child2)

        # Get this Parent Nodes here
        ret = self.condorworkflownode.parents

        # Check result
        self.assertIsInstance(ret[0], CondorWorkflowJobNode)
        self.assertEqual("Job1", ret[0].name)
        self.assertIsInstance(ret[1], CondorWorkflowJobNode)
        self.assertEqual("Job2", ret[1].name)

    def test_update_database_fields(self):
        self.assertIsNone(self.condorworkflownode.update_database_fields())
