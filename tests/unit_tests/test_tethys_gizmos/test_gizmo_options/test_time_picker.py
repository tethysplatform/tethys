import unittest
import tethys_gizmos.gizmo_options.time_picker as gizmo_time_picker


class TestTimePicker(unittest.TestCase):
    def setUp(self):
        self.name = "Time Picker"
        self.display_text = "Unit Test"
        self.default_time = "2:30 PM"
        self.minute_step = 15
        self.show_seconds = True
        self.show_meridian = False

        self.gizmo = gizmo_time_picker.TimePicker(
            name=self.name,
            display_text=self.display_text,
            default_time=self.default_time,
            minute_step=self.minute_step,
            show_seconds=self.show_seconds,
            show_meridian=self.show_meridian,
        )

    def tearDown(self):
        pass

    def test_TimePicker(self):
        self.assertIn(self.name, self.gizmo["name"])
        self.assertIn(self.display_text, self.gizmo["display_text"])
        self.assertIn(self.default_time, self.gizmo["default_time"])
        self.assertEqual(self.minute_step, self.gizmo["minute_step"])
        self.assertTrue(self.gizmo["show_seconds"])
        self.assertFalse(self.gizmo["show_meridian"])

    def test_get_vendor_css(self):
        result = gizmo_time_picker.TimePicker.get_vendor_css()

        self.assertIn("bootstrap-timepicker.min.css", result[0])
        self.assertNotIn("bootstrap-timepicker.min.js", result[0])

    def test_get_vendor_js(self):
        result = gizmo_time_picker.TimePicker.get_vendor_js()

        self.assertIn("bootstrap-timepicker.min.js", result[0])
        self.assertNotIn("bootstrap-timepicker.min.css", result[0])

    def test_get_gizmo_css(self):
        result = gizmo_time_picker.TimePicker.get_gizmo_css()

        self.assertIn("tethys_gizmos/css/time_picker.css", result[0])

    def test_get_gizmo_js(self):
        result = gizmo_time_picker.TimePicker.get_gizmo_js()

        self.assertEqual(result, ())
