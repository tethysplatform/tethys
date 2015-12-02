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

__all__ = ['JobsTable']


class JobsTable(TethysGizmoOptions):
    """
    A jobs table can be used to display users' jobs. The JobsTable gizmo takes the same formatting options as the table view gizmo, but does not allow the columns to be edited. Additional attributes for the jobs table allows for a dynamically updating status field, and action buttons.

    Attributes
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

    Example

    ::

        # CONTROLLER
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

        # TEMPLATE

        {% gizmo jobs_table jobs_table_options %}

    """

    def __init__(self, jobs, column_fields, status_actions=True, run_btn=True, delete_btn=True, results_url='',
                 hover=False, striped=False, bordered=False, condensed=False, attributes={}, classes=''):
        """
        Constructor
        """
        # Initialize super class
        super(JobsTable, self).__init__(attributes=attributes, classes=classes)


        self.jobs = jobs
        self.rows = self.get_rows(column_fields)
        self.column_fields = column_fields
        self.column_names = [col_name.title().replace('_', ' ') for col_name in column_fields]
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

    def get_rows(self, column_fields):
        rows = []
        if self.jobs:
            attributes = self.jobs[0].__dict__.keys()
        for job in self.jobs:
            row_values = []
            for attribute in column_fields:
                if attribute in attributes:
                    row_values.append(job.__getattribute__(attribute))
            rows.append(row_values)
        return rows

