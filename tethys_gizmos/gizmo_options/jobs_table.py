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
from .base import TethysGizmoOptions
import logging
log = logging.getLogger('tethys.tethys_gizmos.gizmo_options.jobs_table')

__all__ = ['JobsTable']


class JobsTable(TethysGizmoOptions):
    """
    A jobs table can be used to display users' jobs. The JobsTable gizmo takes the same formatting options as the table view gizmo, but does not allow the columns to be edited. Additional attributes for the jobs table allows for a dynamically updating status field, and action buttons.

    Attributes:
        jobs(tuple or list, required): A list/tuple of TethysJob objects.
        column_fields(tuple or list, required): A tuple or list of strings that represent TethysJob object attributes to show in the columns.
        status_actions(bool): Add a column to the table to show dynamically updating status, and action buttons. If this is false then the values for run_btn, delete_btn, and results_url will be ignored. Default is True.
        run_btn(bool): Add a button to run the job when job status is "Pending". Default is True.
        delete_btn(bool): Add a button to delete jobs. Default is True.
        results_url(str): A string representing the namespaced path to a controller to that displays job results (e.g. app_name:results_controller)
        hover(bool): Illuminate rows on hover (does not work on striped tables)
        striped(bool): Stripe rows
        bordered(bool): Add borders and rounded corners
        condensed(bool): A more tightly packed table
        attributes(dict): A dictionary representing additional HTML attributes to add to the primary element (e.g. {"onclick": "run_me();"}).
        classes(str): Additional classes to add to the primary HTML element (e.g. "example-class another-class").
        refresh_interval(int): The refresh interval for the runtime and status fields in milliseconds. Default is 5000.

    Controller Example

    ::

        from tethys_apps.sdk.gizmos import JobsTable

        jobs_table_options = JobsTable(
                                       jobs=jobs,
                                       column_fields=('id', 'name', 'description', 'creation_time', 'execute_time'),
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

    def __init__(self, jobs, column_fields, status_actions=True, run_btn=True, delete_btn=True, results_url='',
                 hover=False, striped=False, bordered=False, condensed=False, attributes={}, classes='',
                 refresh_interval=5000, delay_loading_status=True):
        """
        Constructor
        """
        # Initialize super class
        super(JobsTable, self).__init__(attributes=attributes, classes=classes)

        self.jobs = jobs
        self.rows = None
        self.column_fields = None
        self.column_names = None
        self.set_rows_and_columns(jobs, column_fields)

        self.status_actions = status_actions
        self.run = run_btn
        self.delete = delete_btn
        self.results_url = results_url
        self.hover = hover
        self.striped = striped
        self.bordered = bordered
        self.condensed = condensed
        self.attributes = attributes
        self.classes = classes
        self.refresh_interval = refresh_interval
        self.delay_loading_status = delay_loading_status

    def set_rows_and_columns(self, jobs, column_fields):
        self.rows = list()
        self.column_fields = list()
        self.column_names = list()

        if len(jobs) == 0:
            return

        first_job = jobs[0]
        for field in column_fields:
            column_name = field.title().replace('_', ' ')
            try:
                getattr(first_job, field)  # verify that the field name is a valid attribute on the job
                self.column_names.append(column_name)
                self.column_fields.append(field)
            except AttributeError:
                log.warning('Column %s was not added because the %s has no attribute %s.',
                            column_name, str(first_job), field)

        for job in jobs:
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
        row_values = list()
        for attribute in job_attributes:
            value = getattr(job, attribute)
            # Truncate fractional seconds
            if attribute == 'run_time':
                # times = []
                # total_seconds = value.seconds
                # times.append(('days', run_time.days))
                # times.append(('hr', total_seconds/3600))
                # times.append(('min', (total_seconds%3600)/60))
                # times.append(('sec', total_seconds%60))
                # run_time_str = ''
                # for time_str, time in times:
                #     if time:
                #         run_time_str += "%s %s " % (time, time_str)
                # if not run_time_str or (run_time.days == 0 and total_seconds < 2):
                #     run_time_str = '%.2f sec' % (total_seconds + float(run_time.microseconds)/1000000,)
                value = str(value).split('.')[0]
            row_values.append(value)

        return row_values

    @staticmethod
    def get_gizmo_js():
        """
        JavaScript specific to gizmo to be placed in the {% block scripts %} block
        """
        return ('tethys_gizmos/js/jobs_table.js',)
