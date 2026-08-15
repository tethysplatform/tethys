"""
********************************************************************************
* Name: condor_workflow
* Author: nswain
* Created On: September 12, 2018
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""

import datetime
import shlex
import shutil
import logging
from pathlib import Path

from condorpy.static import CONDOR_JOB_STATUSES
from django.db import models, transaction
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone

from tethys_compute.models.condor.condor_base import CondorBase
from tethys_compute.models.condor.condor_py_workflow import CondorPyWorkflow
from tethys_compute.models.condor.condor_workflow_node import CondorWorkflowNode

log = logging.getLogger("tethys." + __name__)


class CondorWorkflow(CondorBase, CondorPyWorkflow):
    """
    CondorPy Workflow job type
    """

    # The ClassAd names a reporter reads off the queue to know which job it is looking
    # at and to prove it may report on it. Renaming either breaks every deployed
    # reporter, so they are named here and documented in the Jobs API rather than
    # written inline. See :ref:`jobs_api_report_status`.
    JOB_ID_AD = "TethysJobId"
    JOB_TOKEN_AD = "TethysJobToken"

    node_statuses_updated = models.DateTimeField(blank=True, null=True)

    @property
    def _condor_object(self):
        """
        Returns: an instance of a condorpy Workflow
        """
        return self.condorpy_workflow

    def _execute(self, options=None):
        # Copied rather than extended in place: the ads are this job's, so appending
        # them to the caller's list would leak them into a second submit that reused it.
        options = list(options) if options is not None else []

        options.extend(self.status_report_options)
        self.load_nodes()
        super()._execute(options=options)

    @property
    def status_report_options(self):
        """Submit options that let whatever runs this DAG report its status back.

        The id and a token authorising reports for this job alone are attached to
        the DAGMan job as ClassAds, so a reporter running next to the scheduler can
        read them off the queue and POST to ``report-job-status`` without the portal
        having to be asked. They are inert where nothing is reporting.

        A ClassAd assignment contains spaces and quotes, and condorpy runs a remote
        submit by joining the arguments into a string for a shell while running a
        local one through argv. So the ad is shell-quoted only when it is going to a
        shell; quoting it for the local path would make condor read the quotes as
        part of the value.
        """
        ads = [
            f'+{self.JOB_ID_AD} = "{self.id}"',
            f'+{self.JOB_TOKEN_AD} = "{self.status_report_token}"',
        ]
        if self.scheduler:
            ads = [shlex.quote(ad) for ad in ads]

        options = []
        for ad in ads:
            options.extend(["-append", ad])
        return options

    @property
    def node_statuses_max_age(self):
        """
        Returns: a ``datetime.timedelta`` of how stale persisted node statuses may
            be and still be served instead of reading each node's live status.
        """
        if not hasattr(self, "_node_statuses_max_age"):
            self._node_statuses_max_age = datetime.timedelta(seconds=60)
        return self._node_statuses_max_age

    @property
    def node_statuses_are_current(self):
        """Whether the persisted node statuses are recent enough to serve.

        Views use this to decide whether to render the DAG from
        ``CondorWorkflowNode.cached_node_status`` or to read each node's live status.
        It is time-based rather than a setting so that a deployment with no
        background updater, or one whose updater has stopped, falls back to reading
        live statuses instead of serving values that never advance again.

        The budget is deliberately not ``update_status_interval``. That is the
        minimum time between polls of a single job, whereas this is how stale a
        rendered status may be. A background updater refreshing many jobs takes
        longer per pass than the interval for one job, so tying the two together
        would leave the statuses never current precisely when there is enough load
        for it to matter.

        Age stops mattering once there is nothing left to learn. A workflow that has
        left the queue with every node in a status it cannot leave will never report
        again, so expiring its statuses only sends the views to the scheduler to be
        told the same thing -- and a finished workflow is the one whose working
        directory is most likely to have been cleaned up, which is what reading a
        node's live status needs.
        """
        if self.node_statuses_updated is None:
            return False
        if (
            self.cached_status in self.TERMINAL_STATUSES
            and self.all_node_statuses_are_terminal
        ):
            return True
        return timezone.now() - self.node_statuses_updated < self.node_statuses_max_age

    @property
    def all_node_statuses_are_terminal(self):
        """Whether every node has reached a status it cannot leave.

        Both halves are load-bearing. The workflow's own status is not enough,
        because a node can be reported terminal and then requeued -- a held node
        that DAGMan retries -- and the workflow is only terminal once DAGMan itself
        has departed. The nodes are not enough either: a status recorded by a
        reporter that never sent a final one leaves the last node non-terminal, and
        that is exactly the copy that must not be trusted forever.

        A node with no persisted status has not been heard about at all, so it
        counts against the whole set rather than being skipped.

        Returns: bool
        """
        statuses = list(self.node_set.values_list("cached_node_status", flat=True))
        if not statuses:
            return False
        return all(
            self.STATUS_MAP.get(status) in self.TERMINAL_STATUS_CODES
            for status in statuses
        )

    @property
    def cached_node_statuses(self):
        """Node status counts built from the database instead of the scheduler.

        Mirrors the shape of :attr:`CondorBase.statuses` -- every condor status name
        mapped to the number of nodes currently in it -- but sources the values from
        ``CondorWorkflowNode.cached_node_status``, so no remote call is made. Nodes
        with no persisted status have not been expanded by DAGMan yet and are counted
        as ``Unexpanded``, matching what condorpy reports for an unsubmitted node.
        """
        statuses = {name: 0 for name in CONDOR_JOB_STATUSES.values()}

        for node in self.node_set.all():
            status = node.cached_node_status or "Unexpanded"
            statuses[status] = statuses.get(status, 0) + 1

        return statuses

    def apply_node_statuses(self, status_by_name):
        """Persist node statuses that were determined elsewhere.

        Args:
            status_by_name(dict): condorpy job name -> condor status name. That is
                the node name with spaces replaced by underscores, as built by
                CondorPyJob.condorpy_job. Names matching no node are ignored, as are
                statuses condor does not define -- the caller is remote, so neither
                is trustworthy.

        Returns:
            dict: node name -> condor status name, for the nodes that matched.
        """
        valid_statuses = set(CONDOR_JOB_STATUSES.values())
        updated = {}
        changed = []

        for node in self.node_set.select_subclasses():
            status = status_by_name.get(node.job.name)
            if not status:
                continue
            if status not in valid_statuses:
                log.warning(
                    f"Ignoring unrecognized status {status!r} reported for node "
                    f"{node.name!r} of job {self.id}."
                )
                continue
            if status != node.cached_node_status:
                node.cached_node_status = status
                changed.append(node)
            updated[node.name] = status

        # Nothing matched, so nothing was learned about this workflow. Leaving the
        # freshness stamp alone keeps the views reading live rather than serving a
        # DAG of unexpanded nodes as though it were current.
        if not updated:
            return updated

        with transaction.atomic():
            if changed:
                CondorWorkflowNode.objects.bulk_update(changed, ["cached_node_status"])
            self.node_statuses_updated = timezone.now()
            self.save(update_fields=["node_statuses_updated"])

        return updated

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
