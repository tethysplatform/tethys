import unittest
import mock

from tethys_compute.job_manager import JobManager, JobTemplate, BasicJobTemplate, CondorJobTemplate,\
    CondorJobDescription, CondorWorkflowTemplate, CondorWorkflowNodeBaseTemplate, CondorWorkflowJobTemplate
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

    def test_JobManager_init(self):
        mock_app = mock.MagicMock()
        mock_app.package = 'test_label'
        mock_app.get_app_workspace.return_value = 'test_app_workspace'

        mock_template1 = mock.MagicMock()
        mock_template1.name = 'template_1'
        mock_template2 = mock.MagicMock()
        mock_template2.name = 'template_2'

        mock_app.job_templates.return_value = [mock_template1, mock_template2]

        # Execute
        ret = JobManager(mock_app)

        # Check Result
        self.assertEqual(mock_app, ret.app)
        self.assertEqual('test_label', ret.label)
        self.assertEqual('test_app_workspace', ret.app_workspace)
        self.assertEqual(mock_template1, ret.job_templates['template_1'])
        self.assertEqual(mock_template2, ret.job_templates['template_2'])

    @mock.patch('tethys_compute.job_manager.print')
    @mock.patch('tethys_compute.job_manager.warnings')
    @mock.patch('tethys_compute.job_manager.JobManager.old_create_job')
    def test_JobManager_create_job_template(self, mock_ocj, mock_warn, mock_print):
        mock_app = mock.MagicMock()
        mock_app.package = 'test_label'
        mock_app.get_app_workspace.return_value = 'test_app_workspace'
        mock_user_workspace = mock.MagicMock()

        mock_app.get_user_workspace.return_value = mock_user_workspace
        mock_app.get_user_workspace().path = 'test_user_workspace'

        mock_template1 = mock.MagicMock()
        mock_template1.name = 'template_1'
        mock_template2 = mock.MagicMock()
        mock_template2.name = 'template_2'

        mock_app.job_templates.return_value = [mock_template1, mock_template2]

        mock_ocj.return_value = 'old_create_job_return_value'
        # Execute
        ret_jm = JobManager(mock_app)
        ret_job = ret_jm.create_job(name='test_name', user='test_user', template_name='template_1')

        # Check result
        self.assertEqual('old_create_job_return_value', ret_job)

        mock_ocj.assert_called_with('test_name', 'test_user', 'template_1')

        # Check if warning message is called
        check_msg = 'The job template "{0}" was used in the "{1}" app. Using job templates is now deprecated.'.format(
            'template_1', 'test_label'
        )
        rts_call_args = mock_warn.warn.call_args_list
        self.assertEqual(check_msg, rts_call_args[0][0][0])
        mock_print.assert_called_with(check_msg)

    @mock.patch('tethys_compute.job_manager.CondorJob')
    def test_JobManager_create_job_template_none(self, mock_cj):
        mock_app = mock.MagicMock()
        mock_app.package = 'test_label'
        mock_app.get_app_workspace.return_value = 'test_app_workspace'
        mock_user_workspace = mock.MagicMock()

        mock_app.get_user_workspace.return_value = mock_user_workspace
        mock_app.get_user_workspace().path = 'test_user_workspace'

        with mock.patch.dict('tethys_compute.job_manager.JOB_TYPES', {'CONDOR': mock_cj}):
            # Execute
            ret_jm = JobManager(mock_app)
            ret_jm.create_job(name='test_name', user='test_user', job_type='CONDOR')
            mock_cj.assert_called_with(label='test_label', name='test_name', user='test_user',
                                       workspace='test_user_workspace')

    def test_old_create_job(self):
        mock_app = mock.MagicMock()
        mock_app.package = 'test_label'
        mock_app.get_app_workspace.return_value = 'test_app_workspace'
        mock_user_workspace = mock.MagicMock()

        mock_app.get_user_workspace.return_value = mock_user_workspace
        mock_app.get_user_workspace().path = 'test_user_workspace'

        mock_template1 = mock.MagicMock()
        mock_template1.name = 'template_1'
        mock_template2 = mock.MagicMock()
        mock_template2.name = 'template_2'

        mock_app.job_templates.return_value = [mock_template1, mock_template2]

        # Execute
        ret_jm = JobManager(mock_app)
        ret_jm.old_create_job(name='test_name', user='test_user', template_name='template_1')
        mock_template1.create_job.assert_called_with(app_workspace='test_app_workspace', label='test_label',
                                                     name='test_name', user='test_user',
                                                     user_workspace=mock_user_workspace,
                                                     workspace='test_user_workspace')

    def test_old_create_job_key_error(self):
        mock_app = mock.MagicMock()

        mock_name = 'foo'
        mock_user = 'foo_user'
        mock_template_name = 'bar'
        mock_app.package = 'test_app_name'

        mgr = JobManager(mock_app)
        self.assertRaises(KeyError, mgr.old_create_job, name=mock_name, user=mock_user,
                          template_name=mock_template_name)

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
        mock_scheduler = mock.MagicMock()
        mock_jd = mock.MagicMock()
        mock_jd.remote_input_files = 'test_input'
        mock_jd.condorpy_template_name = 'test_template'
        mock_jd.attributes = 'test_attributes'
        mock_param = {'workspace': 'test_workspace'}

        ret = CondorJobTemplate(name='test_name', other_params=mock_param, job_description=mock_jd,
                                scheduler=mock_scheduler)

        # Check result
        self.assertEqual(ret.type, CondorJob)
        self.assertEqual('test_name', ret.name)
        self.assertEqual('test_template', ret.parameters['condorpy_template_name'])
        self.assertEqual('test_template', ret.parameters['condorpy_template_name'])
        self.assertEqual(mock_param, ret.parameters['other_params'])
        self.assertEqual(mock_scheduler, ret.parameters['scheduler'])
        self.assertEqual('test_attributes', ret.parameters['attributes'])

    def test_CondorJobTemplate_process_parameters(self):
        mock_name = mock.MagicMock()
        mock_job_description = mock.MagicMock()
        mock_scheduler = mock.MagicMock()
        mock_parameters = {list: ['/foo/app/workspace', '/foo/user/workspace'],
                           'scheduler': mock_scheduler,
                           'remote_input_files': mock_job_description.remote_input_files,
                           'attributes': mock_job_description.attributes}

        ret = CondorJobTemplate(name=mock_name, parameters=mock_parameters, job_description=mock_job_description,
                                scheduler=mock_scheduler)

        self.assertIsNone(ret.process_parameters())

    @mock.patch('tethys_compute.job_manager.CondorJob')
    def test_CondorJobDescription_init(self, mock_job):
        ret = CondorJobDescription(condorpy_template_name='temp1', remote_input_files='rm_files', name='foo')
        self.assertEqual('rm_files', ret.remote_input_files)
        self.assertEqual('temp1', ret.condorpy_template_name)
        self.assertEqual('foo', ret.attributes['name'])

    @mock.patch('tethys_compute.job_manager.JobManager._replace_workspaces')
    def test_CondorJobDescription_process_attributes(self, mock_jm):

        ret_cd = CondorJobDescription(condorpy_template_name='temp1', remote_input_files='rm_files', name='foo')

        mock_app_workspace = mock.MagicMock(path='/foo/app/workspacee')
        mock_user_workspace = mock.MagicMock(path='/foo/user/workspacee')
        before_dict = self.__dict__

        after_dict = before_dict
        after_dict['foo'] = 'bar'
        mock_jm.return_value = after_dict
        ret_cd.process_attributes(app_workspace=mock_app_workspace, user_workspace=mock_user_workspace)

        self.assertEqual(after_dict, ret_cd.__dict__)

    # CondorWorkflowTemplate

    def test_CondorWorkflowTemplate_init(self):
        input_name = 'foo'
        input_parameters = {'param1': 'inputparam1'}
        input_jobs = ['job1', 'job2', 'job3']
        input_max_jobs = 10
        input_config = 'test_path_config_file'

        ret = CondorWorkflowTemplate(name=input_name, parameters=input_parameters, jobs=input_jobs,
                                     max_jobs=input_max_jobs, config=input_config, additional_param='param1')

        self.assertEquals(input_name, ret.name)
        self.assertEquals(input_parameters, ret.parameters)
        self.assertEquals(set(input_jobs), ret.node_templates)
        self.assertEquals(input_max_jobs, ret.parameters['max_jobs'])
        self.assertEquals(input_config, ret.parameters['config'])
        self.assertEquals('param1', ret.parameters['additional_param'])

    @mock.patch('tethys_compute.job_manager.JobTemplate.create_job')
    def test_CondorWorkflowTemplate_create_job(self, mock_save):
        input_name = 'foo'
        input_parameters = {'param1': 'inputparam1'}
        mock_job1 = mock.MagicMock()
        mock_node_parent = mock.MagicMock()
        mock_node_parent.create_node.return_value = 'add_parent_code_line'
        mock_job1.parameters = {'parents': [mock_node_parent]}
        mock_node1 = mock.MagicMock()
        mock_job1.create_node.return_value = mock_node1

        input_jobs = [mock_job1]
        input_max_jobs = 10
        input_config = 'test_path_config_file'

        ret = CondorWorkflowTemplate(name=input_name, parameters=input_parameters, jobs=input_jobs,
                                     max_jobs=input_max_jobs, config=input_config, additional_param='param1')

        app_workspace = '/foo/APP_WORKSPACE'
        user_workspace = '/foo/USER_WORKSPACE'

        # call Execute
        ret.create_job(app_workspace=app_workspace, user_workspace=user_workspace)

        # Check called
        mock_node1.add_parent.assert_called_with('add_parent_code_line')

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
        mock_jd = mock.MagicMock()
        mock_jd.remote_input_files = 'test_input'
        mock_jd.condorpy_template_name = 'test_template'
        mock_jd.attributes = 'test_attributes'

        ret = CondorWorkflowJobTemplate(name='test_name', job_description=mock_jd, other_params='test_kwargs')
        # Check result
        self.assertEqual(ret.type, CondorWorkflowJobNode)
        self.assertEqual('test_name', ret.name)
        self.assertEqual('test_template', ret.parameters['condorpy_template_name'])
        self.assertEqual('test_attributes', ret.parameters['attributes'])
        self.assertEqual('test_kwargs', ret.parameters['other_params'])

    def test_CondorWorkflowJobTemplate_process_parameters(self):
        mock_jd = mock.MagicMock()
        mock_jd.remote_input_files = 'test_input'
        mock_jd.condorpy_template_name = 'test_template'
        mock_jd.attributes = 'test_attributes'

        ret = CondorWorkflowJobTemplate(name='test_name', job_description=mock_jd, other_params='test_kwargs')

        self.assertIsNone(ret.process_parameters())
