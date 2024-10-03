# coding=utf-8
"""
********************************************************************************
* Name: jobs_table.py
* Author: Scott Christensen
* Created On: August 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
from collections import namedtuple
import logging
from functools import wraps
from copy import deepcopy
from pathlib import Path

from django.urls import reverse

from tethys_portal.dependencies import vendor_static_dependencies
from .base import TethysGizmoOptions
from .select_input import SelectInput

log = logging.getLogger("tethys.tethys_gizmos.gizmo_options.jobs_table")

__all__ = ["JobsTable", "CustomJobAction"]


JobsTableRow = namedtuple("JobsTableRow", ["columns", "job_status", "actions"])


def add_static_method(cls):
    def outer(func):
        @wraps(func)
        def wrapper(_, *args, **kwargs):
            return func(*args, **kwargs)

        setattr(cls, func.__name__, wrapper)
        return func

    return outer


def add_method(cls):
    def outer(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(cls, func.__name__, wrapper)
        return func

    return outer


class CustomJobAction:
    """
    A ``CustomJobAction`` is used to create custom actions in the actions dropdown menu of the jobs table.

    Attributes:
        label (str, required): The display name of the action that will show in the actions dropdown.
        callback_or_url (str or callable, required if ``modal_url`` is not supplied): The name of a callable attribute
            on the ``job_type`` object or a callable that accepts a ``TethysJob`` as an argument (may be asynchronous).
            Or it can be the name of a URL that the custom action option will link to.
        enabled_callback (callable): A callable that accepts a ``job_type`` object as an argument and returns True
            if the action should be enabled or False if it should be disabled.
        confirmation_message (str): A message to display in a modal to ask for confirmation to perform the action.
        show_overlay (bool): Whether to show an overlay with a loading spinner while the action is being called.
        modal_url (str, required if ``callback_or_url`` is not supplied): The name of a URL to retrieve content to
            populate a modal.
        job_type (class): A subclass of ``TethysJob``. Must be specified if the ``callback_or_url`` argument is an
            attribute that is only defined at the subclass level.

    Examples:

    ::

        def custom_action(job):
            # do something with job

        def custom_action2(job):
            # do something with job

        def enable_custom_action(job):
            # custom logic to determine if action should be enabled

        CustomJobAction(
            label='Custom Action',
            callback_or_url=custom_action,
            enabled_callback=enable_custom_action,
            confirmation_message='Do you really want to do this?',
            show_overlay=True,  # displays the overlay loading spinner until the custom action function returns
        )

    .. tip::

        For a complete example of using ``CustomJobAction`` refer to the `Gizmo Showcase Tethys app code.
        <https://github.com/tethysplatform/tethysapp-gizmo_showcase/blob/main/tethysapp/gizmo_showcase/controllers/processing.py>`_

    """  # noqa: E501

    def __init__(
        self,
        label,
        callback_or_url=None,
        enabled_callback=None,
        confirmation_message=None,
        show_overlay=False,
        modal_url=None,
        job_type=None,
    ):
        from tethys_compute.models import TethysJob

        job_type = job_type or TethysJob
        self.label = label
        self.confirmation_message = confirmation_message
        self.show_overlay = show_overlay
        self.modal_url = modal_url
        self.url = None
        self.callback = None

        if callback_or_url is None:
            if not modal_url:
                raise ValueError(
                    f'A {self.__class__.__name__} requires either the "callback_or_url" argument '
                    f'or the "modal_url" argument.'
                )
        else:
            if isinstance(callback_or_url, str) and (
                ":" in callback_or_url or "/" in callback_or_url
            ):
                self.url = callback_or_url
            else:
                self.callback = self.register_callback(callback_or_url, job_type)
        if enabled_callback:
            self.register_callback(
                enabled_callback, job_type, self.get_enabled_callback_name(label)
            )

    @property
    def properties(self):
        return {
            "callback": self.callback,
            "url": self.url,
            "modal_url": self.modal_url,
            "confirmation_message": self.confirmation_message,
            "show_overlay": self.show_overlay,
        }

    @staticmethod
    def register_callback(callback, job_type, name=None):
        if isinstance(callback, str):
            getattr(job_type, callback)
            return callback
        elif callable(callback):
            name = name or callback.__name__
            setattr(job_type, name, callback)
            return name
        else:
            raise ValueError(f'The specified callback "{callback}" is not valid.')

    @staticmethod
    def get_enabled_callback_name(label):
        return f"custom_action_{label}_enabled"


class JobsTable(TethysGizmoOptions):
    """
    A jobs table can be used to display users' jobs. The JobsTable gizmo takes the same formatting options as the table view gizmo, but does not allow the columns to be edited. Additional attributes for the jobs table allows for a dynamically updating status field, and action buttons.

    Attributes:
        jobs(tuple or list, required): A list/tuple of TethysJob objects.
        column_fields(tuple or list, required): A tuple or list of strings that represent TethysJob object attributes to show in the columns.
        show_status(bool): Add a column to the table to show dynamically updating job status. Default is True.
        show_actions(bool): Add a column to the table to show a dynamically updating dropdown list of actions that can be done on the job. The available actions are determined by `actions` option. Actions are enabled/disabled based on the job status. If this is False then then `actions` option ignored.
        actions(list): A list of default actions or custom action arguments that can be done on a job with the `|` character used to divide the actions into sections. If None then all the default actions will be used (i.e. `['run', 'resubmit', '|', 'logs', 'monitor', 'results', '|', 'terminate', 'delete']`). Note that if `monitor_url` and `results_url` are supplied then 'monitor' and 'results' respectively will be added if not already in the list. If they are not provided then `monitor` and `results` will be removed from the list if present. Default is None.
        monitor_url(str):  A string representing the namespaced path to a controller to that displays monitoring information about a running job (e.g. app_name:monitoring_controller)
        results_url(str): A string representing the namespaced path to a controller to that displays job results (e.g. app_name:results_controller)
        hover(bool): Illuminate rows on hover (does not work on striped tables)
        striped(bool): Stripe rows
        bordered(bool): Add borders and rounded corners
        condensed(bool): A more tightly packed table
        attributes(dict): A dictionary representing additional HTML attributes to add to the primary element (e.g. {"onclick": "run_me();"}).
        classes(str): Additional classes to add to the primary HTML element (e.g. "example-class another-class").
        refresh_interval(int): The refresh interval for the runtime and status fields in milliseconds. Default is 5000.
        show_detailed_status(bool): Show status of each node in CondorWorkflow jobs when True. Defaults to False.
        sort(bool|callable): Whether to sort the list of jobs in the table. If True, jobs are sorted by creation time from oldest (top of the table) to newest. If a callable is passed then it is used as the key to sort the jobs. Default is True.
        reverse_sort(bool): Whether to reverse the sorting order. If ``sort`` is False then this argument has no effect. Default is False.

    Controller Example

    ::

        from tethys_sdk.gizmos import JobsTable

        jobs_table_options = JobsTable(
            jobs=jobs,
            column_fields=('id', 'name', 'description', 'creation_time', 'execute_time'),
            actions=['run', 'resubmit', '|', 'logs', '|', 'terminate', 'delete'],
            hover=True,
            striped=False,
            bordered=False,
            condensed=False,
            results_url='app_name:results_controller',
        )
        context = {
            'jobs_table_options': jobs_table_options,
        }

    Controller Example with Custom Actions

    ::

        from tethys_sdk.gizmos import JobsTable, CustomJobAction

        def custom_action(job):
            # do something with job

        def custom_action2(job):
            # do something with job

        def enable_custom_action(job):
            # custom logic to determine if action should be enabled

        def controller(request):
            ...

            jobs_table_options = JobsTable(
                jobs=jobs,
                column_fields=('id', 'name', 'description', 'creation_time', 'execute_time'),
                actions=[
                    'run', 'resubmit', '|',
                    'logs', '|',
                    'terminate', 'delete', '|',
                    CustomJobAction(
                        label='Custom Action',
                        callback_or_url=custom_action,
                        enabled_callback=enable_custom_action,
                        confirmation_message='Do you really want to do this?',
                        show_overlay=True,  # displays the overlay loading spinner until the custom action function returns
                    ),
                    # Custom actions can also be defined as a list/tuple of args. The only required arguments are label and callback_or_url
                    ('Another Custom Action', custom_action2),
                    # Instead of a function a custom action can just be a url name for a custom endpoint
                    ('Yet Another Custom Action', 'my_app:custom_endpoint'),
                    # An alternative type of custom action is to provide an endpoint to get content for a modal
                    CustomJobAction('Custom Modal Content', modal_url='my_app:get_modal_content'),
                ],
                hover=True,
                striped=False,
                bordered=False,
                condensed=False,
                results_url='app_name:results_controller',
            )
            context = {
                'jobs_table_options': jobs_table_options,
            }
            ...


    Template Example

    ::

        {% load tethys_gizmos %}

        {% gizmo jobs_table_options %}

    .. tip::

        To see the Jobs Table Gizmo in action, install the `Gizmo Showcase Tethys app.
        <https://github.com/tethysplatform/tethysapp-gizmo_showcase>`_

    """  # noqa: E501

    gizmo_name = "jobs_table"

    def __init__(
        self,
        jobs,
        column_fields,
        show_status=True,
        show_actions=True,
        monitor_url="",
        results_url="",
        hover=False,
        striped=False,
        bordered=False,
        condensed=False,
        attributes=None,
        classes="",
        refresh_interval=5000,
        delay_loading_status=True,
        show_detailed_status=False,
        actions=None,
        enable_data_table=False,
        data_table_options=None,
        sort=True,
        reverse_sort=False,
    ):
        """
        Constructor
        """
        from tethys_compute.models import TethysJob

        # Initialize super class
        super().__init__(attributes=attributes, classes=classes)

        self.jobs = list(jobs)
        if sort:
            key = sort if callable(sort) else lambda j: j.creation_time
            self.jobs.sort(key=key, reverse=reverse_sort)
        self.rows = None
        self.column_fields = None
        self.column_names = None

        self.show_status = show_status
        self.show_actions = show_actions
        self.active_statuses = TethysJob.ACTIVE_STATUSES
        self.hover = hover
        self.striped = striped
        self.bordered = bordered
        self.condensed = condensed
        self.attributes = attributes or {}
        self.classes = classes
        self.refresh_interval = refresh_interval
        self.delay_loading_status = delay_loading_status
        self.show_detailed_status = show_detailed_status
        self.enable_data_table = enable_data_table
        self.data_table_options = data_table_options or {
            "ordering": True,
            "searching": False,
            "paging": False,
        }

        actions = actions or [
            "run",
            "resubmit",
            "|",
            "logs",
            "monitor",
            "results",
            "|",
            "terminate",
            "delete",
        ]

        default_actions_args = dict(
            run=dict(
                label="Run",
                callback_or_url="execute",
                enabled_callback=lambda job, job_status: job_status == "Pending",
            ),
            pause=dict(
                label="Pause",
                callback_or_url="pause",
                enabled_callback=lambda job, job_status: job_status
                in TethysJob.RUNNING_STATUSES,
            ),
            resume=dict(
                label="Resume",
                callback_or_url="resume",
                enabled_callback=lambda job, job_status: job_status == "Paused",
            ),
            resubmit=dict(
                label="Resubmit",
                callback_or_url="resubmit",
                enabled_callback=lambda job, job_status: job_status
                in TethysJob.TERMINAL_STATUSES,
                show_overlay=True,
            ),
            logs=dict(
                label="View Logs",
                enabled_callback=lambda job, job_status: job_status
                not in TethysJob.PRE_RUNNING_STATUSES,
                modal_url="logs",  # Note: this is just a placeholder and is not actually used
            ),
            monitor=dict(
                label="Monitor Job",
                enabled_callback=lambda job, job_status: job_status
                in TethysJob.RUNNING_STATUSES,
            ),
            results=dict(
                label="View Results",
                enabled_callback=lambda job, job_status: job_status
                in TethysJob.TERMINAL_STATUSES,
            ),
            terminate=dict(
                label="Terminate",
                callback_or_url="stop",
                enabled_callback=lambda job, job_status: job_status
                in self.active_statuses,
                confirmation_message="Are you sure you want to terminate this job?",
                show_overlay=True,
            ),
            delete=dict(
                label="Delete",
                callback_or_url="delete",
                enabled_callback=lambda job, job_status: job_status
                not in self.active_statuses,
                confirmation_message="Are you sure you want to permanently delete this job?",
                show_overlay=True,
            ),
        )

        for action_name, url in (("monitor", monitor_url), ("results", results_url)):
            if url:
                kwargs = default_actions_args[action_name]
                kwargs["callback_or_url"] = url
                if action_name in actions:
                    actions[actions.index(action_name)] = kwargs
                else:
                    actions.append(kwargs)
            elif action_name in actions:
                actions.remove(action_name)

        self.actions = dict()

        for i, action in enumerate(actions):
            if action == "|":
                self.actions[f"_sep_{i}"] = {"sep": i}
                # the value dict (i.e. {'sep': i}) needs to have some value in it for the POST request to keep it
                continue
            if isinstance(action, str):
                try:
                    kwargs = default_actions_args[action]
                    action = CustomJobAction(**kwargs)
                except KeyError:
                    raise ValueError(
                        f'The action "{action}" is not a valid default action.'
                    )
            elif isinstance(action, tuple) or isinstance(action, list):
                action = CustomJobAction(*action)
            elif isinstance(action, dict):
                action = CustomJobAction(**action)

            if isinstance(action, CustomJobAction):
                self.actions[action.label] = action.properties

        self.set_rows_and_columns(self.jobs, column_fields)

        # Compute column count
        self.num_cols = len(column_fields)

        if self.show_status:
            self.num_cols += 1

        if self.show_actions:
            self.num_cols += 1

        # Derive base_ajax_url dynamically for use in JavaScript
        # e.g.: /developer/gizmos/ajax/9999/action/delete
        self.base_ajax_url = reverse("gizmos:delete_job", kwargs={"job_id": 9999})
        self.base_ajax_url = self.base_ajax_url.replace("9999/action/delete", "")

    def set_rows_and_columns(self, jobs, column_fields):
        self.rows = list()
        self.column_fields = list()
        self.column_names = list()

        if len(jobs) == 0:
            return

        first_job = jobs[0]
        for field in column_fields:
            if isinstance(field, tuple):
                column_name, field = field
            else:
                column_name = field
                if field.startswith("extended_properties"):
                    column_name = field.split(".")[-1]
                column_name = column_name.title().replace("_", " ")
            try:
                if not field.startswith("extended_properties"):
                    getattr(
                        first_job, field
                    )  # verify that the field name is a valid attribute on the job
                self.column_names.append(column_name)
                self.column_fields.append(field)
            except AttributeError:
                log.warning(
                    "Column %s was not added because the %s has no attribute %s.",
                    column_name,
                    str(first_job),
                    field,
                )

        for job in jobs:
            row_values = self.get_row(
                job,
                self.column_fields,
                deepcopy(self.actions),
                delay_loading_status=self.delay_loading_status,
            )
            self.rows.append(row_values)

    @staticmethod
    def get_row(job, job_attributes, actions=None, delay_loading_status=False):
        """Get the field values for one row (corresponding to one job).

        Args:
            job (TethysJob): An instance of a subclass of TethysJob
            job_attributes (list): a list of attribute names corresponding to the fields in the jobs table
            actions (dict): a dictionary of custom actions
            delay_loading_status (bool): whether to delay loading the status.
                Note that ``cached_status`` will be used and only non-terminal statuses will be updated on load.

        Returns:
            A list of field values for one row.

        """
        from tethys_compute.models import TethysJob

        job_actions = actions or {}
        row_values = list()
        extended_properties = job.extended_properties
        for attribute in job_attributes:
            if attribute.startswith("extended_properties"):
                parts = attribute.split(".")
                keys = parts[1:-1]
                cur_dict = extended_properties
                for key in keys:
                    cur_dict = cur_dict.get(key, {})
                value = cur_dict.get(parts[-1], "")
            else:
                value = getattr(job, attribute)
                # Truncate fractional seconds
                if attribute == "run_time":
                    value = str(value).split(".")[0]

            row_values.append(value)

        job_status = job.cached_status
        if job_status not in TethysJob.TERMINAL_STATUSES:
            job_status = None if delay_loading_status else job.status

        for action, properties in job_actions.items():
            properties["enabled"] = getattr(
                job, CustomJobAction.get_enabled_callback_name(action), lambda js: True
            )(
                job.cached_status
            )  # use cached status in case job_status is None

        return JobsTableRow(row_values, job_status=job_status, actions=job_actions)

    @staticmethod
    def get_gizmo_css():
        return (
            "tethys_gizmos/css/jobs_table.css",
            *SelectInput.get_vendor_css(),
        )

    @staticmethod
    def get_vendor_js():
        return (
            vendor_static_dependencies["d3"].js_url,
            vendor_static_dependencies["lodash"].js_url,
            vendor_static_dependencies["graphlib"].js_url,
            vendor_static_dependencies["dagre"].js_url,
            vendor_static_dependencies["dagre-d3"].js_url,
            *SelectInput.get_vendor_js(),
        )

    @staticmethod
    def get_gizmo_js():
        """
        JavaScript specific to gizmo to be placed in the {% block scripts %} block
        """
        return ("tethys_gizmos/js/jobs_table.js",)

    @staticmethod
    def get_gizmo_modals():
        modals_file = (
            Path(__file__).parents[1]
            / "templates"
            / "tethys_gizmos"
            / "gizmos"
            / "jobs_table_modals.html"
        )
        with modals_file.open() as f:
            modals = f.read()
        return (modals,)
