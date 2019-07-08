"""
********************************************************************************
* Name: condor_py_job
* Author: nswain
* Created On: September 12, 2018
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""
import os

from condorpy import Templates, Job
from django.db import models

from django.contrib.postgres.fields import ArrayField, JSONField


class CondorPyJob(models.Model):
    """
    Database model for condorpy jobs
    """
    condorpyjob_id = models.AutoField(primary_key=True)
    _attributes = JSONField(default=dict, null=True, blank=True)
    _num_jobs = models.IntegerField(default=1)
    _remote_input_files = ArrayField(
        models.CharField(max_length=1024, null=True, blank=True),
        default=list,
    )

    def __init__(self, *args, **kwargs):
        # if condorpy_template_name or attributes is passed in then get the template and add it to the _attributes
        attributes = kwargs.pop('attributes', dict())
        _attributes = kwargs.get('_attributes', dict())
        attributes.update(_attributes)
        condorpy_template_name = kwargs.pop('condorpy_template_name', None)
        if condorpy_template_name is not None:
            template = self.get_condorpy_template(condorpy_template_name)
            template.update(attributes)
            attributes = template
        kwargs['_attributes'] = attributes
        super().__init__(*args, **kwargs)

    @classmethod
    def get_condorpy_template(cls, template_name):
        template_name = template_name or 'base'
        template = getattr(Templates, template_name, None)
        if not template:
            template = Templates.base
        return template

    @property
    def condorpy_job(self):

        if not hasattr(self, '_condorpy_job'):
            job = Job(name=self.name.replace(' ', '_'),
                      attributes=self.attributes,
                      num_jobs=self.num_jobs,
                      remote_input_files=self.remote_input_files,
                      working_directory=self.workspace)

            self._condorpy_job = job
        return self._condorpy_job

    @property
    def attributes(self):
        return self._attributes

    @attributes.setter
    def attributes(self, attributes):
        assert isinstance(attributes, dict)
        self._attributes = attributes
        self.condorpy_job._attributes = attributes

    @property
    def num_jobs(self):
        return self._num_jobs

    @num_jobs.setter
    def num_jobs(self, num_jobs):
        num_jobs = int(num_jobs)
        self.condorpy_job.num_jobs = num_jobs
        self._num_jobs = num_jobs

    @property
    def remote_input_files(self):
        return self._remote_input_files

    @remote_input_files.setter
    def remote_input_files(self, remote_input_files):
        self.condorpy_job.remote_input_files = remote_input_files
        self._remote_input_files = remote_input_files

    @property
    def initial_dir(self):
        return os.path.join(self.workspace, self.condorpy_job.initial_dir)

    def get_attribute(self, attribute):
        return self.condorpy_job.get(attribute)

    def set_attribute(self, attribute, value):
        setattr(self.condorpy_job, attribute, value)

    def update_database_fields(self):
        self._attributes = self.condorpy_job.attributes
        self.num_jobs = self.condorpy_job.num_jobs
        self.remote_input_files = self.condorpy_job.remote_input_files
