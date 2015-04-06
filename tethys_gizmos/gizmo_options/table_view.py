from .base import TethysGizmoOptions

__all__ = ['TableView']


class TableView(TethysGizmoOptions):
    """
    Table View

    Table views can be used to display tabular data. The table view gizmo can be configured to have columns that are editable. When used in this capacity, embed the table view in a form with a submit button.

    Attributes
    rows(tuple/list, required): A list/tuple of lists/tuples representing each row in the table.
    column_names(tuple/list): A tuple or list of strings that represent the table columns names.
    hover(bool): Illuminate rows on hover (does not work on striped tables)
    striped(bool): Stripe rows
    bordered(bool): Add borders and rounded corners
    condensed(bool): A more tightly packed table
    editable_columns(list/tuple): A list or tuple with an entry for each column in the table. The entry is either False for non-editable columns or a string that will be used to create identifiers for the input fields in that column.
    row_ids(list/tuple): A list or tuple of ids for each row in the table. These will be combined with the string in the editable_columns parameter to create unique identifiers for easy input field in the table. If not specified, each row will be assigned an integer value.
    """

    def __init__(self, rows, column_names='', hover=False, striped=False, bordered=False, condensed=False, editable_columns='', row_ids=''):
        """
        Constructor
        """
        # Initialize super class
        super(TableView, self).__init__()

        self.rows = rows
        self.column_names = column_names
        self.hover = hover
        self.striped = striped
        self.bordered = bordered
        self.condensed = condensed
        self.editable_columns = editable_columns
        self.row_ids = row_ids