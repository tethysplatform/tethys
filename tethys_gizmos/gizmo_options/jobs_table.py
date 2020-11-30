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

from tethys_cli.cli_colors import write_warning
from .base import TethysGizmoOptions
from .select_input import SelectInput

log = logging.getLogger('tethys.tethys_gizmos.gizmo_options.jobs_table')

__all__ = ['JobsTable']


JobsTableRow = namedtuple('JobsTableRow', ['columns', 'actions'])


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
                 show_detailed_status=False, actions=None, enable_data_table=False, data_table_options=None,
                 # Deprecated options:
                 status_actions=None, show_resubmit_btn=None, run_btn=None, delete_btn=None, show_log_btn=None):
        """
        Constructor
        """
        # Initialize super class
        super().__init__(attributes=attributes, classes=classes)

        self.jobs = jobs
        self.rows = None
        self.column_fields = None
        self.column_names = None
        self.set_rows_and_columns(jobs, column_fields)

        self.show_status = show_status
        self.show_actions = show_actions
        self.monitor_url = monitor_url
        self.results_url = results_url
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

        actions = actions or ['run', 'resubmit', 'logs', 'terminate', 'delete']
        if monitor_url:
            actions.append('monitor')
        if results_url:
            actions.append('results')

        # code for backwards compatibility. Remove in Tethys v3.3
        if status_actions is not None:
            # deprecation warning
            write_warning('Deprecation Warning: The "status_actions" option in JobsTable will be removed in '
                          'the next release of Tethys. Please use "show_status" and "show_actions" instead.')
            self.show_actions = status_actions
        lcl = locals()
        for option, action in (('run_btn', 'run'), ('delete_btn', 'delete'), ('show_resubmit_btn', 'resubmit'),
                               ('show_log_btn', 'logs')):
            option_val = lcl[option]
            if option_val is not None:
                # deprecation warning
                write_warning(f'Deprecation Warning: The "{option}" option in JobsTable will be removed in the '
                              f'next release of Tethys. Please use the "show_actions" and "actions" options instead.')
                if option_val:
                    actions.append(action)
                else:
                    try:
                        actions.remove(action)
                    except ValueError:
                        pass
        # end compatibility code

        self.actions = dict(
            run='run' in actions,
            resubmit='resubmit' in actions,
            logs='logs' in actions,
            monitor='monitor' in actions and monitor_url,
            results='results' in actions and monitor_url,
            terminate='terminate' in actions,
            delete='delete' in actions,
        )

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
                column_name = field.title().replace('_', ' ')
            try:
                getattr(first_job, field)  # verify that the field name is a valid attribute on the job
                self.column_names.append(column_name)
                self.column_fields.append(field)
            except AttributeError:
                log.warning('Column %s was not added because the %s has no attribute %s.',
                            column_name, str(first_job), field)

        for job in sorted(jobs):
            row_values = self.get_row(job, self.column_fields)
            self.rows.append(row_values)

    @staticmethod
    def get_row(job, job_attributes):
        """Get the field values for one row (corresponding to one job).

        Args:
            job (TethysJob): An instance of a subclass of TethysJob
            job_attributes (list): a list of attribute names corresponding to the fields in the jobs table

        Returns:
            A list of field values for one row.

        """
        from tethys_compute.models import TethysJob
        row_values = list()
        job_actions = dict()
        for attribute in job_attributes:
            value = getattr(job, attribute)
            # Truncate fractional seconds
            if attribute == 'run_time':
                value = str(value).split('.')[0]
            if attribute.startswith('extended_properties'):
                extended_properties = job.extended_properties
                attribute = attribute.split('.')[-1]
                value = extended_properties.get(attribute, '')
            row_values.append(value)

            job_status = job.status
            job_actions = dict(
                run=job_status == 'Pending',
                resubmit=job_status in TethysJob.TERMINAL_STATUSES,
                monitor=job_status in TethysJob.RUNNING_STATUSES,
                results=job_status in TethysJob.TERMINAL_STATUSES,
                logs=job_status not in TethysJob.PRE_RUNNING_STATUSES,
                terminate=job_status in TethysJob.ACTIVE_STATUSES,
                delete=job_status not in TethysJob.ACTIVE_STATUSES,
            )

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
            'https://cdnjs.cloudflare.com/ajax/libs/d3/4.12.2/d3.min.js',
            'tethys_gizmos/vendor/lodash/lodash.min.js',
            'tethys_gizmos/vendor/graphlib/dist/graphlib.core.min.js',
            'tethys_gizmos/vendor/dagre/dist/dagre.core.min.js',
            'tethys_gizmos/vendor/dagre-d3/dist/dagre-d3.core.min.js',
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
