from tethys_sdk.testing import TethysTestCase
from tethys_compute.models.condor.condor_scheduler import CondorScheduler
from tethys_compute.models.condor.condor_py_workflow import CondorPyWorkflow
from tethys_compute.models.condor.condor_workflow_job_node import CondorWorkflowJobNode
from tethys_compute.models.condor.condor_workflow import CondorWorkflow
from django.contrib.auth.models import User
from django.utils import timezone as tz
from unittest import mock
import datetime
import shutil
from pathlib import Path


class CondorWorkflowTest(TethysTestCase):
    mock_nodes = mock.MagicMock()
    mock_nodes.name = "test_job1"

    mock_condor_workflow = mock.MagicMock()
    mock_condor_workflow._execute.return_value = "out", "err"

    def set_up(self):
        test_models_dir = Path(__file__).parent
        self.workspace_dir = test_models_dir / "workspace"
        self.user = User.objects.create_user("tethys_super", "user@example.com", "pass")
        self.private_key = test_models_dir.parent / "files" / "keys" / "testkey"
        self.private_key_pass = "password"

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

        self.condorworkflowjobnode_child = CondorWorkflowJobNode(
            name="Node_child",
            workflow=self.condorpyworkflow,
            _attributes={"test": "one"},
            _num_jobs=1,
            _remote_input_files=["test1.txt"],
        )
        self.condorworkflowjobnode_child.save()

        self.condorworkflowjobnode = CondorWorkflowJobNode(
            name="Node_1",
            workflow=self.condorpyworkflow,
            _attributes={"test": "one"},
            _num_jobs=1,
            _remote_input_files=["test1.txt"],
        )
        self.condorworkflowjobnode.save()

        # Django model many to many relationship add method
        self.condorworkflowjobnode.parent_nodes.add(self.condorworkflowjobnode_child)

        self.condorbase_id = CondorWorkflow.objects.get(
            name="test name"
        ).condorbase_ptr_id
        self.condorpyworkflow_id = CondorWorkflow.objects.get(
            name="test name"
        ).condorpyworkflow_ptr_id

    def tear_down(self):
        self.scheduler.delete()

        if self.condorworkflow.condorbase_ptr_id == self.condorbase_id:
            self.condorworkflow.delete()

        if self.workspace_dir.exists():
            shutil.rmtree(str(self.workspace_dir))

    def test_type(self):
        ret = self.condorworkflow.type
        self.assertEqual("CondorWorkflow", ret)

    def test_condor_object_prop(self):
        ret = self.condorworkflow._condor_object

        # Check workflow return
        self.assertEqual({"foo": 10}, ret.max_jobs)
        self.assertEqual("test_config", ret.config)
        self.assertEqual("<DAG: test_name>", repr(ret))

    @mock.patch(
        "tethys_compute.models.condor.condor_workflow.CondorPyWorkflow.load_nodes"
    )
    @mock.patch("tethys_compute.models.condor.condor_workflow.CondorBase.condor_object")
    def test_execute(self, mock_co, mock_ln):
        # Mock submit to return a 111 cluster id
        mock_co.submit.return_value = 111

        # Execute
        self.condorworkflow._execute(options=["foo"])

        # We already tested load_nodes in CondorPyWorkflow, just mocked to make sure it's called here.
        mock_ln.assert_called()
        options = mock_co.submit.call_args[1]["options"]
        self.assertEqual("foo", options[0])
        self.assertIn(f'+TethysJobId = "{self.condorworkflow.id}"', options)

        # Check cluster_id from _execute in condorbase
        self.assertEqual(111, self.condorworkflow.cluster_id)

    @mock.patch(
        "tethys_compute.models.condor.condor_workflow.CondorPyWorkflow.load_nodes"
    )
    @mock.patch("tethys_compute.models.condor.condor_workflow.CondorBase.condor_object")
    def test_execute_no_options(self, mock_co, mock_ln):
        # Mock submit to return a 111 cluster id
        mock_co.submit.return_value = 111

        # Execute
        self.condorworkflow._execute()

        # We already tested load_nodes in CondorPyWorkflow, just mocked to make sure it's called here.
        mock_ln.assert_called()
        options = mock_co.submit.call_args[1]["options"]
        self.assertEqual(self.condorworkflow.status_report_options[0], options[0])
        self.assertIn(f'+TethysJobId = "{self.condorworkflow.id}"', options)

        # Check cluster_id from _execute in condorbase
        self.assertEqual(111, self.condorworkflow.cluster_id)

    def test_status_report_options_carry_the_job_id(self):
        options = self.condorworkflow.status_report_options

        self.assertEqual(["-append", "-append"], options[0::2])
        self.assertIn(f'+TethysJobId = "{self.condorworkflow.id}"', options)

    def test_status_report_options_token_verifies_back_to_this_job(self):
        options = self.condorworkflow.status_report_options
        ad = [o for o in options if o.startswith("+TethysJobToken")][0]
        token = ad.split('"')[1]

        self.assertEqual(
            str(self.condorworkflow.id),
            CondorWorkflow.id_from_status_report_token(token),
        )

    def test_status_report_options_token_does_not_verify_if_tampered(self):
        options = self.condorworkflow.status_report_options
        ad = [o for o in options if o.startswith("+TethysJobToken")][0]
        token = ad.split('"')[1]

        self.assertIsNone(CondorWorkflow.id_from_status_report_token(token + "x"))

    def test_get_job(self):
        ret = self.condorworkflow.get_job(job_name="Node_1")

        # Check result
        self.assertIsInstance(ret, CondorWorkflowJobNode)
        self.assertEqual("Node_1", ret.name)

    def test_get_job_does_not_exist(self):
        ret = self.condorworkflow.get_job(job_name="Node_2")
        # Check result
        self.assertIsNone(ret)

    @mock.patch(
        "tethys_compute.models.condor.condor_workflow.CondorBase.update_database_fields"
    )
    @mock.patch(
        "tethys_compute.models.condor.condor_workflow.CondorPyWorkflow.update_database_fields"
    )
    def test_update_database_fieds(self, mock_pw_update, mock_ba_update):
        # Execute
        self.condorworkflow.update_database_fields()

        # Check if mock is called
        mock_pw_update.assert_called()
        mock_ba_update.assert_called()

    @mock.patch(
        "tethys_compute.models.condor.condor_workflow.CondorWorkflow.nodes",
        new_callable=mock.PropertyMock(return_value=[mock_nodes]),
    )
    def test_log_files(self, _):
        expected_ret = {
            "workflow": {
                "out": "test_name.dag.dagman.out",
                "log": "test_name.dag.dagman.log",
                "error": "test_name.dag.lib.err",
            },
            "test_job1": {
                "log": str(Path("test_job1/logs/*.log")),
                "error": str(Path("test_job1/logs/*.err")),
                "output": str(Path("test_job1/logs/*.out")),
            },
        }
        # Execute
        ret = self.condorworkflow._log_files()

        self.assertEqual(expected_ret, ret)

    @mock.patch(
        "tethys_compute.models.condor.condor_workflow.CondorWorkflow.update_database_fields"
    )
    def test_condor_workflow_presave(self, mock_update):
        # Excute
        self.condorworkflow.save()

        # Check if update_database_fields is called
        mock_update.assert_called()

    @mock.patch(
        "tethys_compute.models.condor.condor_workflow.CondorWorkflow.condor_object"
    )
    def test_condor_job_pre_delete(self, mock_co):
        if not self.workspace_dir.exists():
            self.workspace_dir.mkdir(parents=True)
            file_path = self.workspace_dir / "test_file.txt"
            file_path.touch()

        self.condorworkflow.delete()

        # Check if close_remote is called
        mock_co.close_remote.assert_called()

        # Check if file has been removed
        self.assertFalse(file_path.is_file())

    @mock.patch("tethys_compute.models.condor.condor_workflow.log")
    @mock.patch(
        "tethys_compute.models.condor.condor_workflow.CondorWorkflow.condor_object"
    )
    def test_condor_job_pre_delete_exception(self, mock_co, mock_log):
        mock_co.close_remote.side_effect = Exception("test error")
        self.condorworkflow.delete()

        # Check if close_remote is called
        mock_log.exception.assert_called_with("test error")

    def test__update_status_no_execute_time(self):
        self.condorworkflow.execute_time = None
        ret = self.condorworkflow._update_status()
        self.assertEqual("SUB", ret)

    @mock.patch("tethys_compute.models.condor.condor_workflow.CondorBase.condor_object")
    def test__update_status_not_Running(self, mock_co):
        self.condorworkflow.execute_time = tz.now()
        mock_co.status = "Completed"

        self.condorworkflow._update_status()

        self.assertEqual("COM", self.condorworkflow._status)

    @mock.patch("tethys_compute.models.condor.condor_workflow.CondorBase.condor_object")
    def test__update_status_Running_not_running_statuses(self, mock_co):
        self.condorworkflow.execute_time = tz.now()
        mock_co.status = "Running"
        mock_co.statuses = {"Unexpanded": 0, "Idle": 0, "Running": 0, "Completed": 1}

        self.condorworkflow._update_status()

        self.assertEqual("VCP", self.condorworkflow._status)

    @mock.patch("tethys_compute.models.condor.condor_workflow.CondorBase.condor_object")
    def test__update_status_Running_no_statuses(self, mock_co):
        self.condorworkflow.execute_time = tz.now()
        mock_co.status = "Running"
        mock_co.statuses = {"Unexpanded": 0, "Idle": 0, "Running": 0, "Completed": 0}

        self.condorworkflow._update_status()

        self.assertEqual("SUB", self.condorworkflow._status)

    @mock.patch("tethys_compute.models.condor.condor_workflow.CondorBase.condor_object")
    def test__update_status_exception(self, mock_co):
        self.condorworkflow.execute_time = tz.now()
        type(mock_co).status = mock.PropertyMock(side_effect=Exception)

        self.condorworkflow._update_status()

        self.assertEqual("ERR", self.condorworkflow._status)

    def test_cached_statuses_unexpanded_when_nothing_persisted(self):
        statuses = self.condorworkflow.cached_statuses

        self.assertEqual(2, statuses["Unexpanded"])
        self.assertEqual(0, statuses["Running"])
        self.assertEqual(0, statuses["Completed"])

    def test_cached_statuses_counts_persisted_statuses(self):
        self.condorworkflowjobnode.cached_node_status = "Running"
        self.condorworkflowjobnode.save()
        self.condorworkflowjobnode_child.cached_node_status = "Completed"
        self.condorworkflowjobnode_child.save()

        statuses = self.condorworkflow.cached_statuses

        self.assertEqual(1, statuses["Running"])
        self.assertEqual(1, statuses["Completed"])
        self.assertEqual(0, statuses["Unexpanded"])

    def test_node_statuses_not_current_when_never_updated(self):
        self.assertIsNone(self.condorworkflow.node_statuses_updated)
        self.assertFalse(self.condorworkflow.node_statuses_are_current)

    def test_node_statuses_current_after_recent_update(self):
        self.condorworkflow.node_statuses_updated = tz.now()

        self.assertTrue(self.condorworkflow.node_statuses_are_current)

    def test_node_statuses_not_current_once_stale(self):
        self.condorworkflow.node_statuses_updated = tz.now() - datetime.timedelta(
            seconds=3600
        )

        self.assertFalse(self.condorworkflow.node_statuses_are_current)

    def test_node_statuses_max_age_exceeds_poll_interval(self):
        """A pass over many jobs takes longer than one job's poll interval."""
        self.assertGreater(
            self.condorworkflow.node_statuses_max_age,
            self.condorworkflow.update_status_interval,
        )

    def test_node_statuses_current_beyond_the_poll_interval(self):
        self.condorworkflow.node_statuses_updated = tz.now() - datetime.timedelta(
            seconds=self.condorworkflow.update_status_interval.total_seconds() * 2
        )

        self.assertTrue(self.condorworkflow.node_statuses_are_current)

    def test_node_statuses_max_age_is_overridable(self):
        self.condorworkflow._node_statuses_max_age = datetime.timedelta(seconds=1)
        self.condorworkflow.node_statuses_updated = tz.now() - datetime.timedelta(
            seconds=5
        )

        self.assertFalse(self.condorworkflow.node_statuses_are_current)

    def test_cached_statuses_makes_no_remote_call(self):
        with mock.patch(
            "tethys_compute.models.condor.condor_workflow.CondorBase.condor_object"
        ) as mock_co:
            self.condorworkflow.cached_statuses

        mock_co.assert_not_called()

    def test_update_node_statuses_no_execute_time(self):
        self.condorworkflow.execute_time = None

        self.assertEqual({}, self.condorworkflow.update_node_statuses())

    @mock.patch("tethys_compute.models.condor.condor_workflow.CondorBase.condor_object")
    def test_update_node_statuses_persists_status(self, mock_co):
        self.condorworkflow.execute_time = tz.now()
        cpy_node = mock.MagicMock()
        cpy_node.job.cluster_id = 7
        cpy_node.job.name = "Node_1"
        mock_co.node_set = [cpy_node]
        mock_co.node_statuses_by_cluster_id.return_value = {7: "Running"}

        updated = self.condorworkflow.update_node_statuses()

        self.condorworkflowjobnode.refresh_from_db()
        self.assertEqual("Running", self.condorworkflowjobnode.cached_node_status)
        self.assertEqual({"Node_1": "Running"}, updated)
        mock_co.node_statuses_by_cluster_id.assert_called_once()
        self.assertTrue(self.condorworkflow.node_statuses_are_current)

    @mock.patch("tethys_compute.models.condor.condor_workflow.CondorBase.condor_object")
    def test_update_node_statuses_matches_name_with_spaces(self, mock_co):
        """Node names are underscored to build the condorpy job name."""
        spaced_node = CondorWorkflowJobNode(
            name="Node With Spaces",
            workflow=self.condorpyworkflow,
            _attributes={"test": "one"},
            _num_jobs=1,
        )
        spaced_node.save()
        self.condorworkflow.execute_time = tz.now()
        cpy_node = mock.MagicMock()
        cpy_node.job.cluster_id = 9
        cpy_node.job.name = "Node_With_Spaces"
        mock_co.node_set = [cpy_node]
        mock_co.node_statuses_by_cluster_id.return_value = {9: "Completed"}

        self.condorworkflow.update_node_statuses()

        spaced_node.refresh_from_db()
        self.assertEqual("Completed", spaced_node.cached_node_status)

    @mock.patch("tethys_compute.models.condor.condor_workflow.CondorBase.condor_object")
    def test_update_node_statuses_remote_failure(self, mock_co):
        self.condorworkflow.execute_time = tz.now()
        mock_co.node_statuses_by_cluster_id.side_effect = Exception("boom")

        updated = self.condorworkflow.update_node_statuses()

        self.assertEqual({}, updated)
        self.condorworkflowjobnode.refresh_from_db()
        self.assertIsNone(self.condorworkflowjobnode.cached_node_status)
        self.assertIsNone(self.condorworkflow.node_statuses_updated)
