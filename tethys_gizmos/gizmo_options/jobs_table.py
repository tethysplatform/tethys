from .base import TethysGizmoOptions

__all__ = ['JobsTable']


class JobsTable(TethysGizmoOptions):
    """
    Table views can be used to display tabular data. The table view gizmo can be configured to have columns that are editable. When used in this capacity, embed the table view in a form with a submit button.

    Attributes
        rows(tuple or list, required): A list/tuple of lists/tuples representing each row in the table.
        column_names(tuple or list): A tuple or list of strings that represent the table columns names.
        hover(bool): Illuminate rows on hover (does not work on striped tables)
        striped(bool): Stripe rows
        bordered(bool): Add borders and rounded corners
        condensed(bool): A more tightly packed table
        editable_columns(list or tuple): A list or tuple with an entry for each column in the table. The entry is either False for non-editable columns or a string that will be used to create identifiers for the input fields in that column.
        row_ids(list or tuple): A list or tuple of ids for each row in the table. These will be combined with the string in the editable_columns parameter to create unique identifiers for easy input field in the table. If not specified, each row will be assigned an integer value.
        attributes(str): A string representing additional HTML attributes to add to the primary element (e.g. "onclick=run_me();").
        classes(str): Additional classes to add to the primary HTML element (e.g. "example-class another-class").

    Example

    ::

        # CONTROLLER
        from tethys_apps.sdk.gizmos import TableView

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

        # TEMPLATE

        {% gizmo table_view table_view %}
        {% gizmo table_view table_view_edit %}

    """

    def __init__(self, jobs, filters, hover=False, striped=False, bordered=False, condensed=False,
                 run_btn=True, delete_btn=True, results_url='', attributes='', classes=''):
        """
        Constructor
        """
        # Initialize super class
        super(JobsTable, self).__init__(attributes=attributes, classes=classes)


        self.jobs = jobs
        self.filters = filters
        self.rows = self.get_rows()
        self.column_names = [col_name.title().replace('_', ' ') for col_name in filters]
        self.hover = hover
        self.striped = striped
        self.bordered = bordered
        self.condensed = condensed
        self.run = run_btn
        self.delete = delete_btn
        self.results_url = results_url
        self.actions = self.delete
        self.status = self.run or self.results_url
        self.attributes = attributes
        self.classes = classes

    def get_rows(self):
        rows = []
        if self.jobs:
            attributes = self.jobs[0].__dict__.keys()
        for job in self.jobs:
            row_values = []
            for attribute in self.filters:
                if attribute in attributes:
                    row_values.append(job.__getattribute__(attribute))
            rows.append(row_values)
        return rows

