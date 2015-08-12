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
        self.workspace = app.get_jobs_workspace()
        self.job_templates = dict()
        for template in app.job_templates():
            self.job_templates[template.name] = template

    def create_job(self, name, user, template_name, **kwargs):
        try:
            template = self.job_templates[template_name]
        except KeyError, e:
            raise KeyError('A job template with name %s was not defined' % (template_name,))
        JobClass = template.type

        kwrgs = dict(name=name, user=user, label=self.label, workspace=self.workspace.path)
        user_workspace = self.app.get_user_workspace(user)
        parameters = self._replace_workspaces(template.parameters, user_workspace)
        kwrgs.update(parameters)
        kwrgs.update(kwargs)
        job = JobClass(**kwrgs)
        return job

    def list_jobs(self, user, order_by='id'):
        """
        Lists all the jobs from current app for current user
        """
        jobs = TethysJob.objects.filter(label=self.label, user=user).order_by(order_by)
        jobs = [job.child for job in jobs]
        return jobs

    def get_job(self, job_id):
        """
        Get job by id
        """
        job = TethysJob.objects.filter(label=self.label, id=job_id)
        if job:
            return job[0].child

    def _replace_workspaces(self, parameters, user_workspace):
        new_parameters = dict()
        for parameter in parameters.values():
            pass
        return parameters


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