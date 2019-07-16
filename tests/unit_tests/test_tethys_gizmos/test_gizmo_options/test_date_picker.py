import unittest
import tethys_gizmos.gizmo_options.date_picker as gizmo_date_picker


class TestButton(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_DatePicker(self):
        name = 'Date Picker'
        display_text = 'Unit Test'
        autoclose = True
        calendar_weeks = True
        clear_button = True
        days_of_week_disabled = '6'
        min_view_mode = 'days'

        result = gizmo_date_picker.DatePicker(name=name, display_text=display_text, autoclose=autoclose,
                                              calendar_weeks=calendar_weeks, clear_button=clear_button,
                                              days_of_week_disabled=days_of_week_disabled, min_view_mode=min_view_mode)

        # Check Result
        self.assertIn(name, result['name'])
        self.assertIn(display_text, result['display_text'])
        self.assertTrue(result['autoclose'])
        self.assertTrue(result['calendar_weeks'])
        self.assertTrue(result['clear_button'])
        self.assertIn(days_of_week_disabled, result['days_of_week_disabled'])
        self.assertIn(min_view_mode, result['min_view_mode'])

        result = gizmo_date_picker.DatePicker.get_vendor_css()

        # Check Result
        self.assertIn('.css', result[0])
        self.assertNotIn('.js', result[0])

        result = gizmo_date_picker.DatePicker.get_vendor_js()
        self.assertIn('.js', result[0])
        self.assertNotIn('.css', result[0])
