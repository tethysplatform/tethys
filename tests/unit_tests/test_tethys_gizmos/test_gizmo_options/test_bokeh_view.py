import unittest
import tethys_gizmos.gizmo_options.bokeh_view as bokeh_view
from bokeh.plotting import figure


class TestBokehView(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_BokehView(self):
        plot = figure(plot_height=300)
        plot.circle([1, 2], [3, 4])
        attr = {'title': 'test title', 'description': 'test attributes'}
        result = bokeh_view.BokehView(plot, attributes=attr)

        self.assertIn('test attributes', result['attributes']['description'])
        self.assertIn('Circle', result['script'])

    def test_get_vendor_css(self):
        result = bokeh_view.BokehView.get_vendor_css()
        self.assertEqual(0, len(result))

    def test_get_vendor_js(self):
        result = bokeh_view.BokehView.get_vendor_js()
        self.assertIn('.js', result[0])
        self.assertNotIn('.css', result[0])
