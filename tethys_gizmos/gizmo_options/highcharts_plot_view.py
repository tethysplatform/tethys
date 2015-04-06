from .base import TethysGizmoOptions

__all__ = ['PlotView', 'HighChartsObjectBase', 'HighChartsLinePlot', 'HighChartsPolarPlot', 'HighChartsScatterPlot',
           'HighChartsPiePlot']


class PlotView(TethysGizmoOptions):
    """
    Highcharts Plot View

    Plot views can be used to generate interactive plots of tabular data. All of the plots available through this gizmo are powered by the Highcharts JavaScript library.

    Attributes
    highcharts_object(PySON, required): The highcharts_object contains the definition of the chart. The full `Highcharts API reference <http://api.highcharts.com/highcharts>`_ is supported via this object. The object can either be a JavaScript string or a JavaScript-equivalent Python data structure. The latter is recommended.
    height(string): Height of the plot element. Any valid css unit of length.
    width(string): Width of the plot element. Any valid css unit of length.
    attributes(string): Any HTML attributes to add to the plot element (e.g.: "id=foo name=bar value=hello-world")
    """

    def __init__(self, highcharts_object, height='520px', width='100%', attributes=""):
        """
        Constructor
        """
        # Initialize super class
        super(PlotView, self).__init__()

        self.highcharts_object = highcharts_object
        self.height = height
        self.width = width
        self.attributes = attributes


class HighChartsObjectBase(TethysGizmoOptions):
    """
    HighCharts Object

    Attributes
    """

    def __init__(self, chart={}, title='', subtitle='', **kwargs):
        """
        Constructor
        """
        # Initialize super class
        super(HighChartsObjectBase, self).__init__()

        self.chart = chart
        self.title = title
        self.subtitle = subtitle
        # add any other attributes the user wants
        for key, value in kwargs.iteritems():
            setattr(self, key, value)


class HighChartsLinePlot(HighChartsObjectBase):
    """
    Line Plot

    Displays as a line graph.

    Attributes
    """

    def __init__(self, chart={'type': 'spline'}, series=[], title='', subtitle='',  **kwargs):
        """
        Constructor

        Args:
        """

        # Initialize super class
        super(HighChartsLinePlot, self).__init__(chart=chart, title=title, subtitle=subtitle, series=series, **kwargs)


class HighChartsPolarPlot(HighChartsObjectBase):
    """
    Polar or Spider Plot

    Displays as a polar plot.

    Attributes
    """

    def __init__(self, chart={'polar': True, 'type': 'line'}, series=[], title='', subtitle='', **kwargs):
        """
        Constructor

        Args:
        """
        # Initialize super class
        super(HighChartsPolarPlot, self).__init__(chart=chart, title=title, subtitle=subtitle, series=series, **kwargs)


class HighChartsScatterPlot(HighChartsObjectBase):
    """
    Scatter Plot

    Displays as a scatter plot.

    Attributes
    """

    def __init__(self, chart={'scatter': True, 'type': 'line'}, series=[], title='', subtitle='', **kwargs):
        """
        Constructor

        Args:
        """
        # Initialize super class
        super(HighChartsScatterPlot, self).__init__(chart=chart, title=title, subtitle=subtitle, series=series, **kwargs)


class HighChartsPiePlot(HighChartsObjectBase):
    """
    Pie Plot

    Displays as a pie chart.

    Attributes
    """

    def __init__(self, chart={'polar': True, 'type': 'pie'}, series=[], title='', subtitle='', **kwargs):
        """
        Constructor

        Args:
        """
        # Initialize super class
        super(HighChartsPiePlot, self).__init__(chart=chart, title=title, subtitle=subtitle, series=series, **kwargs)