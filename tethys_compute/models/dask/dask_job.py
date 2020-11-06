"""
********************************************************************************
* Name: basic_job
* Author: nswain, teva, tran
* Created On: September 19, 2018
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""
import logging
import datetime

from django.utils import timezone
from django.db import models
from dask.delayed import Delayed
from dask.distributed import Client, Future, fire_and_forget
from tethys_compute.models.tethys_job import TethysJob
from tethys_compute.models.dask.dask_scheduler import DaskScheduler
from tethys_compute.models.dask.dask_field import DaskSerializedField
import json

log = logging.getLogger('tethys.' + __name__)
client_fire_forget = None


class DaskJob(TethysJob):
    """
    Dask job type.
    """
    key = models.CharField(max_length=1024, null=True)
    scheduler = models.ForeignKey(DaskScheduler, on_delete=models.SET_NULL, blank=True, null=True)
    forget = models.BooleanField(default=False)
    result = DaskSerializedField(blank=True, null=True)

    DASK_TO_STATUS_TYPES = {
        # States returned from Scheduler transition event.
        'new-released': 'SUB',
        'released-waiting': 'SUB',
        'waiting-no-worker': 'SUB',
        'no-worker-waiting': 'SUB',
        'no-worker-processing': 'RUN',
        'waiting-processing': 'RES',  # Should technically be RUN, but needs to be RES to get results
        'processing-memory': 'RES',
        'memory-released': 'RES',
        # 'memory-forgotten': 'RES',  # Will freeze processing results if enabled.
        # 'processing-forgotten': 'RES',  # Will freeze processing results if enabled.
        'processing-erred': 'ERR',
        'erred-forgotten': 'ERR',
        # States returned by Future objects
        'pending': 'SUB',
        'processing': 'RUN',
        'finished': 'COM'
    }

    @property
    def client(self):

        if self.scheduler:
            return self.scheduler.client
        else:
            return Client()

    @property
    def update_status_interval(self):
        """
        Override default update status interval.

        Returns:
            datetime.timedelta: update status interval.
        """
        if not hasattr(self, '_update_status_interval'):
            self._update_status_interval = datetime.timedelta(seconds=0)
        return self._update_status_interval

    @property
    def future(self):
        """
        Get Future instance associated with this job. The Future can be used to query status, get results, and manage the dask task.
        
        Returns:
            dask.distributed.Future: a future bound to the key associated with the Dask Job.
        """  # noqa: #E501
        if not getattr(self, '_future', None):
            if self.key and self.client:
                try:
                    future = Future(key=self.key,
                                    client=self.client)
                except Exception:
                    log.exception('Dask Future Init Error')
                    return None
            else:
                return None

            self._future = future

        return self._future

    def _execute(self, future_or_delayed, *args, **kwargs):
        """
        Execute Delayed jobs using the distributed Client to get a future object. Save the key of the future object for later use.

        Args:
            future_or_delayed (dask.Delayed or dask.distributed.Future): dask task object to track using TethysJobs.
        """  # noqa: E501
        if not isinstance(future_or_delayed, Future) and not isinstance(future_or_delayed, Delayed):
            raise ValueError('Must pass a valid instance of Delayed or Future.')

        if isinstance(future_or_delayed, Delayed):
            future = self.client.compute(future_or_delayed)
        else:
            future = future_or_delayed

        self.key = future.key

        # NOTE: Job may not actually be running at this point, but we don't have another
        # way to know when the first node in the workflow starts running.
        self._status = 'RUN'
        self.start_time = timezone.now()

        # Send key to the dask scheduler so the scheduler knows which jobs to send status updates to Tethys.
        self.client.set_metadata(self.key, True)

        # Save updated attributes
        self.save()

        # Must use fire and forget to ensure job runs after the future goes out of scope.
        fire_and_forget(future)

        # Save this client to close it after obtaining the result.
        global client_fire_forget
        client_fire_forget = self.client

    def _update_status(self, *args, **kwargs):
        """
        Check status using a Future, translate to Tethys Jobs status and save.
        """
        # Get Future
        future = self.future

        # Do nothing if no Future
        if not future:
            return

        # Get the status
        dask_status = future.status.lower()

        try:
            # Translate to TethysJob status
            self._status = self.DASK_TO_STATUS_TYPES[dask_status]
            self.save()
            # Clean up client
            self.client.close()

        except KeyError:
            log.error('Unknown Dask Status: "{}"'.format(dask_status))

    def _process_results(self, *args, **kwargs):
        """
        Process results callback. If process_results_function is specified, we call it with the results as an argument, otherwise get the result, serialize, and save to database. Also update job status accordingly.
        """  # noqa: E501
        # Lock before processing results to prevent conflicts
        if not self._acquire_pr_lock():
            return

        # Get the future instance
        future = self.future

        # Skip if no Future
        if not future:
            return

        # Skip processing results if forget
        if self.forget:
            # Clean up client
            self.client.close()
            return

        try:
            # Get results using the client
            result = self.client.gather(future)
        except Exception as e:
            # Tell scheduler to stop sending updates about this key
            self.client.set_metadata(self.key, False)
            # Clean up client
            self.client.close()
            result = e
            log.warning('Exception encountered when retrieving results: "{}"'.format(str(e)))

        # Tell scheduler to stop sending updates about this key
        self.client.set_metadata(self.key, False)

        # Handle custom process results function
        if self.process_results_function:
            # Get the process_results_function in TethysJob and call it with the result retrived
            try:
                result = self.process_results_function(result)
            except Exception as e:
                log.exception('Process Results Function Error')
                self._status = 'ERR'
                result = str(e)

        # Serialize the result
        try:
            self.result = result
        except Exception:
            log.exception('Results Serialization Error')
            self._status = 'ERR'
        else:
            self._status = 'COM' if self._status != 'ERR' else 'ERR'

        # Erase the key to avoid problem with dask recycle key
        self.key = ''

        # save the results or status in the database
        self.save()

        # Clean up client
        self.client.close()

        if client_fire_forget:
            client_fire_forget.close()

        self._release_pr_lock()

    def _acquire_pr_lock(self):
        """
        Processing results lock to prevent collisions between multiple processes.

        Returns:
            bool: True if lock acquired successfully, else False.
        """

        ep = self.extended_properties
        is_processing_results = ep.get('processing_results', False)

        if not is_processing_results:
            ep['processing_results'] = True
            self.extended_properties = ep
            self.save()
            return True
        else:
            log.warning('Unable to aquire lock. Processing results already occurring. Skipping...')
            return False

    def _release_pr_lock(self):
        """
        Release processing results lock.
        """
        ep = self.extended_properties
        ep['processing_results'] = False
        self.extended_properties = ep
        self.save()

    def stop(self):
        """
        Stops job from executing.
        """
        # Get the current future instance
        future = self.future

        # Cancel the job
        if future:
            future.cancel()

    def pause(self):
        """
        Pauses job during execution.
        """
        raise NotImplementedError()

    def resume(self):
        """
        Resumes a job that has been paused.
        """
        raise NotImplementedError()

    def done(self):
        """
        Check if job is finished running.

        Returns:
             bool: True if the job has finished running.
        """
        future = self.future

        if future:
            result = future.done()
            return result

    def retry(self):
        """
        Retry this job.
        """
        future = self.future

        if future:
            future.retry()

    def _resubmit(self, *args, **kwargs):
        """
        Resubmit this job. Simply use the retry function.
        """
        self.retry()

    def _get_logs(self):
        """
        Resubmit this job. Simply use the retry function.
        """
        contents = dict()
        contents['Scheduler'] = self._parse_log_content(self.scheduler.client.get_scheduler_logs())
        log_workers = self.scheduler.client.get_worker_logs()
        for i, (worker, worker_content) in enumerate(log_workers.items()):
            contents[f'Worker-{i}'] = self._parse_log_content(worker_content)
        return contents

    @staticmethod
    def _parse_log_content(log_content):
        if log_content:
            log_content = json.dumps(log_content).strip("[]")
            log_content = log_content.replace("], [", "\n")
        return log_content
