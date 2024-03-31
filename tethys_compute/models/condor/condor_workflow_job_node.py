"""
********************************************************************************
* Name: condor_workflow_job_node
* Author: nswain
* Created On: September 12, 2018
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""

from django.db.models.signals import pre_save
from django.dispatch import receiver

from tethys_compute.models.condor.condor_workflow_node import CondorWorkflowNode
from tethys_compute.models.condor.condor_py_job import CondorPyJob


class CondorWorkflowJobNode(CondorWorkflowNode, CondorPyJob):
    """
    CondorWorkflow JOB type node
    """

    @property
    def type(self):
        return "JOB"

    @property
    def workspace(self):
        return "."

    @property
    def job(self):
        return self.condorpy_job

    def update_database_fields(self):
        CondorWorkflowNode.update_database_fields(self)
        CondorPyJob.update_database_fields(self)


@receiver(pre_save, sender=CondorWorkflowJobNode)
def condor_workflow_job_node_pre_save(
    sender, instance, raw, using, update_fields, **kwargs
):
    instance.update_database_fields()
