import unittest
import tethys_gizmos.gizmo_options.jobs_table as gizmo_jobs_table
import mock


class JobObject(object):
    def __init__(self, id, name, description, creation_time, run_time):
        self.id = id
        self.name = name
        self.description = description
        self.creation_time = creation_time
        self.run_time = run_time


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

        ret = gizmo_jobs_table.JobsTable(jobs=jobs, column_fields=column_fields)

        mock_set.assert_called_with(jobs,  ['id', 'name', 'description', 'creation_time', 'run_time'])
        self.assertTrue(ret.status_actions)
        self.assertTrue(ret.run)
        self.assertTrue(ret.delete)
        self.assertTrue(ret.delay_loading_status)
        self.assertFalse(ret.hover)
        self.assertFalse(ret.bordered)
        self.assertFalse(ret.striped)
        self.assertFalse(ret.condensed)
        self.assertFalse(ret.attributes)
        self.assertEqual('', ret.results_url)
        self.assertEqual('', ret.classes)
        self.assertEqual(5000, ret.refresh_interval)

    def test_set_rows_and_columns(self):
        job1 = JobObject(1, 'name1', 'des1', 1, 1)
        job2 = JobObject(2, 'name2', 'des2', 2, 2)
        jobs = [job1, job2]
        column_fields = ['id', 'name', 'description', 'creation_time', 'run_time']

        # This set_rows_and_columns method is called at the init
        result = gizmo_jobs_table.JobsTable(jobs=jobs, column_fields=column_fields)
        self.assertIn(job1.id, result['rows'][0])
        self.assertIn(job1.name, result['rows'][0])
        self.assertIn(job1.description, result['rows'][0])
        self.assertIn(job1.creation_time, result['rows'][0])
        self.assertIn(job1.run_time, result['rows'][0])
        self.assertIn(job2.id, result['rows'][1])
        self.assertIn(job2.name, result['rows'][1])
        self.assertIn(job2.description, result['rows'][1])
        self.assertIn(job2.creation_time, result['rows'][1])
        self.assertIn(job2.run_time, result['rows'][1])
        self.assertTrue(result['status_actions'])

    @mock.patch('tethys_gizmos.gizmo_options.jobs_table.log.warning')
    def test_set_rows_and_columns_warning(self, mock_log):
        job1 = JobObject(1, 'name1', 'des1', 1, 1)
        jobs = [job1]
        column_name = 'not_exist'
        column_fields = [column_name]

        gizmo_jobs_table.JobsTable(jobs=jobs, column_fields=column_fields)

        mock_log.assert_called_with('Column %s was not added because the %s has no attribute %s.',
                                    'Not Exist', str(job1), column_name)

    def test_get_gizmo_js(self):
        self.assertIn('jobs_table.js', gizmo_jobs_table.JobsTable.get_gizmo_js()[0])
        self.assertNotIn('.css', gizmo_jobs_table.JobsTable.get_gizmo_js()[0])
