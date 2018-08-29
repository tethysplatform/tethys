import unittest
import mock

from tethys_compute.job_manager import JobManager, JobTemplate, BasicJobTemplate, CondorJobTemplate,\
    CondorJobDescription, CondorWorkflowTemplate, CondorWorkflowNodeBaseTemplate, CondorWorkflowJobTemplate
from tethys_compute.job_manager import JOB_CAST
from tethys_compute.models import (TethysJob,
                                   BasicJob,
                                   CondorJob,
                                   CondorWorkflow,
                                   CondorWorkflowJobNode)


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

        self.assertEquals(ret, None)
        mock_tethys_job.objects.get_subclass.assert_called_once_with(id='fooid', label=mock_app_package, user='bar')

    def test_JobManager_get_job_status_callback_url(self):
        mock_args = mock.MagicMock()
        mock_request = mock.MagicMock()
        mock_job_id = 'foo'

        mgr = JobManager(mock_args)
        mgr.get_job_status_callback_url(mock_request, mock_job_id)
        mock_request.build_absolute_uri.assert_called_once_with(u'/update-job-status/foo/')

    def test_JobManager_replace_workspaces(self):
        mock_app_workspace = mock.MagicMock()
        mock_user_workspace = mock.MagicMock()
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
        mock_name = mock.MagicMock()
        mock_type = BasicJob
        mock_parameters = {list: ['/foo/app/workspace', '/foo/user/workspace']}

        ret = JobTemplate(name=mock_name, type=mock_type, parameters=mock_parameters)
        self.assertEquals(mock_name, ret.name)
        self.assertEquals(BasicJob, ret.type)
        self.assertEquals(mock_parameters, ret.parameters)

    @mock.patch('tethys_compute.job_manager.JobManager._replace_workspaces')
    def test_JobTemplate_create_job(self, mock_replace_workspaces):
        mock_name = mock.MagicMock()
        mock_type = BasicJob
        mock_app_workspace = '/foo/APP_WORKSPACE'
        mock_user_workspace = '/foo/APP_WORKSPACE'
        mock_parameters = {list: ['/foo/app/workspace', '/foo/user/workspace']}

        ret = JobTemplate(name=mock_name, type=mock_type, parameters=mock_parameters)
        ret2 = ret.create_job(mock_app_workspace, mock_user_workspace)
        mock_replace_workspaces.assert_called_once()
        self.assertTrue(isinstance(ret2, TethysJob))

    # BasicJobTemplate

    def test_BasicJobTemplate_init(self):
        mock_name = mock.MagicMock()
        mock_parameters = {list: ['/foo/app/workspace', '/foo/user/workspace']}

        ret = BasicJobTemplate(name=mock_name, parameters=mock_parameters)
        self.assertEquals(mock_name, ret.name)
        self.assertEquals(BasicJob, ret.type)
        self.assertEquals(mock_parameters, ret.parameters)

    def test_BasicJobTemplate_process_parameters(self):
        mock_name = mock.MagicMock()
        mock_parameters = {list: ['/foo/app/workspace', '/foo/user/workspace']}

        ret = BasicJobTemplate(name=mock_name, parameters=mock_parameters)
        ret.process_parameters()
        self.assertEquals(mock_name, ret.name)
        self.assertEquals(BasicJob, ret.type)
        self.assertEquals(mock_parameters, ret.parameters)

    # CondorJobTemplate

    def test_CondorJobTemplate_init_job_description(self):
        mock_name = mock.MagicMock()
        mock_job_description = mock.MagicMock()
        mock_scheduler = mock.MagicMock()
        mock_parameters = {list: ['/foo/app/workspace', '/foo/user/workspace'],
                           'scheduler': mock_scheduler,
                           'remote_input_files': mock_job_description.remote_input_files,
                           'attributes': mock_job_description.attributes}

        ret = CondorJobTemplate(name=mock_name, parameters=mock_parameters, job_description=mock_job_description,
                                scheduler=mock_scheduler)
        self.assertEquals(mock_name, ret.name)
        self.assertEquals(CondorJob, ret.type)
        self.assertEquals(mock_parameters, ret.parameters)

    @mock.patch('tethys_compute.job_manager.warnings')
    def test_CondorJobTemplate_init_no_job_description(self, mock_warnings):
        mock_name = mock.MagicMock()
        mock_scheduler = mock.MagicMock()
        mock_parameters = {list: ['/foo/app/workspace', '/foo/user/workspace'],
                           'scheduler': mock_scheduler}

        ret = CondorJobTemplate(name=mock_name, parameters=mock_parameters, job_description=None,
                                scheduler=mock_scheduler)
        self.assertEquals(mock_name, ret.name)
        self.assertEquals(CondorJob, ret.type)
        self.assertEquals(mock_parameters, ret.parameters)
        msg = 'The job_description argument was not defined in the job_template {0}. ' \
              'This argument will be required in version 1.5 of Tethys.'.format(mock_name)
        mock_warnings.warn.assert_called_once_with(msg, DeprecationWarning)

    @mock.patch('tethys_compute.job_manager.CondorJob.get_condorpy_template')
    def test_CondorJobTemplate_process_parameters(self, mock_get_condorpy_template):
        mock_name = mock.MagicMock()
        mock_job_description = mock.MagicMock()
        mock_scheduler = mock.MagicMock()
        mock_condorpy = mock.MagicMock()
        mock_template = {'condorpy_template_name': mock_condorpy}
        mock_get_condorpy_template.return_value = mock_template
        mock_parameters = {list: ['/foo/app/workspace', '/foo/user/workspace'],
                           'scheduler': mock_scheduler,
                           'remote_input_files': mock_job_description.remote_input_files,
                           'attributes': mock_job_description.attributes,
                           'executable': '/foo',
                           'condorpy_template_name': mock_condorpy}

        ret = CondorJobTemplate(name=mock_name, parameters=mock_parameters, job_description=mock_job_description,
                                scheduler=mock_scheduler)
        self.assertEquals(mock_name, ret.name)
        self.assertEquals(CondorJob, ret.type)
        self.assertEquals(mock_parameters, ret.parameters)

    # CondorJobDescription

    @mock.patch('tethys_compute.job_manager.CondorJob')
    def test_CondorJobDescription_init(self, mock_job):
        mock_template_name = mock.MagicMock()
        mock_remote_input_files = mock.MagicMock()
        mock_template = {mock_template_name: mock_remote_input_files}
        mock_job.get_condorpy_template.return_value = mock_template
        ret = CondorJobDescription(condorpy_template_name=mock_template_name,
                                   remote_input_files=mock_remote_input_files)
        self.assertEquals(mock_remote_input_files, ret.remote_input_files)
        self.assertEquals(mock_template, ret.attributes)

    @mock.patch('tethys_compute.job_manager.CondorJob')
    def test_CondorJobDescription_process_attributes(self, mock_job):
        mock_template_name = mock.MagicMock()
        mock_remote_input_files = mock.MagicMock()
        mock_template = {mock_template_name: mock_remote_input_files}
        mock_job.get_condorpy_template.return_value = mock_template
        mock_app_workspace = mock.MagicMock()
        mock_user_workspace = mock.MagicMock()

        ret = CondorJobDescription(condorpy_template_name=mock_template_name,
                                   remote_input_files=mock_remote_input_files)
        self.assertEquals(mock_remote_input_files, ret.remote_input_files)
        self.assertEquals(mock_template, ret.attributes)

        ret.process_attributes(app_workspace=mock_app_workspace, user_workspace=mock_user_workspace)
        self.assertEquals({'attributes': mock_template, 'remote_input_files': mock_remote_input_files}, ret.__dict__)

    # CondorWorkflowTemplate

    def test_CondorWorkflowTemplate_init(self):
        mock_name = mock.MagicMock()
        mock_job_description = mock.MagicMock()
        mock_scheduler = mock.MagicMock()
        mock_parameters = {list: ['/foo/app/workspace', '/foo/user/workspace'],
                           'scheduler': mock_scheduler,
                           'remote_input_files': mock_job_description.remote_input_files,
                           'attributes': mock_job_description.attributes}
        mock_job1 = mock.MagicMock()
        mock_job2 = mock.MagicMock()
        mock_jobs = [mock_job1, mock_job2]
        mock_config = mock.MagicMock()

        ret = CondorWorkflowTemplate(name=mock_name, parameters=mock_parameters, jobs=mock_jobs, mock_max_jobs=None,
                                     config=mock_config)
        self.assertEquals(mock_name, ret.name)
        self.assertEquals(CondorWorkflow, ret.type)
        self.assertEquals(mock_parameters, ret.parameters)
        self.assertEquals(set(mock_jobs), ret.node_templates)

    @mock.patch('tethys_compute.job_manager.CondorWorkflow.save')
    def test_CondorWorkflowTemplate_create_job(self, mock_condor_workflow):
        from tethys_compute.models import Scheduler

        mock_name = mock.MagicMock()
        mock_scheduler = mock.MagicMock()
        mock_scheduler.__class__ = Scheduler
        mock_parameters = {}
        mock_job1 = mock.MagicMock()
        mock_job_parent = mock.MagicMock()
        mock_job1.parameters = {'parents': [mock_job_parent]}
        mock_jobs = [mock_job1]
        mock_config = mock.MagicMock()
        mock_app_workspace = '/foo/APP_WORKSPACE'
        mock_user_workspace = '/foo/USER_WORKSPACE'
        mock_condor_workflow.return_value = True

        template = CondorWorkflowTemplate(name=mock_name, parameters=mock_parameters, jobs=mock_jobs,
                                          config=mock_config)
        ret = template.create_job(app_workspace=mock_app_workspace, user_workspace=mock_user_workspace)
        self.assertTrue(isinstance(ret, CondorWorkflow))

    # CondorWorkflowNodeBaseTemplate

    def test_CondorWorkflowNodeBaseTemplate_init(self):
        mock_name = mock.MagicMock()
        mock_type = CondorWorkflowJobNode
        mock_parameters = {}

        ret = CondorWorkflowNodeBaseTemplate(name=mock_name, type=mock_type, parameters=mock_parameters)
        self.assertEquals(mock_name, ret.name)
        self.assertEquals(CondorWorkflowJobNode, ret.type)
        self.assertEquals(mock_parameters, ret.parameters)

    @mock.patch('tethys_compute.job_manager.issubclass')
    def test_CondorWorkflowNodeBaseTemplate_add_dependency(self, mock_issubclass):
        mock_name = mock.MagicMock()
        mock_type = CondorWorkflowJobNode
        mock_parameters = {}
        mock_dependency = mock.MagicMock()
        dep_set = set()
        dep_set.add(mock_dependency)
        mock_issubclass.return_value = True

        ret = CondorWorkflowNodeBaseTemplate(name=mock_name, type=mock_type, parameters=mock_parameters)
        ret.add_dependency(mock_dependency)
        self.assertEquals(dep_set, ret.dependencies)

    @mock.patch('tethys_compute.job_manager.CondorWorkflowNode.save')
    @mock.patch('tethys_compute.job_manager.JobManager._replace_workspaces')
    def test_CondorWorkflowNodeBaseTemplate_create_node(self, mock_replace, mock_node_save):
        mock_name = mock.MagicMock()
        mock_type = CondorWorkflowJobNode
        mock_job1 = mock.MagicMock()
        mock_job_parent = mock.MagicMock()
        mock_job1.parameters = {'parents': [mock_job_parent]}
        mock_parameters = {'parents': [mock_job_parent]}
        mock_app_workspace = '/foo/APP_WORKSPACE'
        mock_user_workspace = '/foo/USER_WORKSPACE'
        mock_workflow = mock.MagicMock()
        mock_workflow.__class__ = CondorWorkflow
        mock_node_save.return_value = True
        mock_replace.return_value = {'parents': [mock_job_parent],
                                     'num_jobs': 1,
                                     'remote_input_files': []}

        ret = CondorWorkflowNodeBaseTemplate(name=mock_name, type=mock_type, parameters=mock_parameters)
        node = ret.create_node(mock_workflow, mock_app_workspace, mock_user_workspace)

        self.assertTrue(isinstance(node, CondorWorkflowJobNode))
        self.assertEquals(mock_parameters, ret.parameters)
        self.assertEquals('JOB', node.type)
        self.assertEquals('', node.workspace)

    # CondorWorkflowJobTemplate

    def test_CondorWorkflowJobTemplate_init(self):
        mock_name = mock.MagicMock()

        mock_job_description = mock.MagicMock()
        mock_job_description.remote_input_files = mock.MagicMock()
        mock_job_description.attributes = mock.MagicMock()

        mock_parameters = {list: ['/foo/app/workspace', '/foo/user/workspace'],
                           'remote_input_files': mock_job_description.remote_input_files,
                           '_attributes': mock_job_description.attributes}

        ret = CondorWorkflowJobTemplate(name=mock_name, job_description=mock_job_description)

        self.assertEquals(mock_parameters['remote_input_files'], ret.parameters['remote_input_files'])
        self.assertEquals(mock_parameters['_attributes'], ret.parameters['_attributes'])

    def test_CondorWorkflowJobTemplate_process_parameters(self):
        mock_name = mock.MagicMock()

        mock_job_description = mock.MagicMock()
        mock_job_description.remote_input_files = mock.MagicMock()
        mock_job_description.attributes = mock.MagicMock()

        mock_parameters = {list: ['/foo/app/workspace', '/foo/user/workspace'],
                           'remote_input_files': mock_job_description.remote_input_files,
                           '_attributes': mock_job_description.attributes}

        ret = CondorWorkflowJobTemplate(name=mock_name, job_description=mock_job_description)
        ret.process_parameters()

        self.assertEquals(mock_parameters['remote_input_files'], ret.parameters['remote_input_files'])
        self.assertEquals(mock_parameters['_attributes'], ret.parameters['_attributes'])
