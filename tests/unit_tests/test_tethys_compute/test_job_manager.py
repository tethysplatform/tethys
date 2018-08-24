import unittest
import mock

from tethys_compute.job_manager import JobManager, JobTemplate, BasicJobTemplate, CondorJobTemplate, CondorJobDescription
from tethys_compute.job_manager import JOB_CAST
from tethys_compute.models import TethysJob


class TestJobManager(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('tethys_compute.job_manager.warnings.warn')
    def test_JobManager_init(self, mock_warn):
        mock_args = mock.MagicMock()

        mock_app_package = mock.MagicMock()
        mock_args.package = mock_app_package

        mock_get_app_workspace = mock.MagicMock()
        mock_args.get_app_workspace = mock_get_app_workspace

        mock_template1 = mock.MagicMock()
        mock_template1.__class__ = JobTemplate
        mock_template1.name = 'foo'
        mock_template1.type = 'footype'
        mock_parameters = mock.MagicMock()
        mock_template1.parameters = mock_parameters
        mock_args.job_templates.return_value = {mock_template1}

        with mock.patch.dict(JOB_CAST, {'footype': mock.MagicMock}, clear=True):
            ret = JobManager(mock_args)

        self.assertEquals(mock_args, ret.app)
        self.assertEquals(mock_args.package, ret.label)
        self.assertEquals(mock_get_app_workspace(), ret.app_workspace)
        self.assertTrue('foo' in ret.job_templates)
        mock_warn.assert_called_once()

    @mock.patch('tethys_compute.job_manager.issubclass')
    def test_JobManager_create_empty_job(self, mock_issubclass):
        mock_args = mock.MagicMock()

        mock_app_package = mock.MagicMock()
        mock_args.package = mock_app_package

        mock_get_user_workspace = mock.MagicMock()
        mock_args.get_user_workspace = mock_get_user_workspace

        mock_name = 'foo'
        mock_user = 'foo_user'
        mock_job_type = mock.MagicMock()
        mock_job_type.return_value = True
        mock_issubclass.return_value = True

        ret = JobManager(mock_args).create_empty_job(mock_name, mock_user, mock_job_type)
        self.assertTrue(ret)
        mock_job_type.assert_called_once_with(label=mock_app_package, name='foo',
                                              workspace=mock_get_user_workspace().path, user='foo_user')
        mock_args.get_user_workspace.assert_any_call('foo_user')

    def test_JobManager_create_job(self):
        mock_args = mock.MagicMock()

        mock_app_package = mock.MagicMock()
        mock_args.package = mock_app_package

        mock_get_app_workspace = mock.MagicMock()
        mock_args.get_app_workspace = mock_get_app_workspace

        mock_get_user_workspace = mock.MagicMock()
        mock_args.get_user_workspace = mock_get_user_workspace

        mock_template1 = mock.MagicMock()
        mock_template1.__class__ = JobTemplate
        mock_template1.name = 'foo'
        mock_template1.type = 'footype'
        mock_parameters = mock.MagicMock()
        mock_template1.parameters = mock_parameters
        mock_args.job_templates.return_value = {mock_template1}

        # Create a JobManager with a template
        with mock.patch.dict(JOB_CAST, {'footype': mock.MagicMock}, clear=True):
            mgr = JobManager(mock_args)

        # Now, create the job
        mock_name = 'foo'
        mock_user = 'foo_user'
        mock_template_name = 'foo'

        mgr.create_job(name=mock_name, user=mock_user, template_name=mock_template_name)

        mock_template1.create_job.assert_called_once_with(app_workspace=mock_get_app_workspace(),
                                                          label=mock_app_package,
                                                          name='foo', user='foo_user',
                                                          user_workspace=mock_get_user_workspace(),
                                                          workspace=mock_get_user_workspace().path)
        mock_args.get_user_workspace.assert_any_call('foo_user')

    def test_JobManager_create_job_assertion(self):
        mock_args = mock.MagicMock()
        mock_job_type = mock.MagicMock()

        mock_name = 'foo'
        mock_user = 'foo_user'
        mock_template_name = 'bar'

        mgr = JobManager(mock_args)
        self.assertRaises(KeyError, mgr.create_job, name=mock_name, user=mock_user, template_name=mock_template_name)

    @mock.patch('tethys_compute.job_manager.TethysJob')
    def test_JobManager_list_job(self, mock_tethys_job):
        mock_args = mock.MagicMock()
        mock_jobs = mock.MagicMock()
        mock_tethys_job.objects.filter().order_by().select_subclasses.return_value = mock_jobs

        mock_user = 'foo_user'

        mgr = JobManager(mock_args)
        ret = mgr.list_jobs(user=mock_user)

        self.assertEquals(ret, mock_jobs)
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

        self.assertEquals(ret, mock_jobs)
        mock_tethys_job.objects.get_subclass.assert_called_once_with(id='fooid', label=mock_app_package, user='bar')

    # @mock.patch('tethys_compute.job_manager.TethysJob')
    # def test_JobManager_get_job_assert(self, mock_tethys_job):
    #     mock_args = mock.MagicMock()
    #     mock_app_package = mock.MagicMock()
    #     mock_args.package = mock_app_package
    #     mock_tethys_job.objects.get_subclass.side_effect = TethysJob.DoesNotExist
    #
    #     mock_job_id = 'fooid'
    #     mock_user = 'bar'
    #
    #     mgr = JobManager(mock_args)
    #     ret = mgr.get_job(job_id=mock_job_id, user=mock_user)
    #
    #     self.assertEquals(ret, None)
    #     mock_tethys_job.objects.get_subclass.assert_called_once_with(id='fooid', label=mock_app_package, user='bar')

    def test_JobManager_get_job_status_callback_url(self):
        mock_args = mock.MagicMock()
        mock_request = mock.MagicMock()
        mock_job_id = 'foo'

        mgr = JobManager(mock_args)
        mgr.get_job_status_callback_url(mock_request, mock_job_id)
        mock_request.build_absolute_uri.assert_called_once_with(u'/update-job-status/foo/')

    def test_JobManager_replace_workspaces(self):
        mock_parameters = mock.MagicMock()
        mock_app_workspace = mock.MagicMock()
        mock_user_workspace = mock.MagicMock()

        # mock_app_workspace.path = '/foo/app/$(APP_WORKSPACE)/foo'
        # mock_user_workspace.path = '/foo/user/$(USER_WORKSPACE)/foo'
        mock_app_workspace.path = 'replace_app'
        mock_user_workspace.path = 'replace_user'

        mock_parameters = {str: '/foo/app/$(APP_WORKSPACE)/foo',
                           dict: {'foo': '/foo/user/$(USER_WORKSPACE)/foo'},
                           list: ['/foo/app/$(APP_WORKSPACE)/foo', '/foo/user/$(USER_WORKSPACE)/foo'],
                           tuple: ('/foo/app/$(APP_WORKSPACE)/foo', '/foo/user/$(USER_WORKSPACE)/foo'),
                           int: 1
                           }

        expected = {str: '/foo/app/replace_app/foo',
                    dict: {'foo': '/foo/user/replace_user/foo'},
                    list: ['/foo/app/replace_app/foo', '/foo/user/replace_user/foo'],
                    tuple: ('/foo/app/replace_app/foo', '/foo/user/replace_user/foo'),
                    int: 1
                    }

        ret = JobManager._replace_workspaces(mock_parameters, mock_app_workspace, mock_user_workspace)
        self.assertEquals(ret, expected)


    # JobTemplate

    def test_JobTemplate_init(self):
        pass

    def test_JobTemplate_create_job(self):
        pass

    # BasicJobTemplate

    def test_BasicJobTemplate_init(self):
        pass

    def test_process_parameters(self):
        pass

    # CondorJobTemplate

    def test_CondorJobTemplate_init(self):
        pass

    def test_CondorJobTemplate_process_parameters(self):
        pass

    # CondorJobDescription

    def test_CondorJobDescription_init(self):
        pass

    @mock.patch('tethys_compute.job_manager.CondorJobDescription')
    def test_CondorJobDescription_process_attributes(self, mock_condor_description):
        mock_app_workspace = mock.MagicMock()
        mock_app_user_space = mock.MagicMock()
        # import pdb
        # pdb.set_trace()

        # CondorJobDescription.process_attributes(mock_condor_description, mock_app_workspace, mock_app_user_space)














    def test_CondorWorkflowTemplate_init(self):
        pass

    def test_CondorWorkflowTemplate_create_job(self):
        pass

    def test_CondorWorkflowNodeBaseTemplate_init(self):
        pass

    def test_CondorWorkflowNodeBaseTemplate_add_dependency(self):
        pass

    def test_CondorWorkflowNodeBaseTemplate_create_node(self):
        pass




