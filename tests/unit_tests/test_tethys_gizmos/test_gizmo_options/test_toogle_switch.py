import unittest
import tethys_gizmos.gizmo_options.toggle_switch as gizmo_toggle_switch


class TestToggleSwitch(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_ToggleSwitch(self):
        display_text = 'Styled Toggle'
        name = 'toggle2'
        on_label = 'Yes'
        off_label = 'No'
        on_style = 'success'
        off_style = 'danger'
        initial = True
        size = 'large'

        result = gizmo_toggle_switch.ToggleSwitch(name=name, display_text=display_text, on_label=on_label,
                                                  off_label=off_label, on_style=on_style, off_style=off_style,
                                                  initial=initial, size=size)
        # Check Result
        self.assertEqual(display_text, result['display_text'])
        self.assertEqual(name, result['name'])
        self.assertEqual(on_label, result['on_label'])
        self.assertEqual(off_label, result['off_label'])
        self.assertEqual(on_style, result['on_style'])
        self.assertTrue(result['initial'])
        self.assertEqual(size, result['size'])

        self.assertIn('.js', gizmo_toggle_switch.ToggleSwitch.get_vendor_js()[0])
        self.assertNotIn('.css', gizmo_toggle_switch.ToggleSwitch.get_vendor_js()[0])

        self.assertIn('.css', gizmo_toggle_switch.ToggleSwitch.get_vendor_css()[0])
        self.assertNotIn('.js', gizmo_toggle_switch.ToggleSwitch.get_vendor_css()[0])

        self.assertIn('.js', gizmo_toggle_switch.ToggleSwitch.get_gizmo_js()[0])
        self.assertNotIn('.css', gizmo_toggle_switch.ToggleSwitch.get_gizmo_js()[0])
