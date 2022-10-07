import unittest
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
