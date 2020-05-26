import unittest
from unittest import mock

from django.contrib.auth.models import User, Group
from tethys_compute.job_manager import JobManager, JOB_TYPES
from tethys_compute.models.tethys_job import TethysJob
from tethys_compute.models.condor.condor_scheduler import CondorScheduler
from tethys_apps.models import TethysApp


class TestJobManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app_model = TethysApp(
            name='test_app_job_manager',
            package='test_app_job_manager'
        )
        cls.app_model.save()

        cls.user_model = User.objects.create_user(
            username='test_user_job_manager',
            email='user@example.com',
            password='pass'
        )

        cls.group_model = Group.objects.create(
            name='test_group_job_manager'
        )

        cls.group_model.user_set.add(cls.user_model)

        cls.scheduler = CondorScheduler(
            name='test_scheduler',
            host='localhost',
        )
        cls.scheduler.save()

        cls.tethysjob = TethysJob(
            name='test_tethysjob',
            description='test_description',
            user=cls.user_model,
            label='test_app_job_manager',
        )
        cls.tethysjob.save()

        cls.tethysjob.groups.add(cls.group_model)

    @classmethod
    def tearDownClass(cls):
        cls.tethysjob.delete()
        cls.scheduler.delete()
        cls.group_model.delete()
        cls.user_model.delete()
        cls.app_model.delete()

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

    def test_JobManager_create_job_custom_class(self):
        self.app_model.get_user_workspace = mock.MagicMock()
        self.app_model.get_user_workspace().path = 'test_user_workspace'

        # Execute
        ret_jm = JobManager(self.app_model)
        ret_job = ret_jm.create_job(
            name='test_create_tethys_job',
            user=self.user_model,
            job_type=TethysJob,
            groups=self.group_model,
        )

        self.assertEqual(ret_job.name, 'test_create_tethys_job')
        self.assertEqual(ret_job.user, self.user_model)
        self.assertEqual(ret_job.label, 'test_app_job_manager')
        self.assertIn(self.group_model, ret_job.groups.all())

        ret_job.delete()

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

    def test_JobManager_list_job_with_user(self):

        mgr = JobManager(self.app_model)
        ret = mgr.list_jobs(user=self.user_model)

        self.assertEqual(ret[0], self.tethysjob)

    def test_JobManager_list_job_with_groups(self):

        mgr = JobManager(self.app_model)
        ret = mgr.list_jobs(groups=[self.group_model])

        self.assertEqual(ret[0], self.tethysjob)

    def test_JobManager_list_job_value_error(self):

        mgr = JobManager(self.app_model)
        self.assertRaises(ValueError, mgr.list_jobs, user=self.user_model, groups=[self.group_model])

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
