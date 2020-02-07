import unittest
from unittest import mock

from tethys_compute.job_manager import JobManager, JOB_TYPES
from tethys_compute.models.tethys_job import TethysJob


class TestJobManager(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_JobManager_init(self):
        mock_app = mock.MagicMock()
        mock_app.package = 'test_label'

        ret = JobManager(mock_app)

        # Check Result
        self.assertEqual(mock_app, ret.app)
        self.assertEqual('test_label', ret.label)

    @mock.patch('tethys_compute.job_manager.CondorJob')
    def test_JobManager_create_job_custom_class(self, mock_cj):
        mock_app = mock.MagicMock()
        mock_app.package = 'test_label'
        mock_app.get_app_workspace.return_value = 'test_app_workspace'
        mock_user_workspace = mock.MagicMock()

        mock_app.get_user_workspace.return_value = mock_user_workspace
        mock_app.get_user_workspace().path = 'test_user_workspace'

        # Execute
        ret_jm = JobManager(mock_app)
        ret_jm.create_job(name='test_name', user='test_user', job_type=mock_cj)
        mock_cj.assert_called_with(label='test_label', name='test_name', user='test_user',
                                   workspace='test_user_workspace')

    @mock.patch('tethys_compute.job_manager.CondorJob')
    def test_JobManager_create_job_string(self, mock_cj):
        mock_app = mock.MagicMock()
        mock_app.package = 'test_label'
        mock_app.get_app_workspace.return_value = 'test_app_workspace'
        mock_user_workspace = mock.MagicMock()

        mock_app.get_user_workspace.return_value = mock_user_workspace
        mock_app.get_user_workspace().path = 'test_user_workspace'

        # Execute
        ret_jm = JobManager(mock_app)
        with mock.patch.dict(JOB_TYPES, {'CONDOR': mock_cj}):
            ret_jm.create_job(name='test_name', user='test_user', job_type='CONDOR')
        mock_cj.assert_called_with(label='test_label', name='test_name', user='test_user',
                                   workspace='test_user_workspace')

    @mock.patch('tethys_compute.job_manager.TethysJob')
    def test_JobManager_list_job(self, mock_tethys_job):
        mock_args = mock.MagicMock()
        mock_jobs = mock.MagicMock()
        mock_tethys_job.objects.filter().order_by().select_subclasses.return_value = mock_jobs

        mock_user = 'foo_user'

        mgr = JobManager(mock_args)
        ret = mgr.list_jobs(user=mock_user)

        self.assertEqual(ret, mock_jobs)
        mock_tethys_job.objects.filter().order_by().select_subclasses.assert_called_once()

    @mock.patch('tethys_compute.job_manager.TethysJob')
    def test_JobManager_get_job(self, mock_tethys_job):
        mock_args = mock.MagicMock()
        mock_app_package = mock.MagicMock()
        mock_args.package = mock_app_package
        mock_jobs = mock.MagicMock()
        mock_tethys_job.objects.get_subclass.return_value = mock_jobs

        mock_job_id = 'fooid'
        mock_user = 'bar'

        mgr = JobManager(mock_args)
        ret = mgr.get_job(job_id=mock_job_id, user=mock_user)

        self.assertEqual(ret, mock_jobs)
        mock_tethys_job.objects.get_subclass.assert_called_once_with(id='fooid', label=mock_app_package, user='bar')

    @mock.patch('tethys_compute.job_manager.TethysJob')
    def test_JobManager_get_job_dne(self, mock_tethys_job):
        mock_args = mock.MagicMock()
        mock_app_package = mock.MagicMock()
        mock_args.package = mock_app_package
        mock_tethys_job.DoesNotExist = TethysJob.DoesNotExist  # Restore original exception
        mock_tethys_job.objects.get_subclass.side_effect = TethysJob.DoesNotExist

        mock_job_id = 'fooid'
        mock_user = 'bar'

        mgr = JobManager(mock_args)
        ret = mgr.get_job(job_id=mock_job_id, user=mock_user)

        self.assertEqual(ret, None)
        mock_tethys_job.objects.get_subclass.assert_called_once_with(id='fooid', label=mock_app_package, user='bar')

    def test_JobManager_get_job_status_callback_url(self):
        mock_args = mock.MagicMock()
        mock_request = mock.MagicMock()
        mock_job_id = 'foo'

        mgr = JobManager(mock_args)
        mgr.get_job_status_callback_url(mock_request, mock_job_id)
        mock_request.build_absolute_uri.assert_called_once_with(u'/update-job-status/foo/')
