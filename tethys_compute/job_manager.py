"""
********************************************************************************
* Name: job_manager.py
* Author: Scott Christensen
* Created On: 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
from tethys_compute.models import TethysJob, CondorJob, BasicJob
import re

JOB_TYPES = {'CONDOR': CondorJob,
             'BASIC': BasicJob,
            }

class JobManager(object):
    """

    """

    # for backwards compatibility
    JOB_TYPES_DICT = JOB_TYPES

    def __init__(self, app):
        self.app = app
        self.label = app.package
        self.app_workspace = app.get_app_workspace()
        self.job_templates = dict()
        for template in app.job_templates():
            self.job_templates[template.name] = template

    def create_job(self, name, user, template_name, **kwargs):
        try:
            template = self.job_templates[template_name]
        except KeyError, e:
            raise KeyError('A job template with name %s was not defined' % (template_name,))
        JobClass = template.type
        user_workspace = self.app.get_user_workspace(user)

        kwrgs = dict(name=name, user=user, label=self.label, workspace=user_workspace.path)
        parameters = self._replace_workspaces(template.parameters, user_workspace)
        kwrgs.update(parameters)
        kwrgs.update(kwargs)
        job = JobClass(**kwrgs)
        return job

    def list_jobs(self, user=None, order_by='id'):
        """
        Lists all the jobs from current app for current user
        """
        filters = dict()
        filters['label'] = self.label
        if user:
            filters['user'] = user
        jobs = TethysJob.objects.filter(**filters).order_by(order_by)
        jobs = [job.child for job in jobs]
        return jobs

    def get_job(self, job_id, user=None):
        """
        Get job by id
        """
        job = TethysJob.objects.filter(label=self.label, id=job_id)
        if job:
            job = job[0].child

            if user and job.user != user:
                return None

            return job

    def _replace_workspaces(self, parameters, user_workspace):
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
            new_string_value = re.sub('\$\(APP_WORKSPACE\)', self.app_workspace.path, string_value)
            new_string_value = re.sub('\$\(USER_WORKSPACE\)', user_workspace.path, new_string_value)
            return new_string_value

        def replace_in_dict(dict_value):
            new_dict_value = dict()
            for key, value in dict_value.iteritems():
                new_dict_value[key] = replace_in_value(value)
            return new_dict_value

        def replace_in_list(list_value):
            new_list_value = [replace_in_value(value) for value in list_value]
            return new_list_value

        def replace_in_tuple(tuple_value):
            new_tuple_value = tuple(replace_in_list(tuple_value))
            return new_tuple_value

        TYPE_DICT = {str: replace_in_string,
                     dict: replace_in_dict,
                     list: replace_in_list,
                     tuple: replace_in_tuple,
                    }

        new_parameters = dict()
        for parameter, value in parameters.iteritems():
            new_value = replace_in_value(value)
            new_parameters[parameter] = new_value
        return new_parameters


class JobTemplate(object):
    def __init__(self, name, type=None, parameters=None):
        self.name = name
        self.type = type or JOB_TYPES['BASIC']
        self.parameters = parameters or dict()
        assert issubclass(type, TethysJob)
        assert isinstance(parameters, dict)


class BasicJobTemplate(JobTemplate):
    def __init__(self, name, parameters=None):
        super(self.__class__, self).__init__(name, JOB_TYPES['BASIC'], parameters)


class CondorJobTemplate(JobTemplate):
    def __init__(self, name, parameters=None):
        super(self.__class__, self).__init__(name, JOB_TYPES['CONDOR'], parameters)