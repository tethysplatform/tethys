import unittest
from unittest import mock
import tethys_gizmos.gizmo_options.bokeh_view as bokeh_view
from bokeh.plotting import figure


class TestBokehView(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_BokehView(self):
        plot = figure(height=300)
        plot.circle([1, 2], [3, 4], radius=0.5)
        attr = {"title": "test title", "description": "test attributes"}
        result = bokeh_view.BokehView(plot, attributes=attr)

        self.assertIn("test attributes", result["attributes"]["description"])
        self.assertIn("Circle", result["script"])

    def test_get_vendor_css(self):
        result = bokeh_view.BokehView.get_vendor_css()
        self.assertEqual(0, len(result))

    def test_get_vendor_js(self):
        result = bokeh_view.BokehView.get_vendor_js()
        self.assertIn(".js", result[0])
        self.assertNotIn(".css", result[0])

    @mock.patch("tethys_gizmos.gizmo_options.bokeh_view.bk_settings")
    def test_bokeh_resources(self, mock_bk_settings):
        mock_bk_settings.resources.return_value = "server"
        bokeh_resources = bokeh_view.BokehView.bk_resources
        self.assertEqual(bokeh_resources.mode, "server")
        self.assertEqual(bokeh_resources.root_url, "/")

    @mock.patch("tethys_gizmos.gizmo_options.bokeh_view.BokehView.bk_resources")
    def test_get_bokeh_resources_server(self, mock_resources):
        mock_resources.mode = "server"
        mock_resources.js_files = ["/static/test.js", "/static/test1.js"]
        files = bokeh_view.BokehView._get_bokeh_resources("js")
        for f in files:
            self.assertNotIn("/static", f)

    @mock.patch("tethys_gizmos.gizmo_options.bokeh_view.bokeh")
    @mock.patch("tethys_gizmos.gizmo_options.bokeh_view.bk_settings")
    def test_bokeh_resources_inline(self, mock_bk_settings, mock_bokeh):
        mock_bokeh.__version__ = "3."
        mock_bk_settings.resources.return_value = "inline"
        bokeh_view.BokehView._bk_resources = None
        bokeh_resources = bokeh_view.BokehView.bk_resources
        self.assertEqual(bokeh_resources.mode, "server")
        self.assertEqual(bokeh_resources.root_url, "/")
