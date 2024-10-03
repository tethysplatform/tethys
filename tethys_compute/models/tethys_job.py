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
from django.db import models
from django.utils import timezone
from model_utils.managers import InheritanceManager

from tethys_apps.base.function_extractor import TethysFunctionExtractor


log = logging.getLogger("tethys." + __name__)


class TethysJob(models.Model):
    """
    Base class for all job types. This is intended to be an abstract class that is not directly instantiated.
    """

    class Meta:
        verbose_name = "Job"
        permissions = [
            ("jobs_table_actions", "Can access job's table endpoints for all jobs."),
        ]

    objects = InheritanceManager()

    STATUSES = (
        ("PEN", "Pending"),
        ("SUB", "Submitted"),
        ("RUN", "Running"),
        ("VAR", "Various"),
        ("PAS", "Paused"),
        ("COM", "Complete"),
        ("ERR", "Error"),
        ("ABT", "Aborted"),
        ("VCP", "Various-Complete"),
        ("RES", "Results-Ready"),
        ("OTH", "Other"),
    )

    VALID_STATUSES = [v for v, _ in STATUSES]
    DISPLAY_STATUSES = [k for _, k in STATUSES]
    REVERSE_STATUSES = {v: k for k, v in STATUSES}

    PRE_RUNNING_STATUSES = DISPLAY_STATUSES[:2]
    RUNNING_STATUSES = DISPLAY_STATUSES[2:4]
    ACTIVE_STATUSES = DISPLAY_STATUSES[1:5]
    NON_TERMINAL_STATUSES = DISPLAY_STATUSES[0:5]
    TERMINAL_STATUSES = DISPLAY_STATUSES[5:-1]

    NON_TERMINAL_STATUS_CODES = VALID_STATUSES[0:5]
    TERMINAL_STATUS_CODES = VALID_STATUSES[5:-1]

    OTHER_STATUS_KEY = "__other_status__"

    name = models.CharField(max_length=1024)
    description = models.CharField(max_length=2048, blank=True, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    groups = models.ManyToManyField(
        Group, verbose_name="groups", related_name="tethys_jobs", blank=True
    )
    label = models.CharField(max_length=1024)
    creation_time = models.DateTimeField(auto_now_add=True)
    execute_time = models.DateTimeField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    completion_time = models.DateTimeField(blank=True, null=True)
    workspace = models.CharField(max_length=1024, default="")
    extended_properties = models.JSONField(default=dict, null=True, blank=True)
    status_message = models.CharField(max_length=2048, blank=True, null=True)
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

    @classmethod
    def _add_custom_status(cls, status, status_categories):
        """
        Adds a custom status to all ``status_categories`` lists if they are not already in the list.

        Args:
            status (str): Name of the custom status to add
            status_categories (list of lists): a list of the status category lists defined on this class:
                (i.e. ``PRE_RUNNING_STATUSES``, ``RUNNING_STATUSES``, ``ACTIVE_STATUSES``,
                 ``NON_TERMINAL_STATUSES``, ``TERMINAL_STATUSES``)
        """
        for status_list in status_categories:
            if status not in status_list:
                status_list.append(status)

    @classmethod
    def add_custom_pre_running_status(cls, status):
        """
        Classify a custom status as a "Pre-Running" Status.
        The status will be added to ``PRE_RUNNING_STATUSES`` and ``NON_TERMINAL_STATUSES``.

        Args:
            status (str): The name of the status to classify
        """
        cls._add_custom_status(
            status, (cls.PRE_RUNNING_STATUSES, cls.NON_TERMINAL_STATUSES)
        )

    @classmethod
    def add_custom_running_status(cls, status):
        """
        Classify a custom status as a "Running" Status.
        The status will be added to ``RUNNING_STATUSES``, ``ACTIVE_STATUSES``, and ``NON_TERMINAL_STATUSES``.

        Args:
            status (str): The name of the status to classify
        """
        cls._add_custom_status(
            status,
            (cls.RUNNING_STATUSES, cls.ACTIVE_STATUSES, cls.NON_TERMINAL_STATUSES),
        )

    @classmethod
    def add_custom_active_status(cls, status):
        """
        Classify a custom status as an "Active" Status.
        The status will be added to ``ACTIVE_STATUSES`` and ``NON_TERMINAL_STATUSES``.

        Args:
            status (str): The name of the status to classify
        """
        cls._add_custom_status(status, (cls.ACTIVE_STATUSES, cls.NON_TERMINAL_STATUSES))

    @classmethod
    def add_custom_terminal_status(cls, status):
        """
        Classify a custom status as a "Terminal" Status.
        The status will be added to ``TERMINAL_STATUSES``.

        Args:
            status (str): The name of the status to classify
        """
        cls._add_custom_status(status, (cls.TERMINAL_STATUSES,))

    @property
    def update_status_interval(self):
        """
        Returns a ``datetime.timedelta`` of the minimum time between updating the status of a job.

        """
        if not hasattr(self, "_update_status_interval"):
            self._update_status_interval = datetime.timedelta(seconds=10)
        return self._update_status_interval

    @property
    def last_status_update(self):
        if not getattr(self, "_last_status_update", None):
            self._last_status_update = (
                self.execute_time or timezone.now() - self.update_status_interval
            )
        return self._last_status_update

    @property
    def cached_status(self):
        """
        The cached status of the job (i.e. the status from the last time it was updated).

        Returns: A string of the display name for the cached job status.

        """
        field = self._meta.get_field("_status")
        status = self._get_FIELD_display(field)
        if self._status == "OTH":
            status = self.extended_properties.get(self.OTHER_STATUS_KEY, status)
        return status

    @property
    def status(self):
        """
        The current status of the job. ``update_status`` is called to ensure status is current.

        Returns: A string of the display name for the current job status.

        It may be set as an attribute in which case ``update_status`` is called.
        """
        self.update_status()
        return self.cached_status

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
            return ""

        return run_time

    def execute(self, *args, **kwargs):
        """
        executes the job
        """
        try:
            self._execute(*args, **kwargs)
            self.execute_time = timezone.now()
            self._status = "SUB"
        except Exception:
            self._status = "ERR"
        self.save()

    def update_status(self, status=None, *args, **kwargs):
        """
        Updates the status of a job. If ``status`` is passed then it will manually update the status. Otherwise,
            it will determine if ``_update_status`` should be called.

        Args:
            status (str, optional): The value to manually set the status to. It may be either the display name or the
                three letter database code for defined statuses. If it is not one of the defined statuses, then the
                status will be set to ``OTH`` and the ``status`` value will be saved in ``extended_properties``
                using the ``OTHER_STATUS_KEY``.
            *args: positional arguments that are passed through to ``_update_status``.
            **kwargs: key-word arguments that are passed through to ``_update_status``.

        """
        old_status = self._status
        update_needed = old_status in self.NON_TERMINAL_STATUS_CODES or (
            old_status == "OTH"
            and self.extended_properties[self.OTHER_STATUS_KEY]
            in self.NON_TERMINAL_STATUSES
        )

        # Set status from status given
        if status:
            if status not in self.VALID_STATUSES:
                if status in self.DISPLAY_STATUSES:
                    status = self.REVERSE_STATUSES[status]
                else:
                    self.extended_properties[self.OTHER_STATUS_KEY] = status
                    status = "OTH"
            if status != "OTH":
                self.extended_properties.pop(self.OTHER_STATUS_KEY, None)
            self._status = status
            self.save()

        # Update status if status not given and still pending/running
        elif update_needed and self.is_time_to_update():
            self._update_status(*args, **kwargs)
            self._last_status_update = timezone.now()

        # Post-process status after update if old status was pending/running
        if update_needed:
            if self._status == "RUN" and (old_status in ("PEN", "SUB")):
                self.start_time = timezone.now()
            if self._status in ["COM", "VCP", "RES"]:
                self.process_results()
            elif self._status == "ERR" or self._status == "ABT":
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
            function_extractor = TethysFunctionExtractor(
                self._process_results_function, None
            )
            if function_extractor.valid:
                return function_extractor.function

    @process_results_function.setter
    def process_results_function(self, function):
        if isinstance(function, str):
            self._process_results_function = function
            return
        module_path = inspect.getmodule(function).__name__.split(".")
        module_path.append(function.__name__)
        self._process_results_function = ".".join(module_path)

    def process_results(self, *args, **kwargs):
        """
        Process the results.
        """
        log.debug("Started processing results for job: {}".format(self))
        self._process_results(*args, **kwargs)
        self.completion_time = timezone.now()
        self._status = "COM"
        self.save()
        log.debug("Finished processing results for job: {}".format(self))

    def resubmit(self, *args, **kwargs):
        self._resubmit(*args, **kwargs)

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
        """
        A method to be implemented by subclasses to retrieve the jobs current status and save it as ``self._status``.
        Args:
            *args:
            **kwargs:
        """
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

    async def safe_close(self):
        """
        Override to close any asynchronous connections before object destruction
        """
        pass
