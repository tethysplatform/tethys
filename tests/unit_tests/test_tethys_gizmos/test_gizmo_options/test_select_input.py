import unittest
import tethys_gizmos.gizmo_options.select_input as gizmo_select_input


class TestSelectInput(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_SelectInput(self):
        display_text = "Select2 Multiple"
        name = "select21"
        multiple = True
        options = [("One", "1"), ("Two", "2"), ("Three", "3")]
        initial = ["Two", "One"]

        result = gizmo_select_input.SelectInput(
            name=name,
            display_text=display_text,
            multiple=multiple,
            options=options,
            initial=initial,
        )

        self.assertEqual(name, result["name"])
        self.assertEqual(display_text, result["display_text"])
        self.assertTrue(result["multiple"])
        self.assertEqual(options, result["options"])
        self.assertEqual(initial, result["initial"])

        self.assertTrue(
            gizmo_select_input.SelectInput.get_vendor_js()[0].endswith(".js")
        )
        self.assertFalse(
            gizmo_select_input.SelectInput.get_vendor_js()[0].endswith(".css")
        )

        self.assertTrue(
            gizmo_select_input.SelectInput.get_vendor_css()[0].endswith(".css")
        )
        self.assertFalse(
            gizmo_select_input.SelectInput.get_vendor_css()[0].endswith(".js")
        )

        self.assertTrue(
            gizmo_select_input.SelectInput.get_gizmo_js()[0].endswith(".js")
        )
        self.assertFalse(
            gizmo_select_input.SelectInput.get_gizmo_js()[0].endswith(".css")
        )
