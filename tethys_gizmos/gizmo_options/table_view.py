"""
********************************************************************************
* Name: table_view.py
* Author: Ezra Rice
* Created On: May 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
from .base import TethysGizmoOptions

__all__ = ['TableView']


class TableView(TethysGizmoOptions):
    """
    Table views can be used to display tabular data. The table view gizmo can be configured to have columns that are editable. When used in this capacity, embed the table view in a form with a submit button.

    Attributes:
        rows(tuple or list, required): A list/tuple of lists/tuples representing each row in the table.
        column_names(tuple or list): A tuple or list of strings that represent the table columns names.
        hover(bool): Illuminate rows on hover (does not work on striped tables)
        striped(bool): Stripe rows
        bordered(bool): Add borders and rounded corners
        condensed(bool): A more tightly packed table
        editable_columns(list or tuple): A list or tuple with an entry for each column in the table. The entry is either False for non-editable columns or a string that will be used to create identifiers for the input column_fields in that column.
        row_ids(list or tuple): A list or tuple of ids for each row in the table. These will be combined with the string in the editable_columns parameter to create unique identifiers for easy input field in the table. If not specified, each row will be assigned an integer value.
        attributes(dict): A dictionary representing additional HTML attributes to add to the primary element (e.g. {"onclick": "run_me();"}).
        classes(str): Additional classes to add to the primary HTML element (e.g. "example-class another-class").

    Controller Example

    ::

        from tethys_sdk.gizmos import TableView

        table_view = TableView(column_names=('Name', 'Age', 'Job'),
                               rows=[('Bill', 30, 'contractor'),
                                     ('Fred', 18, 'programmer'),
                                     ('Bob', 26, 'boss')],
                               hover=True,
                               striped=False,
                               bordered=False,
                               condensed=False)

        table_view_edit = TableView(column_names=('Name', 'Age', 'Job'),
                                    rows=[('Bill', 30, 'contractor'),
                                          ('Fred', 18, 'programmer'),
                                          ('Bob', 26, 'boss')],
                                    hover=True,
                                    striped=True,
                                    bordered=False,
                                    condensed=False,
                                    editable_columns=(False, 'ageInput', 'jobInput'),
                                    row_ids=[21, 25, 31])

        context = {
                    'table_view': table_view,
                    'table_view_edit': table_view_edit,
                  }

    Template Example

    ::

        {% load tethys_gizmos %}

        {% gizmo table_view %}
        {% gizmo table_view_edit %}

    """  # noqa: E501
    gizmo_name = "table_view"

    def __init__(self, rows, column_names='', hover=False, striped=False, bordered=False, condensed=False,
                 editable_columns='', row_ids='', attributes={}, classes=''):
        """
        Constructor
        """
        # Initialize super class
        super().__init__(attributes=attributes, classes=classes)

        self.rows = rows
        self.column_names = column_names
        self.hover = hover
        self.striped = striped
        self.bordered = bordered
        self.condensed = condensed
        self.editable_columns = editable_columns
        self.row_ids = row_ids
