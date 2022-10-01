import unittest
import tethys_gizmos.gizmo_options.table_view as gizmo_table_view


class TestTableView(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_TableView(self):
        rows = [
            ("Bill", "30", "contractor"),
            ("Fred", "18", "programmer"),
            ("Bob", "26", "boss"),
        ]
        column_names = ["Name", "Age", "Job"]

        result = gizmo_table_view.TableView(rows=rows, column_names=column_names)

        self.assertEqual(rows, result["rows"])
        self.assertEqual(column_names, result["column_names"])
