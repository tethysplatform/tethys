from .base import TethysGizmoOptions

__all__ = ['PlotView', 'HighChartsObjectBase', 'HighChartsLinePlot', 'HighChartsPolarPlot', 'HighChartsScatterPlot',
           'HighChartsPiePlot', 'HighChartsBarPlot', 'HighChartsTimeSeries', 'HighChartsAreaRange', 'HighChartsHeatMap']


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

        # CONTROLLER

        from tethys_gizmos.gizmo_options import PlotView, HighChartsLinePlot, HighChartsObjectBase, HighChartsPolarPlot, HighChartsScatterPlot, HighChartsPiePlot

        highcharts_object = HighChartsLinePlot(title='Plot Title',
                                               subtitle='Plot Subtitle',
                                               spline=True,
                                               x_axis_title='Altitude',
                                               x_axis_units='km',
                                               y_axis_title='Temperature',
                                               y_axis_units='*C',
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
                                                       'data': [
                                                           [0, 15], [10, -50],
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

    def __init__(self, chart={}, title='', subtitle='', legend=True, tooltip=True, x_axis={}, y_axis={},
                 tooltip_format={}, plotOptions={}, **kwargs):
        """
        Constructor
        """
        # Initialize super class
        super(HighChartsObjectBase, self).__init__()

        self.chart = chart
        self.xAxis = x_axis
        self.yAxis = y_axis
        self.plotOptions = plotOptions
        if title != '':
            self.title = {'text': title}

        if subtitle != '':
            self.subtitle = {'text': subtitle}

        if legend:
            self.legend = {
                'layout': 'vertical',
                'align': 'right',
                'verticalAlign': 'middle',
                'borderWidth': 0
            }

        if tooltip:
            self.tooltip = tooltip_format

        # add any other attributes the user wants
        for key, value in kwargs.iteritems():
            setattr(self, key, value)


class HighChartsLinePlot(HighChartsObjectBase):
    """
    Line Plot

    Displays as a line graph.

    Attributes
    """

    def __init__(self, series, title='', subtitle='', spline=False, x_axis_title='', x_axis_units='', y_axis_title='',
                 y_axis_units='', **kwargs):
        """
        Constructor

        Args:
        """
        if spline:
            chart = {'type': 'spline'}
        else:
            chart = {'type': 'line'}

        if x_axis_title:
            x_axis = {
                'title': {
                    'enabled': True,
                    'text': '{0} ({1})'.format(x_axis_title, x_axis_units)
                },
                'labels': {'formatter': 'function () { return this.value + " %s"; }' % x_axis_units}
            }
        else:
            x_axis = {
                'labels': {'formatter': 'function () { return this.value + " %s"; }' % x_axis_units}
            }

        if y_axis_title:
            y_axis = {
                'title': {
                    'enabled': True,
                    'text': '{0} ({1})'.format(y_axis_title, y_axis_units)
                },
                'labels': {'formatter': 'function () { return this.value + " %s"; }' % y_axis_units}
            }
        else:
            y_axis = {
                'labels': {'formatter': 'function () { return this.value + " %s"; }' % y_axis_units}
            }

        tooltip_format = {
            'headerFormat': '<b>{series.name}</b><br/>',
            'pointFormat': '{point.x} %s: {point.y} %s' % (x_axis_units, y_axis_units)
        }

        # Initialize super class
        super(HighChartsLinePlot, self).__init__(chart=chart, title=title, subtitle=subtitle, series=series,
                                                 x_axis=x_axis, y_axis=y_axis, tooltip_format=tooltip_format, **kwargs)


class HighChartsPolarPlot(HighChartsObjectBase):
    """
    Polar or Spider Plot

    Displays as a polar plot.

    Attributes
    """

    def __init__(self, series=[], title='', subtitle='', categories=[], **kwargs):
        """
        Constructor

        Args:
        """
        chart = {
            'polar': True,
            'type': 'line'
        }

        x_axis = {
            'categories': categories,
            'tickmarkPlacement': 'on',
            'lineWidth': 0
        }

        y_axis = {
            'gridLineInterpolation': 'polygon',
            'lineWidth': 0,
            'min': 0
        }

        # Initialize super class
        super(HighChartsPolarPlot, self).__init__(chart=chart, title=title, subtitle=subtitle, series=series,
                                                  x_axis=x_axis, y_axis=y_axis, **kwargs)


class HighChartsScatterPlot(HighChartsObjectBase):
    """
    Scatter Plot

    Displays as a scatter plot.

    Attributes
    """

    def __init__(self, series=[], title='', subtitle='', x_axis_title='', x_axis_units='', y_axis_title='',
                 y_axis_units='', **kwargs):
        """
        Constructor

        Args:
        """
        chart = {
            'type': 'scatter',
            'zoomType': 'xy'
        }

        if x_axis_title:
            x_axis = {
                'title': {
                    'enabled': True,
                    'text': '{0} ({1})'.format(x_axis_title, x_axis_units)
                }
            }

        if y_axis_title:
            y_axis = {
                'title': {
                    'enabled': True,
                    'text': '{0} ({1})'.format(y_axis_title, y_axis_units)
                }
            }

        tooltip_format = {
            'headerFormat': '<b>{series.name}</b><br/>',
            'pointFormat': '{point.x} %s: {point.y} %s' % (x_axis_units, y_axis_units)
        }

        # Initialize super class
        super(HighChartsScatterPlot, self).__init__(chart=chart, title=title, subtitle=subtitle, series=series,
                                                    x_axis=x_axis, y_axis=y_axis, tooltip_format=tooltip_format,
                                                    **kwargs)


class HighChartsPiePlot(HighChartsObjectBase):
    """
    Pie Plot

    Displays as a pie chart.

    Attributes
    """

    def __init__(self, series=[], title='', subtitle='', **kwargs):
        """
        Constructor

        Args:
        """
        chart = {
            'plotShadow': False
        }
        plotOptions = {
            'pie': {
                'allowPointSelect': True,
                'cursor': 'pointer',
                'dataLabels': {
                    'enabled': False
                },
                'showInLegend': True
            }
        }
        tooltip_format = {
            'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>'
        }
        # Initialize super class
        super(HighChartsPiePlot, self).__init__(chart=chart, title=title, subtitle=subtitle, series=series,
                                                plotOptions=plotOptions, tooltip_format=tooltip_format, **kwargs)


class HighChartsBarPlot(HighChartsObjectBase):
    """
    Bar Plot

    Displays as either a bar or column chart.

    Attributes
    """

    def __init__(self, series=[], title='', subtitle='', horizontal=False, categories=[], y_axis_title='',
                 y_axis_units='', group_tools=True, **kwargs):
        """
        Constructor

        Args:
        """
        if not horizontal:
            chart = {
                'type': 'column'
            }
            plotOptions = {
                'column': {
                    'pointPadding': 0.2,
                    'borderWidth': 0
                }
            }
        else:
            chart = {
                'type': 'bar'
            }
            plotOptions = {
                'bar': {
                    'dataLabels': {
                        'enabled': True
                    }
                }
            }

        x_axis = {
            'categories': categories,
            'crosshair': True
        }

        y_axis = {
            'min': 0,
            'title': {
                'text': '{0} ({1})'.format(y_axis_title, y_axis_units)
            }
        }

        if group_tools:
            tooltip_format = {
                'headerFormat': '<span style="font-size:10px">{point.key}</span><table>',
                'pointFormat': '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' + '<td style="padding:0"><b>{point.y:.1f} %s </b></td></tr>' % (
                    y_axis_units),
                'footerFormat': '</table>',
                'shared': True,
                'useHTML': True
            }

        # Initialize super class
        super(HighChartsBarPlot, self).__init__(chart=chart, title=title, subtitle=subtitle, series=series,
                                                plotOptions=plotOptions, tooltip_format=tooltip_format, x_axis=x_axis,
                                                y_axis=y_axis, **kwargs)


class HighChartsTimeSeries(HighChartsObjectBase):
    """
    Time Series Plot

    Displays data as a timeseries plot

    Attributes
    """

    def __init__(self, series=[], title='', subtitle='', y_axis_title='', y_axis_units='', **kwargs):
        """
        Constructor

        Args:
        """

        chart = {
            'type': 'area',
            'zoomType': 'x'
        }

        x_axis = {
            'maxZoom': 30 * 24 * 3600000,
            'type': 'datetime'
        }

        y_axis = {
            'title': {
                'text': '{0} ({1})'.format(y_axis_title, y_axis_units)
            },
            'min': 0
        }

        tooltip_format = {
            'pointFormat': '{point.y} %s' % (y_axis_units)
        }

        # Initialize super class
        super(HighChartsTimeSeries, self).__init__(chart=chart, title=title, subtitle=subtitle, series=series,
                                                   x_axis=x_axis, y_axis=y_axis, tooltip_format=tooltip_format,
                                                   **kwargs)


class HighChartsAreaRange(HighChartsObjectBase):
    """
    Area Range Plot

    Displays data as an area range plot

    Attributes
    """

    def __init__(self, series=[], title='', subtitle='', y_axis_title='', y_axis_units='', **kwargs):
        """
        Constructor

        Args:
        """

        chart = {
        }

        x_axis = {
            'type': 'datetime'
        }

        y_axis = {
            'title': {
                'text': '{0} ({1})'.format(y_axis_title, y_axis_units)
            }
        }

        tooltip_format = {
            'crosshairs': True,
            'shared': True,
            'valueSuffix': y_axis_units
        }

        # Initialize super class
        super(HighChartsAreaRange, self).__init__(chart=chart, title=title, subtitle=subtitle, series=series,
                                                  x_axis=x_axis, y_axis=y_axis, tooltip_format=tooltip_format, **kwargs)


class HighChartsHeatMap(HighChartsObjectBase):
    """
    Heat Map

    Displays as a heat map.

    Attributes
    """

    def __init__(self, series=[], title='', subtitle='', x_categories=[], y_categories=[], tooltip_phrase_one='',
                 tooltip_phrase_two='', **kwargs):
        """
        Constructor

        Args:
        """
        chart = {
            'type': 'heatmap',
            'marginTop': 40,
            'marginBottom': 80
        }

        x_axis = {
            'categories': x_categories
        }

        y_axis = {
            'categories': y_categories,
            'title': 'null'
        }

        tooltip_format = {
            'formatter': 'function() {return "<b>" + this.series.xAxis.categories[this.point.x] + "</b> %s <br><b>" + this.point.value + "</b> %s <br><b>" + this.series.yAxis.categories[this.point.y] + "</b>";' % (tooltip_phrase_one, tooltip_phrase_two)
        }

        # Initialize super class
        super(HighChartsHeatMap, self).__init__(chart=chart, title=title, subtitle=subtitle, series=series, x_axis=x_axis, y_axis=y_axis, tooltip_format=tooltip_format, **kwargs)