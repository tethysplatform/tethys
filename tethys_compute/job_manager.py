"""
********************************************************************************
* Name: job_manager.py
* Author: Scott Christensen
* Created On: 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
import logging


from django.urls import reverse

from tethys_compute.models.tethys_job import TethysJob
from tethys_compute.models.basic_job import BasicJob
from tethys_compute.models.dask.dask_job import DaskJob
from tethys_compute.models.condor.condor_job import CondorJob
from tethys_compute.models.condor.condor_workflow import CondorWorkflow

log = logging.getLogger('tethys.tethys_compute.job_manager')

JOB_TYPES = {'CONDOR': CondorJob,
             'CONDORJOB': CondorJob,
             'CONDORWORKFLOW': CondorWorkflow,
             'BASIC': BasicJob,
             'DASK': DaskJob,
             }


class JobManager:
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
        self.job_templates = dict()

    def create_job(self, name, user, groups=None, job_type=None, **kwargs):
        """
        Creates a new job from a JobTemplate.

        Args:
            name (str): The name of the job.
            user (django.contrib.auth.User): A User object for the user who creates the job.
            groups(django.contrib.auth.Group, optional): A list of Group object assigned to job. The job will be saved automatically if
             groups are passed in. Default is None.
            job_type (TethysJob): A subclass of TethysJob.
            **kwargs

        Returns:
            A new job object of the type specified by job_type.
        """  # noqa: E501
        # Allow the job class to be passed in as job_type.
        if isinstance(job_type, str):
            job_type = JOB_TYPES[job_type]
        user_workspace = self.app.get_user_workspace(user)
        kwrgs = dict(name=name, user=user, label=self.label, workspace=user_workspace.path)
        kwrgs.update(kwargs)
        job = job_type(**kwrgs)

        if groups:
            # Need to save the job before we can assign the groups
            job.save()
            job.groups.add(groups)
        return job

    def list_jobs(self, user=None, groups=None, order_by='id', filters=None):
        """
        Lists all the jobs from current app for current user.

        Args:
            user (django.contrib.auth.User, optional): The user to filter the jobs by. Default is None. This parameter cannot be passed
            together with the groups parameter. Choose one or the other.
            groups (django.contrib.auth.Group, optional): One or more Group objects to filter the jobs by. Default is None. This parameter
            cannot be passed together with the user parameter. Choose one or the other.
            order_by (str, optional): An expression to order jobs. Default is 'id'.
            filters (dict, optional): A list of key-value pairs to filter the jobs by. Default is None.

        Returns:
            A list of jobs created in the app (and by the user if the user argument is passed in).
        """  # noqa: E501
        if user and groups:
            raise ValueError("The user and groups parameters are mutually exclusive and cannot be passed together. "
                             "Please choose one or the other.")
        filters = filters or dict()
        if 'label' not in filters.keys():
            filters['label'] = self.label

        if groups:
            filters['groups__in'] = groups
        elif user:
            filters['user'] = user

        jobs = TethysJob.objects.filter(**filters).order_by(order_by).select_subclasses()

        return jobs

    def get_job(self, job_id, user=None, filters=None):
        """
        Gets a job by id.

        Args:
            job_id (int): The id of the job to get.
            user (django.contrib.auth.User, optional): The user to filter the jobs by.

        Returns:
            A instance of a subclass of TethysJob if a job with job_id exists (and was created by user if the user argument is passed in).
        """  # noqa: E501
        filters = filters or dict()
        filters.setdefault('label', self.label)
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
