import unittest
import tethys_gizmos.gizmo_options.plot_view as gizmo_plot_view
import datetime


class TestPlotView(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_PlotViewBase(self):
        engine = "highcharts"
        result = gizmo_plot_view.PlotViewBase(engine=engine)

        # Check Result
        self.assertEqual(engine, result["engine"])

        # Engine is not d3 or hightcharts
        self.assertRaises(ValueError, gizmo_plot_view.PlotViewBase, engine="d2")

        # Check Get Method
        self.assertIn(".js", gizmo_plot_view.PlotViewBase.get_vendor_js()[0])
        self.assertNotIn(".css", gizmo_plot_view.PlotViewBase.get_vendor_js()[0])

        self.assertIn(".js", gizmo_plot_view.PlotViewBase.get_gizmo_js()[0])
        self.assertNotIn(".css", gizmo_plot_view.PlotViewBase.get_gizmo_js()[0])

        self.assertIn(".css", gizmo_plot_view.PlotViewBase.get_gizmo_css()[0])
        self.assertNotIn(".js", gizmo_plot_view.PlotViewBase.get_gizmo_css()[0])

    def test_PlotObject(self):
        chart = "test chart"
        xAxis = "Distance"
        yAxis = "Time"
        title = "Title"
        subtitle = "Subtitle"
        tooltip_format = "Format"
        custom = {"key1": "value1", "key2": "value2"}
        result = gizmo_plot_view.PlotObject(
            chart=chart,
            xAxis=xAxis,
            yAxis=yAxis,
            title=title,
            subtitle=subtitle,
            tooltip_format=tooltip_format,
            custom=custom,
        )
        # Check Result
        self.assertEqual(chart, result["chart"])
        self.assertEqual(xAxis, result["xAxis"])
        self.assertEqual(yAxis, result["yAxis"])
        self.assertEqual(title, result["title"]["text"])
        self.assertEqual(subtitle, result["subtitle"]["text"])
        self.assertEqual(tooltip_format, result["tooltip"])
        self.assertIn(custom["key1"], result["custom"]["key1"])
        self.assertIn(custom["key2"], result["custom"]["key2"])

    def test_LinePlot(self):
        series = [
            {
                "name": "Air Temp",
                "color": "#0066ff",
                "marker": {"enabled": False},
                "data": [
                    [0, 5],
                    [10, -70],
                    [20, -86.5],
                    [30, -66.5],
                    [40, -32.1],
                    [50, -12.5],
                    [60, -47.7],
                    [70, -85.7],
                    [80, -106.5],
                ],
            },
            {
                "name": "Water Temp",
                "color": "#ff6600",
                "data": [
                    [0, 15],
                    [10, -50],
                    [20, -56.5],
                    [30, -46.5],
                    [40, -22.1],
                    [50, -2.5],
                    [60, -27.7],
                    [70, -55.7],
                    [80, -76.5],
                ],
            },
        ]

        result = gizmo_plot_view.LinePlot(series=series)
        # Check result
        self.assertEqual(
            series[0]["color"], result["plot_object"]["series"][0]["color"]
        )
        self.assertEqual(series[0]["name"], result["plot_object"]["series"][0]["name"])
        self.assertEqual(series[0]["data"], result["plot_object"]["series"][0]["data"])

        x_axis_title = "Distance"
        x_axis_units = "m"
        y_axis_title = "Time"
        y_axis_units = "s"

        result = gizmo_plot_view.LinePlot(
            series=series,
            spline=True,
            x_axis_title=x_axis_title,
            y_axis_title=y_axis_title,
            x_axis_units=x_axis_units,
            y_axis_units=y_axis_units,
        )

        # Check result
        x_text = "{0} ({1})".format(x_axis_title, x_axis_units)
        y_text = "{0} ({1})".format(y_axis_title, y_axis_units)
        self.assertEqual(x_text, result["plot_object"]["xAxis"]["title"]["text"])
        self.assertEqual(y_text, result["plot_object"]["yAxis"]["title"]["text"])

    def test_PolarPlot(self):
        series = [
            {
                "name": "Park City",
                "data": [0.2, 0.5, 0.1, 0.8, 0.2, 0.6, 0.8, 0.3],
                "pointPlacement": "on",
            },
            {
                "name": "Little Dell",
                "data": [0.8, 0.3, 0.2, 0.5, 0.1, 0.8, 0.2, 0.6],
                "pointPlacement": "on",
            },
        ]

        result = gizmo_plot_view.PolarPlot(series=series)
        # Check result
        self.assertEqual(
            series[0]["pointPlacement"],
            result["plot_object"]["series"][0]["pointPlacement"],
        )
        self.assertEqual(series[0]["name"], result["plot_object"]["series"][0]["name"])
        self.assertEqual(series[0]["data"], result["plot_object"]["series"][0]["data"])

    def test_ScatterPlot(self):
        male_dataset = {
            "name": "Male",
            "color": "#0066ff",
            "data": [[174.0, 65.6], [175.3, 71.8], [193.5, 80.7], [186.5, 72.6]],
        }

        female_dataset = {
            "name": "Female",
            "color": "#ff6600",
            "data": [[161.2, 51.6], [167.5, 59.0], [159.5, 49.2], [157.0, 63.0]],
        }

        series = [male_dataset, female_dataset]
        x_axis_title = "Distance"
        x_axis_units = "m"
        y_axis_title = "Time"
        y_axis_units = "s"

        result = gizmo_plot_view.ScatterPlot(
            series=series,
            x_axis_title=x_axis_title,
            y_axis_title=y_axis_title,
            x_axis_units=x_axis_units,
            y_axis_units=y_axis_units,
        )

        # Check result
        x_text = "{0} ({1})".format(x_axis_title, x_axis_units)
        y_text = "{0} ({1})".format(y_axis_title, y_axis_units)
        self.assertEqual(x_text, result["plot_object"]["xAxis"]["title"]["text"])
        self.assertEqual(y_text, result["plot_object"]["yAxis"]["title"]["text"])
        self.assertEqual(
            series[0]["color"], result["plot_object"]["series"][0]["color"]
        )
        self.assertEqual(series[0]["name"], result["plot_object"]["series"][0]["name"])
        self.assertEqual(series[0]["data"], result["plot_object"]["series"][0]["data"])
        self.assertEqual(
            series[1]["color"], result["plot_object"]["series"][1]["color"]
        )
        self.assertEqual(series[1]["name"], result["plot_object"]["series"][1]["name"])
        self.assertEqual(series[1]["data"], result["plot_object"]["series"][1]["data"])

    def test_PiePlot(self):
        series = [
            {"name": "Park City", "data": [0.2, 0.5, 0.1, 0.8, 0.2, 0.6, 0.8, 0.3]},
        ]

        result = gizmo_plot_view.PiePlot(series=series)

        # Check result
        self.assertEqual(series[0]["name"], result["plot_object"]["series"][0]["name"])
        self.assertEqual(series[0]["data"], result["plot_object"]["series"][0]["data"])

    def test_BarPlot(self):
        series = [
            {
                "name": "Year 1800",
                "data": [100, 31, 635, 203, 275, 487, 872, 671, 736, 568, 487, 432],
            },
            {
                "name": "Year 1900",
                "data": [133, 200, 947, 408, 682, 328, 917, 171, 482, 140, 176, 237],
            },
        ]

        result = gizmo_plot_view.BarPlot(series=series)
        # Check result
        self.assertEqual(series[0]["name"], result["plot_object"]["series"][0]["name"])
        self.assertEqual(series[0]["data"], result["plot_object"]["series"][0]["data"])

        axis_title = "Population"
        axis_units = "Millions"
        result = gizmo_plot_view.BarPlot(
            series=series, horizontal=True, axis_title=axis_title, axis_units=axis_units
        )
        # Check result
        y_text = "{0} ({1})".format(axis_title, axis_units)
        self.assertEqual(y_text, result["plot_object"]["yAxis"]["title"]["text"])
        self.assertEqual(series[0]["name"], result["plot_object"]["series"][0]["name"])
        self.assertEqual(series[0]["data"], result["plot_object"]["series"][0]["data"])

    def test_TimeSeries(self):
        series = [
            {
                "name": "Winter 2007-2008",
                "data": [["12/02/2008", 0.8], ["12/09/2008", 0.6]],
            }
        ]

        result = gizmo_plot_view.TimeSeries(series=series)
        # Check result
        self.assertEqual(series[0]["name"], result["plot_object"]["series"][0]["name"])
        self.assertEqual(series[0]["data"], result["plot_object"]["series"][0]["data"])

    def test_AreaRange(self):
        averages = [
            [datetime.date(2009, 7, 1), 21.5],
            [datetime.date(2009, 7, 2), 22.1],
            [datetime.date(2009, 7, 3), 23],
        ]
        ranges = [
            [datetime.date(2009, 7, 1), 14.3, 27.7],
            [datetime.date(2009, 7, 2), 14.5, 27.8],
            [datetime.date(2009, 7, 3), 15.5, 29.6],
        ]
        series = [
            {
                "name": "Temperature",
                "data": averages,
                "zIndex": 1,
                "marker": {
                    "lineWidth": 2,
                },
            },
            {
                "name": "Range",
                "data": ranges,
                "type": "arearange",
                "lineWidth": 0,
                "linkedTo": ":previous",
                "fillOpacity": 0.3,
                "zIndex": 0,
            },
        ]
        result = gizmo_plot_view.AreaRange(series=series)
        # Check result
        self.assertEqual(series[0]["name"], result["plot_object"]["series"][0]["name"])
        self.assertEqual(series[0]["data"], result["plot_object"]["series"][0]["data"])

    def test_HeatMap(self):
        sales_data = [
            [0, 0, 10],
            [0, 1, 19],
            [0, 2, 8],
            [0, 3, 24],
            [0, 4, 67],
            [1, 0, 92],
        ]
        series = [
            {
                "name": "Sales per employee",
                "borderWidth": 1,
                "data": sales_data,
                "dataLabels": {"enabled": True, "color": "#000000"},
            }
        ]

        result = gizmo_plot_view.HeatMap(series=series)
        # Check result
        self.assertEqual(series[0]["name"], result["plot_object"]["series"][0]["name"])
        self.assertEqual(series[0]["data"], result["plot_object"]["series"][0]["data"])
