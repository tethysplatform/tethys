"""
********************************************************************************
* Name: condor_py_job
* Author: nswain
* Created On: September 12, 2018
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""

from tethys_portal.optional_dependencies import optional_import
from pathlib import Path

from django.db import models

# optional imports
Templates = optional_import("Templates", from_module="condorpy")
Job = optional_import("Job", from_module="condorpy")


class CondorPyJob(models.Model):
    """
    Database model for condorpy jobs
    """

    condorpyjob_id = models.AutoField(primary_key=True)
    _attributes = models.JSONField(default=dict, null=True, blank=True)
    _num_jobs = models.IntegerField(default=1)
    _remote_input_files = models.JSONField(default=list, null=True, blank=True)

    def __init__(self, *args, attributes=None, condorpy_template_name=None, **kwargs):
        if attributes is None and condorpy_template_name is None:
            super().__init__(*args, **kwargs)
            return
        if args:
            # Then _attributes might be in args (not necessarily in the second position because of subclasses)
            # It's tricky to extract _attributes from args and add it to kwargs because
            # when the object is initialized from the database, it uses some positional arguments that cannot be
            # converted to kwargs (so it can handle passing pk values in place of instances)
            raise ValueError(
                f"Positional arguments cannot be passed to the {self.__class__.__name__} along with the "
                f'"attributes" or "condorpy_template_name" key-word arguments. Please pass all arguments as '
                f"key-word arguments."
            )
        # if condorpy_template_name or attributes is passed in then get the template and add it to the _attributes
        attributes = attributes or dict()
        _attributes = kwargs.get("_attributes", dict())
        attributes.update(_attributes)
        if condorpy_template_name is not None:
            template = self.get_condorpy_template(condorpy_template_name)
            template.update(attributes)
            attributes = template
        kwargs["_attributes"] = attributes
        super().__init__(**kwargs)

    @classmethod
    def get_condorpy_template(cls, template_name):
        template_name = template_name or "base"
        template = getattr(Templates, template_name, None)
        if not template:
            template = Templates.base
        return template

    @property
    def condorpy_job(self):
        if not hasattr(self, "_condorpy_job"):
            job = Job(
                name=self.name.replace(" ", "_"),
                attributes=self.attributes,
                num_jobs=self.num_jobs,
                remote_input_files=self.remote_input_files,
                working_directory=self.workspace,
            )

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
        return str(Path(self.workspace) / self.condorpy_job.initial_dir)

    def get_attribute(self, attribute):
        return self.condorpy_job.get(attribute)

    def set_attribute(self, attribute, value):
        setattr(self.condorpy_job, attribute, value)

    def update_database_fields(self):
        self._attributes = self.condorpy_job.attributes
        self.num_jobs = self.condorpy_job.num_jobs
        self.remote_input_files = self.condorpy_job.remote_input_files
