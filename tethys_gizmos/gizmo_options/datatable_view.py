"""
********************************************************************************
* Name: table_view.py
* Author: Alan Snow
* Created On: November 2016
* License: BSD 2-Clause
********************************************************************************
"""
from .base import TethysGizmoOptions
import re
from json import dumps

__all__ = ['DataTableView']

class DataTableView(TethysGizmoOptions):
    """
    Table views can be used to display tabular data. The table view gizmo can be configured to have columns that are editable. When used in this capacity, embed the table view in a form with a submit button.

    Attributes
        rows(tuple or list, required): A list/tuple of lists/tuples representing each row in the table.
        column_names(tuple or list): A tuple or list of strings that represent the table columns names.
        attributes(Optional[dict]): A dictionary representing additional HTML attributes to add to the primary element (e.g. {"onclick": "run_me();"}).
        classes(Optional[str]): Additional classes to add to the primary HTML element (e.g. "example-class another-class").
        **kwargs(DataTable Options): See https://datatables.net/reference/option.

    Example

    ::

        # CONTROLLER
        from tethys_sdk.gizmos import DataTableView

        table_view = DataTableView(column_names=('Name', 'Age', 'Job'),
                                   rows=[('Bill', 30, 'contractor'),
                                         ('Fred', 18, 'programmer'),
                                         ('Bob', 26, 'boss')],
                                   searching=False,
                                   orderClasses=False,
                                   lengthMenu=[ [10, 25, 50, -1], [10, 25, 50, "All"] ],
                                   )

        # TEMPLATE

        {% gizmo datatable_view table_view %}

    """
    def __init__(self, rows, column_names, attributes={}, classes='', **kwargs):
        """
        Constructor
        """
        # Initialize super class
        super(DataTableView, self).__init__(attributes=attributes, classes=classes)

        self.rows = rows
        self.column_names = column_names
        self.datatable_options = {}        
        for key, value in kwargs.iteritems():
            data_name = re.sub("([a-z])([A-Z])","\g<1>-\g<2>",key).lower()
            self.datatable_options[data_name] = dumps(value)
