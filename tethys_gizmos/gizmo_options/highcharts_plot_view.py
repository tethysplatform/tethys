from .base import TethysGizmoOptions

__all__ = ['PlotView', 'HighChartsObjectBase', 'HighChartsLinePlot', 'HighChartsPolarPlot', 'HighChartsScatterPlot',
           'HighChartsPiePlot']


class PlotView(TethysGizmoOptions):
    """
    Plot views can be used to generate interactive plots of tabular data. All of the plots available through this gizmo are powered by the Highcharts JavaScript library.

    Attributes
        highcharts_object(PySON, required): The highcharts_object contains the definition of the chart. The full `Highcharts API reference <http://api.highcharts.com/highcharts>`_ is supported via this object. The object can either be a JavaScript string or a JavaScript-equivalent Python data structure. The latter is recommended.
        height(str): Height of the plot element. Any valid css unit of length.
        width(str): Width of the plot element. Any valid css unit of length.
        attributes(str): Any HTML attributes to add to the plot element (e.g.: "id=foo name=bar value=hello-world")

    Example

    ::

        # CONSTRUCTOR

        highcharts_object = HighChartsLinePlot(title={'text': 'Plot Title'},
                                               subtitle={'text': 'Plot Subtitle'},
                                               legend={
                                                   'layout': 'vertical',
                                                   'align': 'right',
                                                   'verticalAlign': 'middle',
                                                   'borderWidth': 0
                                               },
                                               xAxis={
                                                   'title': {'enabled': True,
                                                             'text': 'Altitude (km)'
                                                   },
                                                   'labels': {
                                                       'formatter': 'function () { return this.value + " km"; }'
                                                   }
                                               },
                                               yAxis={
                                                   'title': {
                                                       'enabled': True,
                                                       'text': 'Temperature (*C)'
                                                   },
                                                   'labels': {'formatter': 'function () { return this.value + " *C"; }'}
                                               },
                                               tooltip={'headerFormat': '<b>{series.name}</b><br/>',
                                                        'pointFormat': '{point.x} km: {point.y}*C'
                                               },
                                               series=[
                                                   {
                                                       'name': 'Air Temp',
                                                       'color': '#0066ff',
                                                       'marker': {'enabled': False},
                                                       'data': [
                                                           [0, 5], [10, -70],
                                                           [20, -86.5], [30, -66.5],
                                                           [40, -32.1],
                                                           [50, -12.5], [60, -47.7],
                                                           [70, -85.7], [80, -106.5]
                                                       ]
                                                   },
                                                   {
                                                       'name': 'Water Temp',
                                                       'color': '#ff6600',
                                                       'data': [[0, 15], [10, -50],
                                                                [20, -56.5], [30, -46.5],
                                                                [40, -22.1],
                                                                [50, -2.5], [60, -27.7],
                                                                [70, -55.7], [80, -76.5]
                                                       ]
                                                   }
                                               ]
        )

        line_plot_view = PlotView(highcharts_object=highcharts_object,
                                  width='500px',
                                  height='500px')

        # TEMPLATE

        {% gizmo highcharts_plot_view line_plot_view %}

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
        chart['type'] = 'spline'

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