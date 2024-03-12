"""
********************************************************************************
* Name: condor_job
* Author: nswain
* Created On: September 12, 2018
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""

import shutil
import logging

from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver

from tethys_compute.models.condor.condor_base import CondorBase
from tethys_compute.models.condor.condor_py_job import CondorPyJob


log = logging.getLogger("tethys." + __name__)


class CondorJob(CondorBase, CondorPyJob):
    """
    CondorPy Job job type
    """

    @property
    def _condor_object(self):
        """
        Returns: an instance of a condorpy job
        """
        return self.condorpy_job

    def _execute(self, queue=None, options=None):
        if options is None:
            options = list()

        self.num_jobs = queue or self.num_jobs
        super()._execute(queue=self.num_jobs, options=options)

    def update_database_fields(self):
        CondorBase.update_database_fields(self)
        CondorPyJob.update_database_fields(self)


@receiver(pre_save, sender=CondorJob)
def condor_job_pre_save(sender, instance, raw, using, update_fields, **kwargs):
    instance.update_database_fields()


@receiver(pre_delete, sender=CondorJob)
def condor_job_pre_delete(sender, instance, using, **kwargs):
    try:
        instance.condor_object.close_remote()
        shutil.rmtree(instance.initial_dir, ignore_errors=True)
    except Exception as e:
        log.exception(str(e))
