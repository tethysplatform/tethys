import unittest
import tethys_gizmos.gizmo_options.datatable_view as gizmo_datatable_view


class TestDatatableView(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_DataTableView(self):
        column_names = ['Name', 'Age', 'Job']
        datatable_options = {'rows': [['Bill', '30', 'contractor'], ['Fred', '18', 'programmer']]}
        rows = 2
        result = gizmo_datatable_view.DataTableView(rows=rows, column_names=column_names,
                                                    datatable_options=datatable_options)
        # Check Result
        self.assertEqual(rows, result['rows'])
        self.assertEqual(column_names, result['column_names'])
        self.assertIn(datatable_options['rows'][0][0], result['datatable_options']['datatable_options'])
        self.assertIn(datatable_options['rows'][0][1], result['datatable_options']['datatable_options'])
        self.assertIn(datatable_options['rows'][0][2], result['datatable_options']['datatable_options'])
        self.assertIn(datatable_options['rows'][1][0], result['datatable_options']['datatable_options'])
        self.assertIn(datatable_options['rows'][1][1], result['datatable_options']['datatable_options'])
        self.assertIn(datatable_options['rows'][1][2], result['datatable_options']['datatable_options'])

        result = gizmo_datatable_view.DataTableView.get_vendor_css()
        # Check Result
        self.assertIn('.css', result[0])
        self.assertNotIn('.js', result[0])

        result = gizmo_datatable_view.DataTableView.get_vendor_js()
        # Check Result
        self.assertIn('.js', result[0])
        self.assertNotIn('.css', result[0])

        result = gizmo_datatable_view.DataTableView.get_gizmo_js()
        # Check Result
        self.assertIn('.js', result[0])
        self.assertNotIn('.css', result[0])
