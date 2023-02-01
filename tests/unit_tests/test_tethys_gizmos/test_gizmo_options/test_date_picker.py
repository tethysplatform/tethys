import unittest
import tethys_gizmos.gizmo_options.date_picker as gizmo_date_picker


class TestButton(unittest.TestCase):
    def setUp(self):
        self.name = "Date Picker"
        self.display_text = "Unit Test"
        self.autoclose = True
        self.calendar_weeks = True
        self.clear_button = True
        self.days_of_week_disabled = "6"
        self.min_view_mode = "days"

        self.gizmo = gizmo_date_picker.DatePicker(
            name=self.name,
            display_text=self.display_text,
            autoclose=self.autoclose,
            calendar_weeks=self.calendar_weeks,
            clear_button=self.clear_button,
            days_of_week_disabled=self.days_of_week_disabled,
            min_view_mode=self.min_view_mode,
        )

    def tearDown(self):
        pass

    def test_DatePicker(self):
        # Check Result
        self.assertIn(self.name, self.gizmo["name"])
        self.assertIn(self.display_text, self.gizmo["display_text"])
        self.assertTrue(self.gizmo["autoclose"])
        self.assertTrue(self.gizmo["calendar_weeks"])
        self.assertTrue(self.gizmo["clear_button"])
        self.assertIn(self.days_of_week_disabled, self.gizmo["days_of_week_disabled"])
        self.assertIn(self.min_view_mode, self.gizmo["min_view_mode"])

    def test_get_vendor_css(self):
        result = gizmo_date_picker.DatePicker.get_vendor_css()

        self.assertIn("bootstrap-datepicker3.min.css", result[0])
        self.assertNotIn("bootstrap-datepicker.min.js", result[0])

    def test_get_vendor_js(self):
        result = gizmo_date_picker.DatePicker.get_vendor_js()

        self.assertIn("bootstrap-datepicker.min.js", result[0])
        self.assertNotIn("bootstrap-datepicker3.min.css", result[0])
