"""
********************************************************************************
* Name: table_view.py
* Author: Alan Snow
* Created On: November 2016
* License: BSD 2-Clause
********************************************************************************
"""

import re
from json import dumps
from tethys_portal.dependencies import vendor_static_dependencies
from .base import TethysGizmoOptions

__all__ = ["DataTableView"]


class DataTableView(TethysGizmoOptions):
    """
    Table views can be used to display tabular data. The table view gizmo can be configured to have columns that are
    editable. When used in this capacity, embed the table view in a form with a submit button.

    .. note:: The default version of DataTables in Tethys Platform is 1.11.3.

    Attributes:
        rows(tuple or list, required): A list/tuple of lists/tuples representing each row in the table.
        column_names(tuple or list): A tuple or list of strings that represent the table columns names.
        footer(Optional[bool]):If True, it will add the column names to the bottom of the table.
        hover(bool): Illuminate rows on hover (does not work on striped tables)
        striped(bool): Stripe rows
        bordered(bool): Add borders and rounded corners
        condensed(bool): A more tightly packed table
        dark(bool): Style table with dark variant
        attributes(Optional[dict]): A dictionary representing additional HTML attributes to add to the primary element (e.g. {"onclick": "run_me();"}).
        classes(Optional[str]): Additional classes to add to the primary HTML element (e.g. "example-class another-class").
        **kwargs(DataTable Options): See https://datatables.net/reference/option.

    Regular Controller Example

    ::

        from tethys_sdk.gizmos import DataTableView

        datatable_default = DataTableView(
            column_names=('Name', 'Age', 'Job'),
            rows=[('Bill', 30, 'contractor'),
                ('Fred', 18, 'programmer'),
                ('Bob', 26, 'boss')],
            searching=False,
            orderClasses=False,
            lengthMenu=[ [10, 25, 50, -1], [10, 25, 50, "All"] ],
        )

        context = {
            'datatable_view': datatable_default
        }

    Regular Template Example

    ::

        {% load tethys_gizmos %}

        {% gizmo datatable_view %}

    .. note:: You can also add extensions to the data table view as shown in the next example.
              To learn more about DataTable extensions, go to https://datatables.net/extensions/index.

    ColReorder Controller Example

    ::

        from tethys_sdk.gizmos import DataTableView

        datatable_with_extension = DataTableView(
            column_names=('Name', 'Age', 'Job'),
            rows=[('Bill', 30, 'contractor'),
                ('Fred', 18, 'programmer'),
                ('Bob', 26, 'boss')],
            colReorder=True,
        )

        context = {
            'datatable_with_extension': datatable_with_extension
        }

    ColReorder Template Example

    ::

        {% load tethys_gizmos %}

        #LOAD IN EXTENSION JAVASCRIPT/CSS
        {% block global_scripts %}
          {{ block.super }}
           <script type="text/javascript" language="javascript" src="https://cdn.datatables.net/colreorder/1.3.2/js/dataTables.colReorder.min.js"></script>
        {% endblock %}

        {% block styles %}
          {{ block.super }}
          <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/colreorder/1.3.2/css/colReorder.dataTables.min.css">
        {% endblock %}
        #END LOAD IN EXTENSION JAVASCRIPT/CSS

        {% gizmo datatable_with_extension %}

    """  # noqa: E501

    # UNSUPPORTED_EXTENSIONS = ('autoFill', 'select', 'keyTable', 'rowReorder')
    # SUPPORTED_EXTENSIONS = ('buttons', 'colReorder', 'fixedColumns',
    #                         'fixedHeader', 'responsive',  'scroller')
    gizmo_name = "datatable_view"
    version = vendor_static_dependencies["datatables"].version

    def __init__(
        self,
        rows,
        column_names,
        footer=False,
        hover=False,
        striped=False,
        bordered=False,
        condensed=False,
        dark=False,
        attributes=None,
        classes="",
        **kwargs,
    ):
        """
        Constructor
        """
        # Initialize super class
        super().__init__(attributes=attributes, classes=classes)

        self.rows = rows
        self.column_names = column_names
        self.footer = footer
        self.hover = hover
        self.striped = striped
        self.bordered = bordered
        self.condensed = condensed
        self.dark = dark
        self.datatable_options = {}
        for key, value in kwargs.items():
            data_name = re.sub(r"([a-z])([A-Z])", r"\g<1>-\g<2>", key).lower()
            self.datatable_options[data_name] = dumps(value)

    @classmethod
    def get_vendor_css(cls):
        """
        JavaScript vendor libraries to be placed in the
        {% block global_scripts %} block
        """
        return (vendor_static_dependencies["datatables_bs5"].css_url,)

    @classmethod
    def get_vendor_js(cls):
        """
        JavaScript vendor libraries to be placed in the
        {% block global_scripts %} block
        """
        return (
            vendor_static_dependencies["datatables"].js_url,
            vendor_static_dependencies["datatables_bs5"].js_url,
        )

    @staticmethod
    def get_gizmo_js():
        """
        JavaScript specific to gizmo to be placed in the
        {% block scripts %} block
        """
        return ("tethys_gizmos/js/datatable_view.js",)
