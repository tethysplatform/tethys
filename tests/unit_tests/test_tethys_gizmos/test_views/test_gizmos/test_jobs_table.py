import unittest
import tethys_gizmos.views.gizmos.jobs_table as gizmo_jobs_table
import mock
from django.test import RequestFactory

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

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.log.error')
    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob.objects.get_subclass')
    def test_execute_exception(self, mock_tj, mock_log):
        tj = mock_tj()
        tj.execute.side_effect = Exception('error')

        gizmo_jobs_table.execute(request='', job_id='1')

        mock_log.assert_called_with('The following error occurred when executing job %s: %s', '1', 'error')

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob.objects.get_subclass')
    def test_delete(self, mock_tj):
        tj = mock_tj()
        tj.delete.return_value = mock.MagicMock()

        result = gizmo_jobs_table.delete(request='', job_id='1')

        self.assertEqual(200, result.status_code)

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.log.error')
    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob.objects.get_subclass')
    def test_delete_exception(self, mock_tj, mock_log):
        tj = mock_tj()
        tj.delete.side_effect = Exception('error')

        gizmo_jobs_table.delete(request='', job_id='1')

        mock_log.assert_called_with('The following error occurred when deleting job %s: %s', '1', 'error')

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob.objects.get_subclass')
    def test_update_row(self, mock_tj):
        mock_tj.return_value = mock.MagicMock(status='Various', label='gizmos_showcase')
        rows = [('1', '30'),
                ('2', '18'),
                ('3', '26')]
        column_names = ['ID', 'Time(s)']
        request = RequestFactory().post(reversed('jobs'), {'column_fields': column_names, 'row': rows})
        result = gizmo_jobs_table.update_row(request, job_id='1')

        # Check Result
        self.assertEqual(200, result.status_code)

        # Another Case
        mock_tj.return_value = mock.MagicMock(status='Various', label='test_label')
        result = gizmo_jobs_table.update_row(request, job_id='1')

        # Check Result
        self.assertEqual(200, result.status_code)

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.log.error')
    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob.objects.get_subclass')
    def test_update_row_exception(self, mock_tj, mock_log):
        mock_tj.side_effect = Exception('error')
        rows = [('1', '30'),
                ('2', '18'),
                ('3', '26')]
        column_names = ['ID', 'Time(s)']
        request = RequestFactory().post(reversed('jobs'), {'column_fields': column_names, 'row': rows})
        gizmo_jobs_table.update_row(request, job_id='1')

        # Check Result
        mock_log.assert_called_with('The following error occurred when updating row for job %s: %s', '1', str('error'))

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob.objects.get_subclass')
    def test_update_status(self, mock_tj):
        mock_tj.return_value = mock.MagicMock(status='Various', label='gizmos_showcase')
        rows = [('1', '30'),
                ('2', '18'),
                ('3', '26')]
        column_names = ['ID', 'Time(s)']
        request = RequestFactory().post(reversed('jobs'), {'column_fields': column_names, 'row': rows})
        result = gizmo_jobs_table.update_status(request, job_id='1')

        # Check Result
        self.assertEqual(200, result.status_code)

        # Another Case
        mock_tj.return_value = mock.MagicMock(status='Various', label='test_label')
        result = gizmo_jobs_table.update_status(request, job_id='1')

        # Check Result
        self.assertEqual(200, result.status_code)

    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.log.error')
    @mock.patch('tethys_gizmos.views.gizmos.jobs_table.TethysJob.objects.get_subclass')
    def test_update_status_exception(self, mock_tj, mock_log):
        mock_tj.side_effect = Exception('error')
        rows = [('1', '30'),
                ('2', '18'),
                ('3', '26')]
        column_names = ['ID', 'Time(s)']
        request = RequestFactory().post(reversed('jobs'), {'column_fields': column_names, 'row': rows})
        gizmo_jobs_table.update_status(request, job_id='1')

        mock_log.assert_called_with('The following error occurred when updating status for job %s: %s', '1', str('error'))

    def test_parse_value(self):
        result = gizmo_jobs_table._parse_value('True')
        self.assertTrue(result)

        result = gizmo_jobs_table._parse_value('False')
        self.assertFalse(result)

        result = gizmo_jobs_table._parse_value('Test')
        self.assertEqual('Test', result)
