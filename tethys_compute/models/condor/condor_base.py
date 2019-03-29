"""
********************************************************************************
* Name: condor_base
* Author: nswain
* Created On: September 12, 2018
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""
from abc import abstractmethod

from django.db import models
from django.utils import timezone

from tethys_compute.models.tethys_job import TethysJob
from tethys_compute.models.condor.condor_scheduler import CondorScheduler


class CondorBase(TethysJob):
    """
    Base class for CondorJob and CondorWorkflow
    """
    cluster_id = models.IntegerField(blank=True, default=0)
    remote_id = models.CharField(max_length=32, blank=True, null=True)
    scheduler = models.ForeignKey(CondorScheduler, on_delete=models.SET_NULL, blank=True, null=True)

    STATUS_MAP = {'Unexpanded': 'SUB',
                  'Idle': 'SUB',
                  'Running': 'RUN',
                  'Removed': 'ABT',
                  'Completed': 'COM',
                  'Held': 'ERR',
                  'Submission_err': 'ERR',
                  'Various': 'VAR',
                  'Various-Complete': 'VCP',
                  }

    @property
    def condor_object(self):
        """
        Returns: an instance of a condorpy job or condorpy workflow with scheduler, cluster_id, and remote_id attributes set
        """  # noqa: E501
        condor_object = self._condor_object
        condor_object._cluster_id = self.cluster_id
        condor_object._cwd = self.workspace
        if self.scheduler:
            condor_object.set_scheduler(self.scheduler.host,
                                        self.scheduler.username,
                                        self.scheduler.password,
                                        self.scheduler.private_key_path,
                                        self.scheduler.private_key_pass
                                        )
            self.remote_id = self.remote_id or condor_object._remote_id
            condor_object._remote_id = self.remote_id
        return condor_object

    @abstractmethod
    def _condor_object(self):
        """
        Returns: an instance of a condorpy job or condorpy workflow
        """
        pass

    @property
    def statuses(self):
        updated = (timezone.now() - self.last_status_update) < self.update_status_interval
        if not (hasattr(self, '_statuses') and updated):
            self._statuses = self.condor_object.statuses

        return self._statuses

    @abstractmethod
    def _execute(self, *args, **kwargs):
        self.cluster_id = self.condor_object.submit(*args, **kwargs)
        self.save()

    def _update_status(self, *args, **kwargs):
        if not self.execute_time:
            return 'PEN'
        try:
            # get the status of the condorpy job/workflow
            condor_status = self.condor_object.status

            if condor_status == 'Various':
                statuses = self.statuses
                running_statuses = statuses['Unexpanded'] + statuses['Idle'] + statuses['Running']
                if not running_statuses:
                    condor_status = 'Various-Complete'
        except Exception:
            condor_status = 'Submission_err'

        self._status = self.STATUS_MAP[condor_status]
        self.save()

    def _process_results(self):
        if self.scheduler:
            self.condor_object.sync_remote_output()
            self.condor_object.close_remote()

    def stop(self):
        self.condor_object.remove()

    def pause(self):
        """
        Pauses job during execution
        """
        pass
        # self.condor_object.hold()

    def resume(self):
        """
        Resumes a job that has been paused
        """
        pass
        # self.condor_object.release()

    def update_database_fields(self):
        self.remote_id = self.remote_id or self._condor_object._remote_id
