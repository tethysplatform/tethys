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

    def test_JobsTable(self):
        job1 = JobObject(1, 'name1', 'des1', 1, 1)
        job2 = JobObject(2, 'name2', 'des2', 2, 2)
        jobs = [job1, job2]
        column_fields = ['id', 'name', 'description', 'creation_time', 'run_time']

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
    def test_jobsTable_warning(self, mock_log):
        job1 = JobObject(1, 'name1', 'des1', 1, 1)
        jobs = [job1]
        column_name = 'id2'
        column_fields = [column_name]

        gizmo_jobs_table.JobsTable(jobs=jobs, column_fields=column_fields)

        mock_log.assert_called_with('Column %s was not added because Job has no attribute %s.',
                                    column_name.title(), column_name)

    def test_get_gizmo_js(self):
        self.assertIn('jobs_table.js', gizmo_jobs_table.JobsTable.get_gizmo_js()[0])
        self.assertNotIn('.css', gizmo_jobs_table.JobsTable.get_gizmo_js()[0])
