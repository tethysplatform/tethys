"""
********************************************************************************
* Name: tethys_job
* Author: nswain
* Created On: September 12, 2018
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""
import logging
import datetime
import inspect
from abc import abstractmethod

from django.contrib.auth.models import User, Group
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
from model_utils.managers import InheritanceManager

from tethys_apps.base.function_extractor import TethysFunctionExtractor


log = logging.getLogger('tethys.' + __name__)


class TethysJob(models.Model):
    """
    Base class for all job types. This is intended to be an abstract class that is not directly instantiated.
    """
    class Meta:
        verbose_name = 'Job'

    objects = InheritanceManager()

    STATUSES = (
        ('PEN', 'Pending'),
        ('SUB', 'Submitted'),
        ('RUN', 'Running'),
        ('COM', 'Complete'),
        ('ERR', 'Error'),
        ('ABT', 'Aborted'),
        ('VAR', 'Various'),
        ('VCP', 'Various-Complete'),
        ('RES', 'Results-Ready'),
    )

    VALID_STATUSES = [v for v, _ in STATUSES]
    DISPLAY_STATUSES = [k for _, k in STATUSES]
    DISPLAY_STATUSES.insert(3, DISPLAY_STATUSES.pop(6))  # Move 'Various' to be by 'Running'

    PRE_RUNNING_STATUSES = DISPLAY_STATUSES[:2]
    RUNNING_STATUSES = DISPLAY_STATUSES[2:4]
    ACTIVE_STATUSES = DISPLAY_STATUSES[1:4]
    TERMINAL_STATUSES = DISPLAY_STATUSES[4:]

    name = models.CharField(max_length=1024)
    description = models.CharField(max_length=2048, blank=True, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    groups = models.ManyToManyField(Group, verbose_name='groups', related_name='tethys_jobs', blank=True)
    label = models.CharField(max_length=1024)
    creation_time = models.DateTimeField(auto_now_add=True)
    execute_time = models.DateTimeField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    completion_time = models.DateTimeField(blank=True, null=True)
    workspace = models.CharField(max_length=1024, default='')
    extended_properties = JSONField(default=dict, null=True, blank=True)
    _process_results_function = models.CharField(max_length=1024, blank=True, null=True)
    _status = models.CharField(max_length=3, choices=STATUSES, default=STATUSES[0][0])

    def __lt__(self, other):
        return self.id < other.id

    @property
    def type(self):
        """
        Returns the name of Tethys Job type.
        """
        return self.__class__.__name__

    @property
    def update_status_interval(self):
        if not hasattr(self, '_update_status_interval'):
            self._update_status_interval = datetime.timedelta(seconds=10)
        return self._update_status_interval

    @property
    def last_status_update(self):
        if not getattr(self, '_last_status_update', None):
            self._last_status_update = self.execute_time or timezone.now() - self.update_status_interval
        return self._last_status_update

    @property
    def status(self):
        self.update_status()
        field = self._meta.get_field('_status')
        status = self._get_FIELD_display(field)
        return status

    @status.setter
    def status(self, value):
        self.update_status(status=value)

    @property
    def run_time(self):
        start_time = self.start_time or self.execute_time
        if start_time:
            end_time = self.completion_time or datetime.datetime.now(start_time.tzinfo)
            run_time = end_time - start_time
        else:
            return ''

        return run_time

    def execute(self, *args, **kwargs):
        """
        executes the job
        """
        self._execute(*args, **kwargs)
        self.execute_time = timezone.now()
        self._status = 'SUB'
        self.save()

    def update_status(self, status=None, *args, **kwargs):
        """
        Update status of job.
        """
        old_status = self._status

        # Set status from status given
        if status:
            if status not in self.VALID_STATUSES:
                log.error('Invalid status given: {}'.format(status))
                return

            self._status = status
            self.save()

        # Update status if status not given and still pending/running
        elif old_status in ['PEN', 'SUB', 'RUN', 'VAR'] and self.is_time_to_update():
            self._update_status(*args, **kwargs)
            self._last_status_update = timezone.now()

        # Post-process status after update if old status was pending/running
        if old_status in ['PEN', 'SUB', 'RUN', 'VAR']:
            if self._status == 'RUN' and (old_status == 'PEN' or old_status == 'SUB'):
                self.start_time = timezone.now()
            if self._status in ["COM", "VCP", "RES"]:
                self.process_results()
            elif self._status == 'ERR' or self._status == 'ABT':
                self.completion_time = timezone.now()

        self.save()

    def is_time_to_update(self):
        """
        Check if it is time to update again.

        Returns:
            bool: True if update_status_interval or longer has elapsed since our last update, else False.
        """
        time_since_last_update = timezone.now() - self.last_status_update
        is_time_to_update = time_since_last_update > self.update_status_interval
        return is_time_to_update

    @property
    def process_results_function(self):
        """

        Returns:
            A function handle or None if function cannot be resolved.
        """
        if self._process_results_function:
            function_extractor = TethysFunctionExtractor(self._process_results_function, None)
            if function_extractor.valid:
                return function_extractor.function

    @process_results_function.setter
    def process_results_function(self, function):
        if isinstance(function, str):
            self._process_results_function = function
            return
        module_path = inspect.getmodule(function).__name__.split('.')
        module_path.append(function.__name__)
        self._process_results_function = '.'.join(module_path)

    def process_results(self, *args, **kwargs):
        """
        Process the results.
        """
        log.debug('Started processing results for job: {}'.format(self))
        self._process_results(*args, **kwargs)
        self.completion_time = timezone.now()
        self._status = 'COM'
        self.save()
        log.debug('Finished processing results for job: {}'.format(self))

    def resubmit(self):
        self._resubmit()

    def get_logs(self):
        return self._get_logs()

    @abstractmethod
    def _get_logs(self):
        pass

    @abstractmethod
    def _resubmit(self, *args, **kwargs):
        pass

    @abstractmethod
    def _execute(self, *args, **kwargs):
        pass

    @abstractmethod
    def _update_status(self, *args, **kwargs):
        pass

    @abstractmethod
    def _process_results(self, *args, **kwargs):
        pass

    @abstractmethod
    def stop(self):
        """
        Stops job from executing
        """
        raise NotImplementedError()

    @abstractmethod
    def pause(self):
        """
        Pauses job during execution
        """
        raise NotImplementedError()

    @abstractmethod
    def resume(self):
        """
        Resumes a job that has been paused
        """
        raise NotImplementedError()
