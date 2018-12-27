"""
********************************************************************************
* Name: job_manager.py
* Author: Scott Christensen
* Created On: 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
from __future__ import print_function
import re
from abc import abstractmethod
import logging
import warnings


from django.urls import reverse

from tethys_compute.models import (TethysJob,
                                   BasicJob,
                                   CondorJob,
                                   CondorWorkflow,
                                   CondorWorkflowNode,
                                   CondorWorkflowJobNode,
                                   )

log = logging.getLogger('tethys.tethys_compute.job_manager')

JOB_TYPES = {'CONDOR': CondorJob,
             'CONDORJOB': CondorJob,
             'CONDORWORKFLOW': CondorWorkflow,
             'BASIC': BasicJob,
             }


class JobManager(object):
    """
    A manager for interacting with the Jobs database providing a simple interface creating and retrieving jobs.

    Note:
        Each app creates its own instance of the JobManager. The ``get_job_manager`` method returns the app.

        ::

            from app import MyApp as app

            job_manager = app.get_job_manager()
    """

    def __init__(self, app):
        self.app = app
        self.label = app.package
        self.app_workspace = app.get_app_workspace()
        self.job_templates = dict()
        templates = app.job_templates() or list()
        for template in templates:
            self.job_templates[template.name] = template

    def create_job(self, name, user, template_name=None, job_type=None, **kwargs):
        """
        Creates a new job from a JobTemplate.

        Args:
            name (str): The name of the job.
            user (User): A User object for the user who creates the job.
            job_type (TethysJob): A subclass of TethysJob.
            **kwargs

        Returns:
            A new job object of the type specified by job_type.
        """
        if template_name is not None:
            msg = 'The job template "{0}" was used in the "{1}" app. Using job templates is now deprecated.'.format(
                template_name, self.app.package
            )
            warnings.warn(msg, DeprecationWarning)
            print(msg)
            return self.old_create_job(name, user, template_name, **kwargs)

        job_type = JOB_TYPES[job_type]
        user_workspace = self.app.get_user_workspace(user)
        kwrgs = dict(name=name, user=user, label=self.label, workspace=user_workspace.path)
        kwrgs.update(kwargs)
        job = job_type(**kwrgs)
        return job

    def old_create_job(self, name, user, template_name, **kwargs):
        """
        Creates a new job from a JobTemplate.

        Args:
            name (str): The name of the job.
            user (User): A User object for the user who creates the job.
            template_name (str): The name of the JobTemplate from which to create the job.
            **kwargs

        Returns:
            A new job object of the type specified by the JobTemplate
        """
        try:
            template = self.job_templates[template_name]
        except KeyError:
            raise KeyError('A job template with name %s was not defined' % (template_name,))
        user_workspace = self.app.get_user_workspace(user)
        kwrgs = dict(name=name, user=user, label=self.label, workspace=user_workspace.path)
        # parameters = self._replace_workspaces(template.parameters, self.app_workspace, user_workspace)
        # kwrgs.update(parameters)
        kwrgs.update(kwargs)
        job = template.create_job(app_workspace=self.app_workspace, user_workspace=user_workspace, **kwrgs)
        return job

    def list_jobs(self, user=None, order_by='id', filters=None):
        """
        Lists all the jobs from current app for current user.

        Args:
            user (User, optional): The user to filter the jobs by. Default is None.
            order_by (str, optional): An expression to order jobs. Default is 'id'.
            filters (dict, optional): A list of key-value pairs to filter the jobs by. Default is None.

        Returns:
            A list of jobs created in the app (and by the user if the user argument is passed in).
        """
        filters = filters or dict()
        filters['label'] = self.label
        if user:
            filters['user'] = user
        jobs = TethysJob.objects.filter(**filters).order_by(order_by).select_subclasses()
        # jobs = [job.child for job in jobs]
        return jobs

    def get_job(self, job_id, user=None, filters=None):
        """
        Gets a job by id.

        Args:
            job_id (int): The id of the job to get.
            user (User, optional): The user to filter the jobs by.

        Returns:
            A instance of a subclass of TethysJob if a job with job_id exists (and was created by user if the user argument is passed in).
        """  # noqa: E501
        filters = filters or dict()
        filters['label'] = self.label
        filters['id'] = job_id
        if user:
            filters['user'] = user

        try:
            job = TethysJob.objects.get_subclass(**filters)
        except TethysJob.DoesNotExist:
            return None

        return job

    def get_job_status_callback_url(self, request, job_id):
        """
        Get the absolute url to call to update job status
        """
        relative_uri = reverse('update_job_status', kwargs={'job_id': job_id})
        absolute_uri = request.build_absolute_uri(relative_uri)
        return absolute_uri

    @classmethod
    def _replace_workspaces(cls, parameters, app_workspace, user_workspace):
        """
        Replaces all instances of '$(APP_WORKSPACE)' and '$(USER_WORKSPACE)' in job parameters with the actual paths.
        """

        def replace_in_value(value):
            value_type = type(value)
            if value_type in TYPE_DICT.keys():
                replace_func = TYPE_DICT[value_type]
                new_value = replace_func(value)
                return new_value
            return value

        def replace_in_string(string_value):
            new_string_value = re.sub('\$\(APP_WORKSPACE\)', app_workspace.path, string_value)
            new_string_value = re.sub('\$\(USER_WORKSPACE\)', user_workspace.path, new_string_value)
            return new_string_value

        def replace_in_dict(dict_value):
            new_dict_value = dict()
            for key, value in dict_value.items():
                new_dict_value[key] = replace_in_value(value)
            return new_dict_value

        def replace_in_list(list_value):
            new_list_value = [replace_in_value(value) for value in list_value]
            return new_list_value

        def replace_in_tuple(tuple_value):
            new_tuple_value = tuple(replace_in_list(tuple_value))
            return new_tuple_value

        TYPE_DICT = {
            str: replace_in_string,
            dict: replace_in_dict,
            list: replace_in_list,
            tuple: replace_in_tuple,
        }

        new_parameters = dict()
        for parameter, value in parameters.items():
            new_value = replace_in_value(value)
            new_parameters[parameter] = new_value
        return new_parameters


class JobTemplate(object):
    """
    **DEPRECATED**
    A template from which to create a job.

    Args:
        name (str): Name to refer to the template.
        type (TethysJob): A subclass of the TethysJob base class. Use the JOB_TYPE dictionary for possible values.
        parameters (dict): A dictionary of key-value pairs. Each Job type defines the possible parameters.
    """

    def __init__(self, name, type=None, parameters=None):
        self.name = name
        self.type = type or JOB_TYPES['BASIC']
        self.parameters = parameters or dict()
        assert issubclass(type, TethysJob)
        assert isinstance(parameters, dict)
        self.process_parameters()

    @abstractmethod
    def process_parameters(self):
        pass

    def create_job(self, app_workspace, user_workspace, **kwargs):
        parameters = JobManager._replace_workspaces(self.parameters, app_workspace, user_workspace)
        kwargs.update(parameters)
        job = self.type(**kwargs)
        return job


class BasicJobTemplate(JobTemplate):
    """
    **DEPRECATED**
    A subclass of JobTemplate with the ``type`` argument set to BasicJob.

    Args:
        name (str): Name to refer to the template.
        parameters (dict): A dictionary of parameters to pass to the BasicJob constructor.
    """
    def __init__(self, name, parameters=None):
        super(BasicJobTemplate, self).__init__(name, JOB_TYPES['BASIC'], parameters)

    def process_parameters(self):
        pass


class CondorJobDescription(object):
    """
    **DEPRECATED**
    Helper class for CondorJobTemplate and CondorWorkflowJobTemplates. Stores job attributes.
    """
    def __init__(self, condorpy_template_name=None, remote_input_files=None, **kwargs):
        self.remote_input_files = remote_input_files
        self.condorpy_template_name = condorpy_template_name
        self.attributes = kwargs

    def process_attributes(self, app_workspace, user_workspace):
        self.__dict__ = JobManager._replace_workspaces(self.__dict__, app_workspace, user_workspace)


class CondorJobTemplate(JobTemplate):
    """
    **DEPRECATED**
    A subclass of the JobTemplate with the ``type`` argument set to CondorJob.

    Args:
        name (str): Name to refer to the template.
        job_description (CondorJobDescription): An object containing the attributes for the condorpy job.
        scheduler (Scheduler): An object containing the connection information to submit the condorpy job remotely.
    """
    def __init__(self, name, job_description, scheduler=None, **kwargs):
        parameters = dict()
        parameters['scheduler'] = scheduler
        parameters['remote_input_files'] = job_description.remote_input_files
        parameters['condorpy_template_name'] = job_description.condorpy_template_name
        parameters['attributes'] = job_description.attributes
        parameters.update(kwargs)
        super(CondorJobTemplate, self).__init__(name, JOB_TYPES['CONDORJOB'], parameters)

    def process_parameters(self):
        pass


class CondorWorkflowTemplate(JobTemplate):
    """
    **DEPRECATED**
    A subclass of the JobTemplate with the ``type`` argument set to CondorWorkflow.

    Args:
        name (str): Name to refer to the template.
        parameters (dict, DEPRECATED): A dictionary of key-value pairs. Each Job type defines the possible parameters.
        jobs (list): A list of CondorWorkflowJobTemplates.
        max_jobs (dict, optional): A dictionary of category-max_job pairs defining the maximum number of jobs that will run simultaneously from each category.
        config (str, optional): A path to a configuration file for the condorpy DAG.
    """  # noqa: E501
    def __init__(self, name, parameters=None, jobs=None, max_jobs=None, config='', **kwargs):
        parameters = parameters or dict()
        jobs = jobs or list()
        self.node_templates = set(jobs)
        parameters['max_jobs'] = max_jobs
        parameters['config'] = config
        parameters.update(kwargs)
        super(CondorWorkflowTemplate, self).__init__(name, JOB_TYPES['CONDORWORKFLOW'], parameters)

    def process_parameters(self):
        pass
        # instantiate WorkflowNodes from templates
        # add methods to workflow to get nodes by name.

    def create_job(self, app_workspace, user_workspace, **kwargs):
        job = super(CondorWorkflowTemplate, self).create_job(app_workspace, user_workspace, **kwargs)
        job.save()

        node_dict = dict()

        def add_to_node_dict(node):
            if node not in node_dict:
                node_dict[node] = node.create_node(job, app_workspace, user_workspace)

        for node_template in self.node_templates:
            add_to_node_dict(node_template)
            node = node_dict[node_template]
            if 'parents' in node_template.parameters:
                for parent in node_template.parameters['parents']:
                    add_to_node_dict(parent)
                    node.add_parent(node_dict[parent])

        # add code to link nodes
        return job


NODE_TYPES = {'JOB': CondorWorkflowJobNode,
              # 'SUBWWORKFLOW': CondorWorkflowSubworkflowNode,
              # 'DATA': CondorWorkflowDataNode,
              # 'FINAL': CondorWorkflowFinalNode,
              }


class CondorWorkflowNodeBaseTemplate(object):
    """
    **DEPRECATED**
    A template from which to create a job.

    Args:
        name (str): Name to refer to the template.
        type (TethysJob): A subclass of the TethysJob base class. Use the JOB_TYPE dictionary for possible values.
        parameters (dict): A dictionary of key-value pairs. Each Job type defines the possible parameters.
    """

    def __init__(self, name, type=None, parameters=None):
        self.name = name
        self.type = type or NODE_TYPES['JOB']
        self.parameters = parameters or dict()
        assert issubclass(type, CondorWorkflowNode)
        assert isinstance(parameters, dict)
        self.dependencies = set()

    def add_dependency(self, dependency):
        """
        Adds a dependency or parent workflow-job to the current workflow-job.

        Args:
            dependency: Another instance of CondorWorkflowNodeBaseTemplate whose job must be completed before this one.
        """
        assert issubclass(dependency, self.__class__)
        self.dependencies.add(dependency)

    def create_node(self, workflow, app_workspace, user_workspace):
        kwargs = JobManager._replace_workspaces(self.parameters, app_workspace, user_workspace)
        if 'parents' in kwargs:
            kwargs.pop('parents')
        node = self.type(name=self.name, workflow=workflow, **kwargs)
        node.save()
        return node


class CondorWorkflowJobTemplate(CondorWorkflowNodeBaseTemplate):
    """
    **DEPRECATED**
    A subclass of the CondorWorkflowNodeBaseTemplate with the ``type`` argument set to CondorWorkflowJobNode.

    Args:
        name (str): Name to refer to the template.
        job_description (CondorJobDescription): An instance of `CondorJobDescription` containing of key-value pairs of job attributes.
    """  # noqa: E501
    def __init__(self, name, job_description, **kwargs):
        parameters = kwargs
        parameters['remote_input_files'] = job_description.remote_input_files
        parameters['condorpy_template_name'] = job_description.condorpy_template_name
        parameters['attributes'] = job_description.attributes
        super(CondorWorkflowJobTemplate, self).__init__(name, NODE_TYPES['JOB'], parameters)

    def process_parameters(self):
        pass
