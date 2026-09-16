import unittest
import warnings
from unittest import mock
import tethys_gizmos.gizmo_options.plotly_view as gizmo_plotly_view
import plotly.graph_objs as go


class TestPlotlyView(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_PlotlyView(self):
        trace0 = go.Scatter(x=[1, 2, 3, 4], y=[10, 15, 13, 17])
        trace1 = go.Scatter(x=[1, 2, 3, 4], y=[16, 5, 11, 9])
        plot_input = [trace0, trace1]

        result = gizmo_plotly_view.PlotlyView(plot_input)
        # Check Result
        self.assertIn(",".join(str(e) for e in trace0.x), result["plotly_div"])
        self.assertIn(",".join(str(e) for e in trace0.y), result["plotly_div"])
        self.assertIn(",".join(str(e) for e in trace1.x), result["plotly_div"])
        self.assertIn(",".join(str(e) for e in trace1.y), result["plotly_div"])

        self.assertIn(".js", gizmo_plotly_view.PlotlyView.get_vendor_js()[0])
        self.assertNotIn(".css", gizmo_plotly_view.PlotlyView.get_vendor_js()[0])

    def test_PlotlyView_show_link_backward_compatible(self):
        with mock.patch.object(
            gizmo_plotly_view.opy, "plot", return_value="<div></div>"
        ) as mock_plot:
            with warnings.catch_warnings(record=True) as caught_warnings:
                warnings.simplefilter("always")
                result = gizmo_plotly_view.PlotlyView([], show_link=True)

        self.assertEqual("<div></div>", result["plotly_div"])
        _, kwargs = mock_plot.call_args
        self.assertNotIn("show_link", kwargs)
        self.assertTrue(
            any(item.category == DeprecationWarning for item in caught_warnings)
        )
        self.assertTrue(
            any("show_link" in str(item.message) for item in caught_warnings)
        )
        self.assertTrue(
            any("has no effect" in str(item.message) for item in caught_warnings)
        )

    def test_PlotlyView_show_link_false_warns(self):
        with mock.patch.object(
            gizmo_plotly_view.opy, "plot", return_value="<div></div>"
        ):
            with warnings.catch_warnings(record=True) as caught_warnings:
                warnings.simplefilter("always")
                gizmo_plotly_view.PlotlyView([], show_link=False)

        self.assertTrue(
            any(item.category == DeprecationWarning for item in caught_warnings)
        )

    def test_PlotlyView_without_show_link_does_not_warn(self):
        with mock.patch.object(
            gizmo_plotly_view.opy, "plot", return_value="<div></div>"
        ):
            with warnings.catch_warnings(record=True) as caught_warnings:
                warnings.simplefilter("always")
                gizmo_plotly_view.PlotlyView([])

        self.assertFalse(caught_warnings)
