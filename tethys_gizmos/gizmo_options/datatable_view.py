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
    
    .. info:: The current version of DataTables in Tethys Platform is 1.10.12.

    Attributes:
        rows(tuple or list, required): A list/tuple of lists/tuples representing each row in the table.
        column_names(tuple or list): A tuple or list of strings that represent the table columns names.
        attributes(Optional[dict]): A dictionary representing additional HTML attributes to add to the primary element (e.g. {"onclick": "run_me();"}).
        classes(Optional[str]): Additional classes to add to the primary HTML element (e.g. "example-class another-class").
        **kwargs(DataTable Options): See https://datatables.net/reference/option.

    Regular Controller Example

    ::

        from tethys_sdk.gizmos import DataTableView

        datatable_default = DataTableView(column_names=('Name', 'Age', 'Job'),
                                          rows=[('Bill', 30, 'contractor'),
                                                ('Fred', 18, 'programmer'),
                                                ('Bob', 26, 'boss')],
                                          searching=False,
                                          orderClasses=False,
                                          lengthMenu=[ [10, 25, 50, -1], [10, 25, 50, "All"] ],
                                          )

        context = { 'datatable_view': datatable_default}

    Regular Template Example 

    ::
    
        {% load tethys_gizmos %}
        
        {% block register_gizmos %}
          {% register_gizmo_dependency datatable_view %}
        {% endblock %}

        {% gizmo datatable_view table_view %}
        
    .. note:: You can also add extensions to the data table view as shown in the next example.
              To learn more about DataTable extensions, go to https://datatables.net/extensions/index.

    ColReorder Controller Example

    ::

        from tethys_sdk.gizmos import DataTableView

        datatable_with_extension = DataTableView(column_names=('Name', 'Age', 'Job'),
                                                 rows=[('Bill', 30, 'contractor'),
                                                       ('Fred', 18, 'programmer'),
                                                       ('Bob', 26, 'boss')],
                                                 colReorder=True,
                                                 )
                                                 
        context = { 'datatable_with_extension': datatable_with_extension}

    ColReorder Template Example 

    ::

        {% load tethys_gizmos %}
        
        {% block register_gizmos %}
          {% register_gizmo_dependency datatable_view %}
        {% endblock %}
    
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
    
        {% gizmo datatable_view datatable_with_extension %}

    """
    ##UNSUPPORTED_EXTENSIONS = ('autoFill', 'select', 'keyTable', 'rowReorder')
    ##SUPPORTED_EXTENSIONS = ('buttons', 'colReorder', 'fizedColumns', 
    ##                        'fixedHeader', 'responsive',  'scroller')
    
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
