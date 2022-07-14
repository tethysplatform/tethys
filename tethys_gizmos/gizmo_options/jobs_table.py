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

from tethys_portal.dependencies import vendor_static_dependencies
from tethys_cli.cli_colors import write_warning
from tethys_compute.models import TethysJob
from .base import TethysGizmoOptions
from .select_input import SelectInput

log = logging.getLogger('tethys.tethys_gizmos.gizmo_options.jobs_table')

__all__ = ['JobsTable']


JobsTableRow = namedtuple('JobsTableRow', ['columns', 'actions'])


def add_static_method(cls):
    def outer(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
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
    def __init__(self, label, callback_or_url=None, enabled_callback=None, confirm_message=None,
                 show_overlay=False, modal_url=None, job_type=TethysJob):
        self.label = label
        self.confirm_message = confirm_message
        self.show_overlay = show_overlay
        self.modal_url = modal_url
        self.url = None
        self.callback = None

        if callback_or_url is None:
            pass
        elif modal_url is None and callback_or_url is None:
            raise ValueError('There is not a callback url or modal url.')
        else:
            if isinstance(callback_or_url, str) and (':' in callback_or_url or '/' in callback_or_url):
                self.url = callback_or_url
            else:
                self.callback = self.register_callback(callback_or_url, job_type)
        if enabled_callback:
            self.register_callback(enabled_callback, job_type, self.get_enabled_callback_name(label))

    @property
    def properties(self):
        return {
            'callback': self.callback,
            'url': self.url,
            'modal_url': self.modal_url,
            'confirm_message': self.confirm_message,
            'show_overlay': self.show_overlay,
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
        return f'custom_action_{label}_enabled'


DEFAULT_ACTIONS_ARGS = dict(
    run=['Run', 'execute', lambda job, job_status: job_status == 'Pending'],
    pause=['Pause', 'pause', lambda job, job_status: job_status in TethysJob.RUNNING_STATUSES],
    resume=['Resume', 'resume', lambda job, job_status: job_status == 'Paused'],
    resubmit=['Resubmit', 'resubmit', lambda job, job_status: job_status in TethysJob.TERMINAL_STATUSES, '', True],
    logs=['View Logs', None, lambda job, job_status: job_status not in TethysJob.PRE_RUNNING_STATUSES],
    monitor=['Monitor Job', None, lambda job, job_status: job_status in TethysJob.RUNNING_STATUSES],
    results=['View Results', None, lambda job, job_status: job_status in TethysJob.TERMINAL_STATUSES],
    terminate=['Terminate', 'stop', lambda job, job_status: job_status in TethysJob.ACTIVE_STATUSES,
               'Are you sure you want to terminate this job?', True],
    delete=['Delete', 'delete', lambda job, job_status: job_status not in TethysJob.ACTIVE_STATUSES,
            'Are you sure you want to permanently delete this job?', True],
)


class JobsTable(TethysGizmoOptions):
    """
    A jobs table can be used to display users' jobs. The JobsTable gizmo takes the same formatting options as the table view gizmo, but does not allow the columns to be edited. Additional attributes for the jobs table allows for a dynamically updating status field, and action buttons.

    Attributes:
        jobs(tuple or list, required): A list/tuple of TethysJob objects.
        column_fields(tuple or list, required): A tuple or list of strings that represent TethysJob object attributes to show in the columns.
        show_status(bool): Add a column to the table to show dynamically updating job status. Default is True.
        show_actions(bool): Add a column to the table to show a dynamically updating dropdown list of actions that can be done on the job. The available actions are determined by `actions` option. Actions are enabled/disabled based on the job status. If this is False then then `actions` option ignored.
        actions(list): A list of actions that can be done on a job. Available actions are ['run', 'resubmit', 'logs', 'terminate', 'delete']. If `monitor_url` and `results_url` are supplied then 'monitor' and 'results' respectively will be added. If None then all actions will be used. Default is None.
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

    Deprecated Attributes:
        status_actions(bool): Add a column to the table to show dynamically updating status, and action buttons. If this is false then the values for run_btn, delete_btn, monitor_url, and results_url will be ignored. Default is True.
        run_btn(bool): Add a button to run the job when job status is "Pending". Default is True.
        delete_btn(bool): Add a button to delete jobs. Default is True.
        show_resubmit_btn(bool): Add a button to resubmit jobs. Default is False.
        show_log_btn(bool): Add a button to see log for submitted job. Default is False.

    Controller Example

    ::

        from tethys_apps.sdk.gizmos import JobsTable

        jobs_table_options = JobsTable(
                                       jobs=jobs,
                                       column_fields=('id', 'name', 'description', 'creation_time', 'execute_time'),
                                       actions=['run', 'resubmit', 'logs', 'terminate', 'delete'],
                                       hover=True,
                                       striped=False,
                                       bordered=False,
                                       condensed=False,
                                       results_url='app_name:results_controller',
                                     )
        context = {
                    'jobs_table_options': jobs_table_options,
                  }

    Template Example

    ::

        {% load tethys_gizmos %}

        {% gizmo jobs_table_options %}

    """  # noqa: E501
    gizmo_name = "jobs_table"

    def __init__(self, jobs, column_fields, show_status=True, show_actions=True,
                 monitor_url='', results_url='', hover=False, striped=False, bordered=False, condensed=False,
                 attributes=None, classes='', refresh_interval=5000, delay_loading_status=True,
                 show_detailed_status=False, actions=None, enable_data_table=False, data_table_options=None):
        """
        Constructor
        """
        # Initialize super class
        super().__init__(attributes=attributes, classes=classes)

        self.jobs = jobs
        self.rows = None
        self.column_fields = None
        self.column_names = None

        self.show_status = show_status
        self.show_actions = show_actions
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
        self.data_table_options = data_table_options or {'ordering': True, 'searching': False, 'paging': False}

        actions = actions or ['run', 'resubmit', '|', 'logs', 'monitor', 'results', '|', 'terminate', 'delete']

        # TODO: this is backward compatibility code, remove at next major release
        if '|' not in actions:
            # revert to previous default order
            actions.extend(['monitor', 'results'])
            actions = set(actions)
            ordered_actions = list()
            prev_len = 0
            for action_group in [
                ['run', 'pause', 'resume', 'resubmit'],
                ['logs', 'monitor', 'results'],
                ['terminate', 'delete'],
            ]:
                for action in action_group:
                    if action in actions:
                        ordered_actions.append(action)
                        actions.remove(action)
                if len(ordered_actions) > prev_len:
                    ordered_actions.append('|')
                prev_len = len(ordered_actions)
            ordered_actions.extend(actions)
            actions = ordered_actions[:-1] if ordered_actions[-1] == '|' else ordered_actions
        # end compatibility code

        for action_name, url in (('monitor', monitor_url), ('results', results_url)):
            if url:
                args = DEFAULT_ACTIONS_ARGS[action_name]
                args[1] = url
                if action_name in actions:
                    actions[actions.index(action_name)] = args
                else:
                    actions.append(args)
            elif action_name in actions:
                actions.remove(action_name)

        self.actions = dict()

        for i, action in enumerate(actions):
            if action == '|':
                self.actions[f'_sep_{i}'] = {'sep': i}
                # the value dict (i.e. {'sep': i}) needs to have some value in it for the POST request to keep it
                continue
            if isinstance(action, str):
                try:
                    args = DEFAULT_ACTIONS_ARGS[action]
                    action = CustomJobAction(*args)
                except KeyError:
                    raise ValueError(f'The action "{action}" is not a valid default action.')
            if isinstance(action, tuple) or isinstance(action, list):
                action = CustomJobAction(*action)

            if isinstance(action, CustomJobAction):
                self.actions[action.label] = action.properties

        self.set_rows_and_columns(jobs, column_fields)

        # Compute column count
        self.num_cols = len(column_fields)

        if self.show_status:
            self.num_cols += 1

        if self.show_actions:
            self.num_cols += 1

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
                if field.startswith('extended_properties'):
                    column_name = field.split('.')[-1]
                column_name = column_name.title().replace('_', ' ')
            try:
                if not field.startswith('extended_properties'):
                    getattr(first_job, field)  # verify that the field name is a valid attribute on the job
                self.column_names.append(column_name)
                self.column_fields.append(field)
            except AttributeError:
                log.warning('Column %s was not added because the %s has no attribute %s.',
                            column_name, str(first_job), field)

        for job in sorted(jobs):
            row_values = self.get_row(
                job, self.column_fields, deepcopy(self.actions), delay_loading_status=self.delay_loading_status
            )
            self.rows.append(row_values)

    @staticmethod
    def get_row(job, job_attributes, actions=None, delay_loading_status=False):
        """Get the field values for one row (corresponding to one job).

        Args:
            job (TethysJob): An instance of a subclass of TethysJob
            job_attributes (list): a list of attribute names corresponding to the fields in the jobs table
            actions (dict): a dictionary of custom actions
            delay_loading_status (bool): whether to delay loading the status

        Returns:
            A list of field values for one row.

        """
        job_actions = actions or {}
        row_values = list()
        extended_properties = job.extended_properties
        for attribute in job_attributes:
            if attribute.startswith('extended_properties'):
                parts = attribute.split('.')
                keys = parts[1:-1]
                cur_dict = extended_properties
                for key in keys:
                    cur_dict = cur_dict.get(key, {})
                value = cur_dict.get(parts[-1], '')
            else:
                value = getattr(job, attribute)
                # Truncate fractional seconds
                if attribute == 'run_time':
                    value = str(value).split('.')[0]

            row_values.append(value)

        job_status = None if delay_loading_status else job.status

        for action, properties in job_actions.items():
            properties['enabled'] = getattr(
                job, CustomJobAction.get_enabled_callback_name(action), lambda js: True)(job_status)

        return JobsTableRow(row_values, actions=job_actions)

    @staticmethod
    def get_gizmo_css():
        return (
            'tethys_gizmos/css/jobs_table.css',
            *SelectInput.get_vendor_css(),
        )

    @staticmethod
    def get_vendor_js():
        return (
            vendor_static_dependencies['d3'].js_url,
            vendor_static_dependencies['lodash'].js_url,
            vendor_static_dependencies['graphlib'].js_url,
            vendor_static_dependencies['dagre'].js_url,
            vendor_static_dependencies['dagre-d3'].js_url,
            *SelectInput.get_vendor_js(),
        )

    @staticmethod
    def get_gizmo_js():
        """
        JavaScript specific to gizmo to be placed in the {% block scripts %} block
        """
        return (
            'tethys_gizmos/js/jobs_table.js',
        )

    @staticmethod
    def get_gizmo_modals():
        return (
            jobs_table_modals,
        )


# HTML code to be read
jobs_table_modals = '''
<!-- Jobs Table: Loading Overlay -->
<div id="jobs_table_overlay" class="d-none">
    <div class="cv-spinner" >
        <span class="spinner"></span>
    </div>
</div>

<!-- Jobs Table: Logs Modal -->
<div id="modal-dialog-jobs-table-show-log" title="Logs" class="modal" role="dialog">
  <div class="modal-dialog modal-lg" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="ModalJobLogTitle">Logs</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div id="modal-dialog-jobs-table-log-nav"></div>
      <div class="modal-body" id="modal-dialog-jobs-table-log-body">
        <div id="jobs_table_logs_overlay" class="d-none">
          <div class="cv-spinner" >
            <span class="spinner"></span>
          </div>
        </div>
        <div id="modal-dialog-jobs-table-log-content"></div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-default" data-bs-dismiss="modal">Close</button>
        <button type="button" class="btn btn-success" id="tethys_log_refresh_job_id" value="">Refresh</button>
      </div>
    </div>
  </div>
</div>

<!-- Jobs Table: Confirmation Modal -->
<div id="modal-dialog-jobs-table-confirm" title="Confirm" class="modal" role="dialog">
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="modal-job-confirm-title">Confirm Action</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body">
        <div id="modal-dialog-jobs-table-confirm-content"></div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-default" data-bs-dismiss="modal">Cancel</button>
        <button type="button" class="btn btn-danger" id="tethys_jobs-table-confirm" value="">Yes</button>
      </div>
    </div>
  </div>
</div>

<!-- Jobs Table: Custom Modal -->
<div id="modal-dialog-jobs-table-modal" title="Modal_option" class="modal" role="dialog">
  <div class="modal-dialog" role="document">
    <div class="modal-content" id="modal-dialog-jobs-table-modal-content">
    </div>
  </div>
</div>
'''
