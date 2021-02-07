from unittest import mock
import unittest
import json
from django.test import RequestFactory
import tethys_gizmos.views.gizmos.jobs_table as gizmo_jobs_table
from condorpy.workflow import Workflow, Node
from tethys_compute.models import CondorWorkflow, TethysJob, CondorWorkflowJobNode, DaskJob
from tethys_gizmos.views.gizmos.jobs_table import bokeh_row


class TestJobsTable(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob.objects.get_subclass')
    def test_execute(self, mock_tj):
        tj = mock_tj()
        tj.execute.return_value = mock.MagicMock()

        result = gizmo_jobs_table.execute(request='', job_id='1')

        self.assertEqual(200, result.status_code)

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.log')
    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob')
    def test_execute_exception(self, mock_tj, mock_log):
        tj = mock_tj.objects.get_subclass()
        tj.execute.side_effect = Exception('error')

        gizmo_jobs_table.execute(request='', job_id='1')

        mock_log.error.assert_called_with('The following error occurred when executing job %s: %s', '1', 'error')

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob')
    def test_terminate(self, mock_tj):
        tj = mock_tj.objects.get_subclass()
        tj.stop.return_value = mock.MagicMock()

        result = gizmo_jobs_table.terminate(request='', job_id='1')

        self.assertEqual(200, result.status_code)

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.log')
    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob')
    def test_terminate_exception(self, mock_tj, mock_log):
        tj = mock_tj.objects.get_subclass()
        tj.stop.side_effect = Exception('error')

        gizmo_jobs_table.terminate(request='', job_id='1')

        mock_log.error.assert_called_with('The following error occurred when terminating job %s: %s', '1', 'error')

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob')
    def test_delete(self, mock_tj):
        tj = mock_tj.objects.get_subclass()
        tj.delete.return_value = mock.MagicMock()

        result = gizmo_jobs_table.delete(request='', job_id='1')

        self.assertEqual(200, result.status_code)

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.log')
    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob')
    def test_delete_exception(self, mock_tj, mock_log):
        tj = mock_tj.objects.get_subclass()
        tj.delete.side_effect = Exception('error')

        gizmo_jobs_table.delete(request='', job_id='1')

        mock_log.error.assert_called_with('The following error occurred when deleting job %s: %s', '1', 'error')

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob.objects.get_subclass')
    def test_resubmit(self, mock_tj):
        tj = mock_tj()
        tj.resubmit.return_value = mock.MagicMock()

        result = gizmo_jobs_table.resubmit(request='', job_id='1')

        self.assertEqual(200, result.status_code)

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.log')
    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob')
    def test_resubmit_exception(self, mock_tj, mock_log):
        tj = mock_tj.objects.get_subclass()
        tj.resubmit.side_effect = Exception('error')

        gizmo_jobs_table.resubmit(request='', job_id='1')

        mock_log.error.assert_called_with('The following error occurred when resubmiting job %s: %s', '1', 'error')

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob.objects.get_subclass')
    def test_show_log(self, mock_tj):
        tj = mock_tj()
        tj.get_logs.return_value = {'log': {'sub_log_1': mock.MagicMock(), 'sub_log_2': 'log content'}}

        result = gizmo_jobs_table.show_log(request='', job_id='1')
        self.assertEqual(200, result.status_code)

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.log')
    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob')
    def test_show_log_exception(self, mock_tj, mock_log):
        tj = mock_tj.objects.get_subclass()
        tj.get_logs.side_effect = Exception('error')

        gizmo_jobs_table.show_log(request='', job_id='1')

        mock_log.error.assert_called_with('The following error occurred when retrieving logs for job %s: %s',
                                          '1', 'error')

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob')
    def test_get_log_content(self, mock_tj):
        tj = mock_tj.objects.get_subclass()
        tj.get_logs.return_value = {'log': 'log content'}

        result = gizmo_jobs_table.get_log_content(request='', job_id='1', key1='log')
        self.assertEqual(200, result.status_code)

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob')
    def test_get_log_content_key2(self, mock_tj):
        tj = mock_tj.objects.get_subclass()
        log_func = mock.MagicMock()
        log_func.return_value = 'log content'
        tj.get_logs.return_value = {'log': {'sub_log_1': log_func, 'sub_log_2': 'log content'}}

        result = gizmo_jobs_table.get_log_content(request='', job_id='1', key1='log', key2='sub_log_1')
        self.assertEqual(200, result.status_code)

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.log')
    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob')
    def test_get_log_content_exception(self, mock_tj, mock_log):
        tj = mock_tj.objects.get_subclass()
        tj.get_logs.side_effect = Exception('error')

        gizmo_jobs_table.get_log_content(request='', job_id='1', key1='log')

        mock_log.error.assert_called_with(
            'The following error occurred when retrieving log content for log %s in job %s: %s', '1', 'log ', 'error'
        )

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.render_to_string')
    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob')
    def test_update_row_showcase(self, mock_tj, mock_rts):
        mock_rts.return_value = '{"job_statuses":[]}'
        mock_tj.objects.get_subclass.return_value = mock.MagicMock(
            spec=TethysJob, status='Various', label='gizmos_showcase'
        )
        rows = [('1', '30')]
        column_names = ['id', 'creation_time']
        request = RequestFactory().post('/jobs', {'column_fields': column_names, 'row': rows})
        result = gizmo_jobs_table.update_row(request, job_id='1')

        # Check Result
        rts_call_args = mock_rts.call_args_list
        self.assertEqual('Various', rts_call_args[0][0][1]['job_status'])
        self.assertIn('job_statuses', rts_call_args[0][0][1])
        self.assertEqual({'Completed': 40, 'Error': 10, 'Running': 30, 'Aborted': 5},
                         rts_call_args[0][0][1]['job_statuses'])
        self.assertEqual(200, result.status_code)

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.render_to_string')
    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob')
    def test_update_row_showcase_various_complete(self, mock_tj, mock_rts):
        mock_rts.return_value = '{"job_statuses":[]}'
        mock_tj.objects.get_subclass.return_value = mock.MagicMock(
            spec=TethysJob, status='Various-Complete', label='gizmos_showcase'
        )
        rows = [('1', '30')]
        column_names = ['id', 'creation_time']
        request = RequestFactory().post('/jobs', {'column_fields': column_names, 'row': rows})
        result = gizmo_jobs_table.update_row(request, job_id='1')

        # Check Result
        rts_call_args = mock_rts.call_args_list
        self.assertEqual('Various-Complete', rts_call_args[0][0][1]['job_status'])
        self.assertIn('job_statuses', rts_call_args[0][0][1])
        self.assertEqual({'Completed': 80, 'Error': 15, 'Running': 0, 'Aborted': 5},
                         rts_call_args[0][0][1]['job_statuses'])
        self.assertEqual(200, result.status_code)

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.render_to_string')
    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob')
    def test_update_row_showcase_condor_workflow(self, mock_tj, mock_rts):
        mock_rts.return_value = '{"job_statuses":[]}'
        mock_tj.objects.get_subclass.return_value = mock.MagicMock(
            spec=CondorWorkflow, status='Various', label='gizmos_showcase'
        )
        rows = [('1', '30')]
        column_names = ['id', 'creation_time']
        request = RequestFactory().post('/jobs', {'column_fields': column_names, 'row': rows})
        result = gizmo_jobs_table.update_row(request, job_id='1')

        # Check Result
        rts_call_args = mock_rts.call_args_list
        self.assertEqual('Various', rts_call_args[0][0][1]['job_status'])
        self.assertIn('job_statuses', rts_call_args[0][0][1])
        self.assertEqual({'Completed': 20, 'Error': 20, 'Running': 40, 'Aborted': 0},
                         rts_call_args[0][0][1]['job_statuses'])
        self.assertEqual(200, result.status_code)

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.render_to_string')
    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob')
    def test_update_row(self, mock_tj, mock_rts):
        # Another Case where job.label is not gizmos_showcase
        mock_rts.return_value = '{"job_statuses":[]}'
        mock_tj.objects.get_subclass.return_value = mock.MagicMock(
            spec=CondorWorkflow, status='Various', label='test_label',
            statuses={'Completed': 1, 'Running': 1}, num_jobs=2
        )
        rows = [('1', '30')]
        column_names = ['id', 'creation_time']

        request = RequestFactory().post('/jobs', {'column_fields': column_names, 'row': rows,
                                                  'actions[run]': False, 'actions[resubmit]': False})
        result = gizmo_jobs_table.update_row(request, job_id='1')

        # Check Result
        rts_call_args = mock_rts.call_args_list
        self.assertEqual('Various', rts_call_args[0][0][1]['job_status'])
        self.assertIn('job_statuses', rts_call_args[0][0][1])
        self.assertEqual({'Aborted': 0, 'Completed': 50.0, 'Error': 0, 'Running': 50.0},
                         rts_call_args[0][0][1]['job_statuses'])
        self.assertEqual(200, result.status_code)

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.render_to_string')
    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob')
    def test_update_row_dask_job_results_ready(self, mock_tj, mock_rts):
        # Another Case where job.label is not gizmos_showcase
        mock_rts.return_value = '{"job_statuses":[]}'
        mock_tj.objects.get_subclass.return_value = mock.MagicMock(
            spec=DaskJob, status='Results-Ready', label='test_label',
        )
        rows = [('1', '30')]
        column_names = ['id', 'creation_time']
        request = RequestFactory().post('/jobs', {'column_fields': column_names, 'row': rows})
        result = gizmo_jobs_table.update_row(request, job_id='1')

        # Check Result
        rts_call_args = mock_rts.call_args_list
        self.assertEqual('Running', rts_call_args[0][0][1]['job_status'])
        self.assertEqual(200, result.status_code)

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.render_to_string')
    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob')
    def test_update_row_condor_workflow_no_statuses(self, mock_tj, mock_rts):
        # Another Case where job.label is not gizmos_showcase
        mock_rts.return_value = '{"job_statuses":[]}'
        mock_tj.objects.get_subclass.return_value = mock.MagicMock(
            spec=CondorWorkflow, status='Various', label='test_label',
            statuses={'Completed': 0, 'Running': 0}, num_jobs=1
        )
        rows = [('1', '30')]
        column_names = ['id', 'creation_time']
        request = RequestFactory().post('/jobs', {'column_fields': column_names, 'row': rows})
        result = gizmo_jobs_table.update_row(request, job_id='1')

        # Check Result
        rts_call_args = mock_rts.call_args_list
        self.assertIn('job_statuses', rts_call_args[0][0][1])
        self.assertEqual({'Aborted': 0, 'Completed': 0, 'Error': 0, 'Running': 0},
                         rts_call_args[0][0][1]['job_statuses'])
        self.assertIn('job_status', rts_call_args[0][0][1])
        self.assertEqual('Submitted', rts_call_args[0][0][1]['job_status'])
        self.assertEqual(200, result.status_code)

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.log')
    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob')
    def test_update_row_exception(self, mock_tj, mock_log):
        mock_tj.objects.get_subclass.side_effect = Exception('error')
        rows = [('1', '30'),
                ('2', '18'),
                ('3', '26')]
        column_names = ['id', 'creation_time']
        request = RequestFactory().post('/jobs', {'column_fields': column_names, 'row': rows})
        gizmo_jobs_table.update_row(request, job_id='1')

        # Check Result
        mock_log.warning.assert_called_with('Updating row for job 1 failed: error')

    def test_parse_value(self):
        result = gizmo_jobs_table._parse_value('True')
        self.assertTrue(result)

        result = gizmo_jobs_table._parse_value('False')
        self.assertFalse(result)

        result = gizmo_jobs_table._parse_value('Test')
        self.assertEqual('Test', result)

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob')
    def test_update_workflow_nodes_row(self, mock_tj):
        mock_job_a = mock.MagicMock(
            spec=Node,
            cluster_id=1,
            status='Completed'
        )
        mock_job_a.name = 'a-job'

        mock_node_a = mock.MagicMock(
            spec=CondorWorkflowJobNode,
            parent_nodes=[],
            job=mock_job_a
        )

        mock_job_b = mock.MagicMock(
            spec=Node,
            cluster_id=2,
            status='Running'
        )
        mock_job_b.name = 'b_job'

        mock_node_b = mock.MagicMock(
            spec=CondorWorkflowJobNode,
            parent_nodes=[
                mock_node_a
            ],
            job=mock_job_b
        )

        mock_condor_object = mock.MagicMock(
            spec=Workflow,
            node_set=[mock_node_a, mock_node_b]
        )

        mock_tj.objects.get_subclass.return_value = mock.MagicMock(
            spec=CondorWorkflow, status='Various', label='test_label',
            condor_object=mock_condor_object
        )

        request = RequestFactory().post('/jobs')

        result = gizmo_jobs_table.update_workflow_nodes_row(request, job_id='1')

        self.assertEqual(200, result.status_code)
        data = json.loads(result.content.decode())
        self.assertTrue(data['success'])
        self.assertEqual('Various', data['status'])
        self.assertEqual(
            {
                'a-job': {
                    'status': 'com',
                    'cluster_id': 1,
                    'parents': [],
                    'display': 'A Job'
                },
                'b_job': {
                    'status': 'run',
                    'cluster_id': 2,
                    'parents': ['a-job'],
                    'display': 'B Job'
                }
            },
            data['dag']
        )

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob')
    def test_update_workflow_nodes_row_showcase(self, mock_tj):
        mock_tj.objects.get_subclass.return_value = mock.MagicMock(
            spec=CondorWorkflow, status='Various', label='gizmos_showcase',
        )

        request = RequestFactory().post('/jobs')

        result = gizmo_jobs_table.update_workflow_nodes_row(request, job_id='1')

        self.assertEqual(200, result.status_code)
        data = json.loads(result.content.decode())
        self.assertTrue(data['success'])
        self.assertEqual('Various', data['status'])
        self.assertEqual(
            {
                'a': {
                    'status': 'com',
                    'parents': [],
                    'cluster_id': 1,
                    'display': 'Job A'
                },
                'b': {
                    'status': 'err',
                    'parents': ['a'],
                    'cluster_id': 2,
                    'display': 'Job B'
                },
                'c': {
                    'status': 'run',
                    'parents': ['a'],
                    'cluster_id': 3,
                    'display': 'Job C'
                },
                'd': {
                    'status': 'sub',
                    'parents': ['a'],
                    'cluster_id': 4,
                    'display': 'Job D'
                },
                'e': {
                    'status': 'pen',
                    'parents': ['c', 'd'],
                    'cluster_id': 5,
                    'display': 'Job E'
                },
                'f': {
                    'status': 'abt',
                    'parents': ['b', ],
                    'cluster_id': 0,
                    'display': 'Job F'
                }
            },
            data['dag']
        )

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.log')
    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob')
    def test_update_workflow_nodes_row_exception(self, mock_tj, mock_log):
        mock_tj.objects.get_subclass.side_effect = Exception

        request = RequestFactory().post('/jobs')

        result = gizmo_jobs_table.update_workflow_nodes_row(request, job_id='1')

        self.assertEqual(200, result.status_code)
        data = json.loads(result.content.decode())
        self.assertFalse(data['success'])
        self.assertIsNone(data['status'])
        self.assertEqual({}, data['dag'])
        mock_log.error.assert_called()

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.render_to_string')
    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.server_document')
    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.DaskScheduler')
    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob')
    def test_bokeh_row(self, mock_tethys, mock_scheduler, mock_bokeh, mock_render):
        mock_job = mock.MagicMock()
        mock_job.status = 'test_status'
        mock_job.scheduler_id = 'test_scheduler_id'
        mock_tethys.objects.get_subclass.return_value = mock_job

        mock_dask_scheduler = mock.MagicMock()
        mock_dask_scheduler.dashboard = 'test_dashboard'
        mock_scheduler.objects.get.return_value = mock_dask_scheduler

        request = mock.MagicMock()

        mock_bokeh.return_value = 'test_script'
        mock_render.return_value = 'test_html'

        # Excute

        ret = bokeh_row(request, job_id='test_id')

        self.assertIn('"html": "test_html"', ret.content.decode('utf-8'))
        mock_bokeh.assert_called_with('http://test_dashboard/individual-graph')

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.log')
    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.server_document')
    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.DaskScheduler')
    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob')
    def test_bokeh_row_error(self, mock_tethys, mock_scheduler, mock_bokeh, mock_log):
        mock_job = mock.MagicMock()
        mock_job.status = 'test_status'
        mock_job.scheduler_id = 'test_scheduler_id'
        mock_tethys.objects.get_subclass.return_value = mock_job

        mock_dask_scheduler = mock.MagicMock()
        mock_dask_scheduler.name = 'test_name'
        mock_dask_scheduler.dashboard = 'test_dashboard'
        mock_scheduler.objects.get.return_value = mock_dask_scheduler

        request = mock.MagicMock()

        mock_bokeh.side_effect = Exception('test_error_message')

        # Excute

        bokeh_row(request, job_id='test_id')

        mock_log.error.assert_called_with('The following error occurred when getting bokeh chart from scheduler'
                                          ' test_name for job test_id: test_error_message')
