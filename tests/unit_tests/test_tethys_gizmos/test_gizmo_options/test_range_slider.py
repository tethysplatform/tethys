import unittest
import tethys_gizmos.gizmo_options.range_slider as gizmo_range_slider


class TestRangeSlider(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_RangeSlider(self):
        name = 'Test Range Slider'
        min = 0
        max = 100
        initial = 50
        step = 1

        result = gizmo_range_slider.RangeSlider(name=name, min=min, max=max, initial=initial, step=step)

        # Check Result
        self.assertEqual(name, result['name'])
        self.assertEqual(min, result['min'])
        self.assertEqual(max, result['max'])
        self.assertEqual(initial, result['initial'])
        self.assertEqual(step, result['step'])

        self.assertIn('.js', gizmo_range_slider.RangeSlider.get_gizmo_js()[0])
        self.assertNotIn('.css', gizmo_range_slider.RangeSlider.get_gizmo_js()[0])
