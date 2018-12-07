"""
********************************************************************************
* Name: models.py
* Author: Scott Christensen
* Created On: 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
from django.dispatch import receiver
from django.db.models.signals import post_save

from tethys_compute.models.scheduler import Scheduler  # noqa: F401
from tethys_compute.models.condor.condor_scheduler import CondorScheduler  # noqa: F401
from tethys_compute.models.tethys_job import TethysJob  # noqa: F401
from tethys_compute.models.basic_job import BasicJob  # noqa: F401

from tethys_compute.models.condor.condor_base import CondorBase  # noqa: F401
from tethys_compute.models.condor.condor_py_job import CondorPyJob  # noqa: F401
from tethys_compute.models.condor.condor_job import CondorJob  # noqa: F401
from tethys_compute.models.condor.condor_py_workflow import CondorPyWorkflow  # noqa: F401
from tethys_compute.models.condor.condor_workflow import CondorWorkflow  # noqa: F401
from tethys_compute.models.condor.condor_workflow_node import CondorWorkflowNode  # noqa: F401
from tethys_compute.models.condor.condor_workflow_job_node import CondorWorkflowJobNode  # noqa: F401

from tethys_compute.models.dask.dask_job import DaskJob
from tethys_compute.models.dask.dask_scheduler import DaskScheduler  # noqa: F401


@receiver(post_save, sender=DaskJob)
@receiver(post_save, sender=CondorJob)
@receiver(post_save, sender=BasicJob)
@receiver(post_save, sender=TethysJob)
def tethys_job_post_save(sender, instance, raw, using, update_fields, **kwargs):
    if instance.name.find('{id}') >= 0:
        instance.name = instance.name.format(id=instance.id)
        instance.save()
