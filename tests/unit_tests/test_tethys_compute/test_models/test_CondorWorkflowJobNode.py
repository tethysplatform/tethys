from tethys_sdk.testing import TethysTestCase
from tethys_compute.models.tethys_job import TethysJob
from tethys_compute.models.condor.condor_py_workflow import CondorPyWorkflow
from tethys_compute.models.condor.condor_workflow_job_node import CondorWorkflowJobNode
from tethys_compute.models.condor.condor_workflow import CondorWorkflow
from django.contrib.auth.models import User
from unittest import mock
from pathlib import Path


class CondorPyWorkflowJobNodeTest(TethysTestCase):
    def set_up(self):
        self.workspace_dir = Path(__file__).parent / "workspace"

        self.user = User.objects.create_user("tethys_super", "user@example.com", "pass")

        self.condorworkflow = CondorWorkflow(
            _max_jobs={"foo": 10},
            _config="test_config",
            name="foo{id}",
            workspace=str(self.workspace_dir),
            user=self.user,
        )
        self.condorworkflow.save()

        # To have a flow Node, we need to have a Condor Job which requires a CondorBase which requires a TethysJob
        self.id_value = CondorWorkflow.objects.get(
            name="foo{id}"
        ).condorpyworkflow_ptr_id
        self.condorpyworkflow = CondorPyWorkflow.objects.get(
            condorpyworkflow_id=self.id_value
        )

        self.condorworkflowjobnode = CondorWorkflowJobNode(
            name="Job1_NodeA",
            workflow=self.condorpyworkflow,
            _attributes={"test": "one"},
            _num_jobs=1,
            _remote_input_files=["test1.txt"],
        )
        self.condorworkflowjobnode.save()

    def tear_down(self):
        self.condorworkflow.delete()
        self.condorworkflowjobnode.delete()

    def test_type_prop(self):
        self.assertEqual("JOB", self.condorworkflowjobnode.type)

    def test_workspace_prop(self):
        self.assertEqual(".", self.condorworkflowjobnode.workspace)

    @mock.patch(
        "tethys_compute.models.condor.condor_workflow_job_node.CondorPyJob.condorpy_job"
    )
    def test_job_prop(self, mock_cpj):
        # Condorpy_job Prop is already tested in CondorPyJob Test case
        self.assertEqual(mock_cpj, self.condorworkflowjobnode.job)

    @mock.patch(
        "tethys_compute.models.condor.condor_workflow_job_node.CondorWorkflowNode.update_database_fields"
    )
    @mock.patch(
        "tethys_compute.models.condor.condor_workflow_job_node.CondorPyJob.update_database_fields"
    )
    def test_update_database_fields(self, mock_pj_update, mock_wfn_update):
        # Execute
        self.condorworkflowjobnode.update_database_fields()

        # Check result
        mock_pj_update.assert_called_once()
        mock_wfn_update.assert_called_once()

    @mock.patch(
        "tethys_compute.models.condor.condor_workflow_job_node.CondorWorkflowNode.update_database_fields"
    )
    @mock.patch(
        "tethys_compute.models.condor.condor_workflow_job_node.CondorPyJob.update_database_fields"
    )
    def test_receiver_pre_save(self, mock_pj_update, mock_wfn_update):
        self.condorworkflowjobnode.save()

        # Check result
        mock_pj_update.assert_called_once()
        mock_wfn_update.assert_called_once()

    def test_job_post_save(self):
        # get the job
        tethys_job = TethysJob.objects.get(name="foo{id}")
        id_val = tethys_job.id

        # Run save to activate post save
        tethys_job.save()

        # Set up new name
        new_name = "foo{id}".format(id=id_val)

        # Get same tethys job with new name
        tethys_job = TethysJob.objects.get(name=new_name)

        # Check results
        self.assertIsInstance(tethys_job, TethysJob)
        self.assertEqual(new_name, tethys_job.name)
