"""
********************************************************************************
* Name: condor_workflow
* Author: nswain
* Created On: September 12, 2018
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""

import shutil
import logging
from pathlib import Path

from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver

from tethys_compute.models.condor.condor_base import CondorBase
from tethys_compute.models.condor.condor_py_workflow import CondorPyWorkflow
from tethys_compute.models.condor.condor_workflow_node import CondorWorkflowNode


log = logging.getLogger("tethys." + __name__)


class CondorWorkflow(CondorBase, CondorPyWorkflow):
    """
    CondorPy Workflow job type
    """

    @property
    def _condor_object(self):
        """
        Returns: an instance of a condorpy Workflow
        """
        return self.condorpy_workflow

    def _execute(self, options=None):
        if options is None:
            options = list()

        self.load_nodes()
        super()._execute(options=options)

    def _update_status(self, *args, **kwargs):
        if not self.execute_time:
            return "SUB"
        try:
            # get the status of the condorpy job/workflow
            condor_status = self.condor_object.status

            if condor_status == "Running":
                condor_status = "Various"
                statuses = self.statuses

                running_statuses = (
                    statuses["Unexpanded"] + statuses["Idle"] + statuses["Running"]
                )
                if not running_statuses:
                    condor_status = "Various-Complete"

                # Handle case where DAG has been submitted (i.e.: condor_status is running)
                # but jobs have not started (i.e.: all statuses at 0 count)
                num_statuses = 0
                for val in statuses.values():
                    num_statuses += val

                if not num_statuses:
                    condor_status = "Idle"

        except Exception as e:
            log.error(
                "Unexpected exception encountered while attempting to update "
                "CondorWorkflow status: {}".format(str(e))
            )
            condor_status = "Submission_err"

        self._status = self.STATUS_MAP[condor_status]
        self.save()

    def get_job(self, job_name):
        try:
            node = self.node_set.get_subclass(name=job_name)
            return node
        except CondorWorkflowNode.DoesNotExist:
            return None

    def update_database_fields(self):
        CondorBase.update_database_fields(self)
        CondorPyWorkflow.update_database_fields(self)

    def _log_files(self):
        """
        Build a nested dictionary with all the log files we want to retrieve.
        """
        log_folder_list = dict()
        # The first item of the log_folder_list is always the workflow log
        workflow_name = self.name.replace(" ", "_")
        log_folder_list["workflow"] = {
            "out": f"{workflow_name}.dag.dagman.out",
            "log": f"{workflow_name}.dag.dagman.log",
            "error": f"{workflow_name}.dag.lib.err",
        }
        for job_node in self.nodes:
            job_name = job_node.name
            log_file_path = str(Path(job_name) / "logs" / "*.log")
            error_file_path = str(Path(job_name) / "logs" / "*.err")
            out_file_path = str(Path(job_name) / "logs" / "*.out")
            log_folder_list[job_name] = {
                "log": log_file_path,
                "error": error_file_path,
                "output": out_file_path,
            }
        return log_folder_list


@receiver(pre_save, sender=CondorWorkflow)
def condor_workflow_pre_save(sender, instance, raw, using, update_fields, **kwargs):
    instance.update_database_fields()


@receiver(pre_delete, sender=CondorWorkflow)
def condor_workflow_pre_delete(sender, instance, using, **kwargs):
    try:
        instance.condor_object.close_remote()
        shutil.rmtree(instance.workspace, ignore_errors=True)
    except Exception as e:
        log.exception(str(e))
