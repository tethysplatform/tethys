import unittest
import tethys_gizmos.gizmo_options.jobs_table as gizmo_jobs_table
from unittest import mock


class JobObject:
    def __init__(self, id, name, description, creation_time, run_time):
        self.id = id
        self.name = name
        self.description = description
        self.creation_time = creation_time
        self.run_time = run_time
        self.extended_properties = {'processing_results': True}
        self.status = 'Pending'

    def __lt__(self, other):
        return self.id < other.id


class TestJobsTable(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('tethys_gizmos.gizmo_options.jobs_table.JobsTable.set_rows_and_columns')
    def test_JobsTable_init(self, mock_set):
        job1 = JobObject(1, 'name1', 'des1', 1, 1)
        job2 = JobObject(2, 'name2', 'des2', 2, 2)
        jobs = [job1, job2]
        column_fields = ['id', 'name', 'description', 'creation_time', 'run_time']

        ret = gizmo_jobs_table.JobsTable(jobs=jobs, column_fields=column_fields, show_resubmit_btn=True,
                                         show_log_btn=True)

        mock_set.assert_called_with(jobs,  ['id', 'name', 'description', 'creation_time', 'run_time'])
        self.assertIn('run', ret.actions)
        self.assertIn('delete', ret.actions)
        self.assertIn('resubmit', ret.actions)
        self.assertIn('logs', ret.actions)
        self.assertTrue(ret.delay_loading_status)
        self.assertFalse(ret.hover)
        self.assertFalse(ret.bordered)
        self.assertFalse(ret.striped)
        self.assertFalse(ret.condensed)
        self.assertFalse(ret.attributes)
        self.assertEqual('', ret.results_url)
        self.assertEqual('', ret.classes)
        self.assertEqual(5000, ret.refresh_interval)
        self.assertFalse(ret.show_detailed_status)
        self.assertEqual(7, ret.num_cols)

    @mock.patch('tethys_gizmos.gizmo_options.jobs_table.JobsTable.set_rows_and_columns')
    def test_JobsTable_init_monitor_url(self, mock_set):
        job1 = JobObject(1, 'name1', 'des1', 1, 1)
        job2 = JobObject(2, 'name2', 'des2', 2, 2)
        jobs = [job1, job2]
        column_fields = ['id', 'name', 'description', 'creation_time', 'run_time']

        ret = gizmo_jobs_table.JobsTable(jobs=jobs, column_fields=column_fields, monitor_url='monitor')

        self.assertIn('monitor', ret.actions)
        self.assertEqual('monitor', ret.monitor_url)

    @mock.patch('tethys_gizmos.gizmo_options.jobs_table.JobsTable.set_rows_and_columns')
    def test_JobsTable_init_results_url(self, mock_set):
        job1 = JobObject(1, 'name1', 'des1', 1, 1)
        job2 = JobObject(2, 'name2', 'des2', 2, 2)
        jobs = [job1, job2]
        column_fields = ['id', 'name', 'description', 'creation_time', 'run_time']

        ret = gizmo_jobs_table.JobsTable(jobs=jobs, column_fields=column_fields, results_url='results')

        self.assertIn('results', ret.actions)
        self.assertEqual('results', ret.results_url)

    @mock.patch('tethys_gizmos.gizmo_options.jobs_table.JobsTable.set_rows_and_columns')
    def test_JobsTable_init_no_delete_btn(self, mock_set):
        job1 = JobObject(1, 'name1', 'des1', 1, 1)
        job2 = JobObject(2, 'name2', 'des2', 2, 2)
        jobs = [job1, job2]
        column_fields = ['id', 'name', 'description', 'creation_time', 'run_time']

        ret = gizmo_jobs_table.JobsTable(jobs=jobs, column_fields=column_fields, delete_btn=False)

        mock_set.assert_called_with(jobs, ['id', 'name', 'description', 'creation_time', 'run_time'])
        self.assertFalse(ret.actions['delete'])
        self.assertEqual(7, ret.num_cols)

    def test_set_rows_and_columns(self):
        job1 = JobObject(1, 'name1', 'des1', 1, 1)
        job2 = JobObject(2, 'name2', 'des2', 2, 2)
        jobs = [job1, job2]
        column_fields = [('id', '1'), 'name', 'description', 'creation_time', 'run_time', 'extended_properties']

        # This set_rows_and_columns method is called at the init
        result = gizmo_jobs_table.JobsTable(jobs=jobs, column_fields=column_fields)
        self.assertIn(job1.id, result['rows'][0].columns)
        self.assertIn(job1.name, result['rows'][0].columns)
        self.assertIn(job1.description, result['rows'][0].columns)
        self.assertIn(job1.creation_time, result['rows'][0].columns)
        self.assertIn(job1.run_time, result['rows'][0].columns)
        self.assertIn(job2.id, result['rows'][1].columns)
        self.assertIn(job2.name, result['rows'][1].columns)
        self.assertIn(job2.description, result['rows'][1].columns)
        self.assertIn(job2.creation_time, result['rows'][1].columns)
        self.assertIn(job2.run_time, result['rows'][1].columns)

    def test_set_rows_and_columns_no_jobs(self):
        column_fields = ['id', 'name', 'description', 'creation_time', 'run_time']
        result = gizmo_jobs_table.JobsTable(jobs=[], column_fields=column_fields)
        self.assertEqual([], result.rows)
        self.assertEqual([], result.column_fields)
        self.assertEqual([], result.column_names)

    @mock.patch('tethys_gizmos.gizmo_options.jobs_table.log.warning')
    def test_set_rows_and_columns_warning(self, mock_log):
        job1 = JobObject(1, 'name1', 'des1', 1, 1)
        jobs = [job1]
        column_name = 'not_exist'
        column_fields = [column_name]

        gizmo_jobs_table.JobsTable(jobs=jobs, column_fields=column_fields)

        mock_log.assert_called_with('Column %s was not added because the %s has no attribute %s.',
                                    'Not Exist', str(job1), column_name)

    def test_get_gizmo_css(self):
        gizmo_css = gizmo_jobs_table.JobsTable.get_gizmo_css()
        self.assertEqual(2, len(gizmo_css))
        self.assertIn('jobs_table.css', gizmo_css[0])
        self.assertNotIn('.js', gizmo_css[0])

    def test_get_vendor_js(self):
        vendor_js = gizmo_jobs_table.JobsTable.get_vendor_js()
        self.assertEqual(6, len(vendor_js))
        self.assertIn('d3', vendor_js[0])
        self.assertIn('.js', vendor_js[0])
        self.assertNotIn('.css', vendor_js[0])
        self.assertIn('lodash', vendor_js[1])
        self.assertIn('.js', vendor_js[1])
        self.assertNotIn('.css', vendor_js[1])
        self.assertIn('graphlib', vendor_js[2])
        self.assertIn('.js', vendor_js[2])
        self.assertNotIn('.css', vendor_js[2])
        self.assertIn('dagre', vendor_js[3])
        self.assertIn('.js', vendor_js[3])
        self.assertNotIn('.css', vendor_js[3])
        self.assertIn('dagre-d3', vendor_js[4])
        self.assertIn('.js', vendor_js[4])
        self.assertNotIn('.css', vendor_js[4])

    def test_get_gizmo_js(self):
        gizmo_js = gizmo_jobs_table.JobsTable.get_gizmo_js()
        self.assertEqual(1, len(gizmo_js))
        self.assertIn('jobs_table.js', gizmo_js[0])
        self.assertNotIn('.css', gizmo_js[0])

    def test_depricated_exception(self):
        job1 = JobObject(1, 'name1', 'des1', 1, 1)
        job2 = JobObject(2, 'name2', 'des2', 2, 2)
        jobs = [job1, job2]
        column_fields = ['id', 'name', 'description', 'creation_time', 'run_time']

        ret = gizmo_jobs_table.JobsTable(jobs=jobs, column_fields=column_fields, actions=['delete'], run_btn=False)
        self.assertTrue(ret.actions['delete'])
        self.assertFalse(ret.actions['run'])

    @mock.patch('tethys_gizmos.gizmo_options.jobs_table.JobsTable.set_rows_and_columns')
    def test_deprecated_status_actions(self, mock_set):
        job1 = JobObject(1, 'name1', 'des1', 1, 1)
        job2 = JobObject(2, 'name2', 'des2', 2, 2)
        jobs = [job1, job2]
        column_fields = ['id', 'name', 'description', 'creation_time', 'run_time']

        ret = gizmo_jobs_table.JobsTable(jobs=jobs, column_fields=column_fields, status_actions=False)

        mock_set.assert_called_with(jobs, ['id', 'name', 'description', 'creation_time', 'run_time'])
        self.assertFalse(ret.show_actions)
        self.assertEqual(6, ret.num_cols)
