from tethys_compute.models import TethysJob, CondorJob

class JobManager(object):
    """

    """
    JOB_TYPES_DICT = {
        'CONDOR': CondorJob,
        'BASIC': TethysJob,
    }

    def __init__(self, label, job_templates=None):
        self.label = label
        self.job_templates = dict()
        for template in job_templates:
            self.job_templates[template.name] = template

    def create_job(self, name, user, template_name, **kwargs):
        try:
            template = self.job_templates[template_name]
        except KeyError, e:
            raise KeyError('A job template with name %s was not defined' % (template_name,))
        JobClass = template.type
        kwrgs = dict(name=name, user=user, label=self.label)
        kwrgs.update(template.parameters)
        kwrgs.update(kwargs)
        job = JobClass(**kwrgs)
        return job

    def list_jobs(self, user):
        """Lists all the jobs from current app for current user

        """
        jobs = TethysJob.objects.all(label=self.label, user=user)
        return jobs


class JobTemplate(object):
    def __init__(self, name, type=None, parameters=None):
        self.name = name
        self.type = type or JobManager.JOB_TYPES_DICT['CONDOR']
        self.parameters = parameters or dict()
        assert isinstance(type, TethysJob)
        assert isinstance(parameters, dict)
