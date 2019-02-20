# coding=utf-8
from .base import TethysGizmoOptions

__all__ = ['PlotObject', 'LinePlot', 'PolarPlot', 'ScatterPlot',
           'PiePlot', 'BarPlot', 'TimeSeries', 'AreaRange', 'HeatMap']


class PlotViewBase(TethysGizmoOptions):
    """
    Plot view classes inherit from this class.
    """
    gizmo_name = "plot_view"

    def __init__(self, width='500px', height='500px', engine='d3'):
        """
        Constructor
        """
        # Initialize the super class
        super().__init__()

        self.width = width
        self.height = height

        if engine not in ('d3', 'highcharts'):
            raise ValueError('Parameter "engine" must be either "d3" or "highcharts".')

        self.engine = engine
        self.plot_object = PlotObject()

    @staticmethod
    def get_vendor_js():
        """
        JavaScript vendor libraries to be placed in the
        {% block global_scripts %} block
        """
        return ('tethys_gizmos/vendor/highcharts/js/highcharts.js',
                'tethys_gizmos/vendor/highcharts/js/highcharts-more.js',
                'tethys_gizmos/vendor/highcharts/js/modules/exporting.js',
                'https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.5/d3.min.js',
                'tethys_gizmos/vendor/d3_tooltip/d3.tip.v0.6.3.js')

    @staticmethod
    def get_gizmo_js():
        """
        JavaScript specific to gizmo to be placed in the
        {% block scripts %} block
        """
        return ('tethys_gizmos/js/plot_view.js',)

    @staticmethod
    def get_gizmo_css():
        """
        CSS specific to gizmo to be placed in the
        {% block content_dependent_styles %} block
        """
        return ('tethys_gizmos/css/plot_view.css',)


class PlotObject(TethysGizmoOptions):
    """
    Base Plot Object that is constructed by plot views.
    """

    def __init__(self, chart={}, title='', subtitle='', legend=None, display_legend=True,
                 tooltip=True, x_axis={}, y_axis={}, tooltip_format={}, plotOptions={}, **kwargs):
        """
        Constructor
        """
        # Initialize super class
        super().__init__()

        self.chart = chart
        self.xAxis = x_axis
        self.yAxis = y_axis
        self.plotOptions = plotOptions

        if title != '':
            self.title = {'text': title}

        if subtitle != '':
            self.subtitle = {'text': subtitle}

        if display_legend:
            default_legend = {
                'layout': 'vertical',
                'align': 'right',
                'verticalAlign': 'middle',
                'borderWidth': 0
            }
            self.legend = legend or default_legend

        if tooltip:
            self.tooltip = tooltip_format

        # add any other attributes the user wants
        for key, value in kwargs.items():
            setattr(self, key, value)


class LinePlot(PlotViewBase):
    """
    Used to create line plot visualizations.

    Attributes:
        series(list, required): A list of  series dictionaries.
        height(str): Height of the plot element. Any valid css unit of length.
        width(str): Width of the plot element. Any valid css unit of length.
        engine(str): The plot engine to be used for rendering, either 'd3' or 'highcharts'. Defaults to 'd3'.
        title(str): Title of the plot.
        subtitle(str): Subtitle of the plot.
        spline(bool): If True, lines are smoothed using a spline technique.
        x_axis_title(str): Title of the x-axis.
        x_axis_units(str): Units of the x-axis.
        y_axis_title(str): Title of the y-axis.
        y_axis_units(str): Units of the y-axis.

    **Controller Example**

    ::

        from tethys_sdk.gizmos import LinePlot

        line_plot_view = LinePlot(
            height='500px',
            width='500px',
            engine='highcharts',
            title='Plot Title',
            subtitle='Plot Subtitle',
            spline=True,
            x_axis_title='Altitude',
            x_axis_units='km',
            y_axis_title='Temperature',
            y_axis_units='°C',
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

        context = {
                    'line_plot_view': line_plot_view,
                  }

    **Template Example**

    ::

        {% load tethys_gizmos %}

        {% gizmo line_plot_view %}

    """

    def __init__(self, series, height='500px', width='500px', engine='d3', title='', subtitle='', spline=False,
                 x_axis_title='', x_axis_units='', y_axis_title='', y_axis_units='', **kwargs):
        """
        Constructor
        """
        # Initialize super class
        super().__init__(height=height, width=width, engine=engine)

        chart = kwargs.pop('chart', None)

        if not chart:
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

        # Initialize the plot view object
        self.plot_object = PlotObject(chart=chart, title=title, subtitle=subtitle, series=series,
                                      x_axis=x_axis, y_axis=y_axis, tooltip_format=tooltip_format, **kwargs)


class PolarPlot(PlotViewBase):
    """
    Use to create a  polar plot visualization.

    Attributes:
        series(list, required): A list of  series dictionaries.
        height(str): Height of the plot element. Any valid css unit of length.
        width(str): Width of the plot element. Any valid css unit of length.
        engine(str): The plot engine to be used for rendering, either 'd3' or 'highcharts'. Defaults to 'd3'.
        title(str): Title of the plot.
        subtitle(str): Subtitle of the plot.
        categories(list): List of category names, one for each data point in the series.

    **Controller Example**

    ::

        from tethys_sdk.gizmos import PolarPlot

        web_plot = PolarPlot(
            height='500px',
            width='500px',
            engine='highcharts',
            title='Polar Chart',
            subtitle='Polar Chart',
            pane={
              'size': '80%'
            },
            categories=['Infiltration', 'Soil Moisture', 'Precipitation', 'Evaporation',
                      'Roughness', 'Runoff', 'Permeability', 'Vegetation'],
            series=[
              {
                  'name': 'Park City',
                  'data': [0.2, 0.5, 0.1, 0.8, 0.2, 0.6, 0.8, 0.3],
                  'pointPlacement': 'on'
              },
              {
                  'name': 'Little Dell',
                  'data': [0.8, 0.3, 0.2, 0.5, 0.1, 0.8, 0.2, 0.6],
                  'pointPlacement': 'on'
              }
            ]
        )

        context = {
                    'web_plot': web_plot,
                  }

    **Template Example**

    ::

        {% load tethys_gizmos %}

        {% gizmo web_plot %}

    """

    def __init__(self, series=[], height='500px', width='500px', engine='d3', title='', subtitle='', categories=[],
                 **kwargs):
        """
        Constructor
        """
        # Initialize super class
        super().__init__(height=height, width=width, engine=engine)

        chart = kwargs.pop('chart', None)
        x_axis = kwargs.pop('x_axis', None)
        y_axis = kwargs.pop('y_axis', None)

        if not chart:
            chart = {
                'polar': True,
                'type': 'line'
            }

        if not x_axis:
            x_axis = {
                'categories': categories,
                'tickmarkPlacement': 'on',
                'lineWidth': 0
            }

        if not y_axis:
            y_axis = {
                'gridLineInterpolation': 'polygon',
                'lineWidth': 0,
                'min': 0
            }

        # Initialize super class
        self.plot_object = PlotObject(chart=chart, title=title, subtitle=subtitle, series=series,
                                      x_axis=x_axis, y_axis=y_axis, **kwargs)


class ScatterPlot(PlotViewBase):
    """
    Use to create a  scatter plot visualization.

    Attributes:
        series(list, required): A list of  series dictionaries.
        height(str): Height of the plot element. Any valid css unit of length.
        width(str): Width of the plot element. Any valid css unit of length.
        engine(str): The plot engine to be used for rendering, either 'd3' or 'highcharts'. Defaults to 'd3'.
        title(str): Title of the plot.
        subtitle(str): Subtitle of the plot.
        spline(bool): If True, lines are smoothed using a spline technique.
        x_axis_title(str): Title of the x-axis.
        x_axis_units(str): Units of the x-axis.
        y_axis_title(str): Title of the y-axis.
        y_axis_units(str): Units of the y-axis.

    **Controller Example**

    ::

        from tethys_sdk.gizmos import ScatterPlot

        male_dataset = {
            'name': 'Male',
            'color': '#0066ff',
            'data': [
                [174.0, 65.6], [175.3, 71.8], [193.5, 80.7], [186.5, 72.6],
                [187.2, 78.8], [181.5, 74.8], [184.0, 86.4], [184.5, 78.4],
                [175.0, 62.0], [184.0, 81.6], [180.0, 76.6], [177.8, 83.6],
                [192.0, 90.0], [176.0, 74.6], [174.0, 71.0], [184.0, 79.6],
                [192.7, 93.8], [171.5, 70.0], [173.0, 72.4], [176.0, 85.9],
                [176.0, 78.8], [180.5, 77.8], [172.7, 66.2], [176.0, 86.4],
                [173.5, 81.8], [178.0, 89.6], [180.3, 82.8], [180.3, 76.4],
                [164.5, 63.2], [173.0, 60.9], [183.5, 74.8], [175.5, 70.0],
                [188.0, 72.4], [189.2, 84.1], [172.8, 69.1], [170.0, 59.5],
                [182.0, 67.2], [170.0, 61.3], [177.8, 68.6], [184.2, 80.1],
                [186.7, 87.8], [171.4, 84.7], [172.7, 73.4], [175.3, 72.1],
                [180.3, 82.6], [182.9, 88.7], [188.0, 84.1], [177.2, 94.1],
                [172.1, 74.9], [167.0, 59.1], [169.5, 75.6], [174.0, 86.2],
                [172.7, 75.3], [182.2, 87.1], [164.1, 55.2], [163.0, 57.0],
                [171.5, 61.4], [184.2, 76.8], [174.0, 86.8], [174.0, 72.2],
                [177.0, 71.6], [186.0, 84.8], [167.0, 68.2], [171.8, 66.1]
            ]
        }

        female_dataset = {
            'name': 'Female',
            'color': '#ff6600',
            'data': [
                [161.2, 51.6], [167.5, 59.0], [159.5, 49.2], [157.0, 63.0],
                [155.8, 53.6], [170.0, 59.0], [159.1, 47.6], [166.0, 69.8],
                [176.2, 66.8], [160.2, 75.2], [172.5, 55.2], [170.9, 54.2],
                [172.9, 62.5], [153.4, 42.0], [160.0, 50.0], [147.2, 49.8],
                [168.2, 49.2], [175.0, 73.2], [157.0, 47.8], [167.6, 68.8],
                [159.5, 50.6], [175.0, 82.5], [166.8, 57.2], [176.5, 87.8],
                [170.2, 72.8], [174.0, 54.5], [173.0, 59.8], [179.9, 67.3],
                [170.5, 67.8], [160.0, 47.0], [154.4, 46.2], [162.0, 55.0],
                [176.5, 83.0], [160.0, 54.4], [152.0, 45.8], [162.1, 53.6],
                [170.0, 73.2], [160.2, 52.1], [161.3, 67.9], [166.4, 56.6],
                [168.9, 62.3], [163.8, 58.5], [167.6, 54.5], [160.0, 50.2],
                [161.3, 60.3], [167.6, 58.3], [165.1, 56.2], [160.0, 50.2],
                [170.0, 72.9], [157.5, 59.8], [167.6, 61.0], [160.7, 69.1],
                [163.2, 55.9], [152.4, 46.5], [157.5, 54.3], [168.3, 54.8],
                [180.3, 60.7], [165.5, 60.0], [165.0, 62.0], [164.5, 60.3]
            ]
        }

        scatter_plot_view = ScatterPlot(
            width='500px',
            height='500px',
            engine='highcharts',
            title='Scatter Plot',
            subtitle='Scatter Plot',
            x_axis_title='Height',
            x_axis_units='cm',
            y_axis_title='Weight',
            y_axis_units='kg',
            series=[
                male_dataset,
                female_dataset
            ]
        )

        context = {
                    'scatter_plot_view': scatter_plot_view,
                  }

    **Template Example**

    ::

        {% load tethys_gizmos %}

        {% gizmo scatter_plot_view %}

    """

    def __init__(self, series=[], height='500px', width='500px', engine='d3', title='', subtitle='',
                 x_axis_title='', x_axis_units='', y_axis_title='', y_axis_units='', **kwargs):
        """
        Constructor
        """
        # Initialize super class
        super().__init__(height=height, width=width, engine=engine)

        chart = kwargs.pop('chart', None)

        if not chart:
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
        self.plot_object = PlotObject(chart=chart, title=title, subtitle=subtitle, series=series,
                                      x_axis=x_axis, y_axis=y_axis, tooltip_format=tooltip_format, **kwargs)


class PiePlot(PlotViewBase):
    """
    Use to create a  pie plot visualization.

    Attributes:
        series(list, required): A list of  series dictionaries.
        height(str): Height of the plot element. Any valid css unit of length.
        width(str): Width of the plot element. Any valid css unit of length.
        engine(str): The plot engine to be used for rendering, either 'd3' or 'highcharts'. Defaults to 'd3'.
        title(str): Title of the plot.
        subtitle(str): Subtitle of the plot.

    **Controller Example**

    ::

        from tethys_sdk.gizmos import PieChart

        pie_plot_view = PiePlot(
            height='500px',
            width='500px',
            engine='highcharts',
            title='Pie Chart',
            subtitle='Pie Chart',
            series=[
                  {'name': 'Firefox', 'value': 45.0},
                  {'name': 'IE', 'value': 26.8},
                  {'name': 'Chrome', 'value': 12.8},
                  {'name': 'Safari', 'value': 8.5},
                  {'name': 'Opera', 'value': 8.5},
                  {'name': 'Others', 'value': 0.7}
            ]
        )

        context = {
                    'pie_plot_view': pie_plot_view,
                  }

    **Template Example**

    ::

        {% load tethys_gizmos %}

        {% gizmo pie_plot_view %}

    """

    def __init__(self, series=[], height='500px', width='500px', engine='d3', title='', subtitle='', **kwargs):
        """
        Constructor

        Args:
        """
        # Initialize super class
        super().__init__(height=height, width=width, engine=engine)

        chart = kwargs.pop('chart', None)

        if not chart:
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
        self.plot_object = PlotObject(chart=chart, title=title, subtitle=subtitle, series=series,
                                      plotOptions=plotOptions, tooltip_format=tooltip_format, **kwargs)


class BarPlot(PlotViewBase):
    """
    Bar Plot

    Displays as either a bar or column chart.

    Attributes:
        series(list, required): A list of  series dictionaries.
        height(str): Height of the plot element. Any valid css unit of length.
        width(str): Width of the plot element. Any valid css unit of length.
        engine(str): The plot engine to be used for rendering, either 'd3' or 'highcharts'. Defaults to 'd3'.
        title(str): Title of the plot.
        subtitle(str): Subtitle of the plot.
        horizontal(bool): If True, bars are displayed horizontally, otherwise they are displayed vertically.
        categories(list): A list of category titles, one for each bar.
        axis_title(str): Title of the axis.
        axis_units(str): Units of the axis.
        y_min(int,float): Minimum value of y axis.

    **Controller Example**

    ::

        from tethys_sdk.gizmos import BarPlot

        bar_plot_view = BarPlot(
            height='500px',
            width='500px',
            engine='highcharts',
            title='Bar Chart',
            subtitle='Bar Chart',
            vertical=True,
            categories=[
                'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
            ],
            axis_units='millions',
            axis_title='Population',
            series=[{
                    'name': "Year 1800",
                    'data': [100, 31, 635, 203, 275, 487, 872, 671, 736, 568, 487, 432]
                }, {
                    'name': "Year 1900",
                    'data': [133, 200, 947, 408, 682, 328, 917, 171, 482, 140, 176, 237]
                }, {
                    'name': "Year 2000",
                    'data': [764, 628, 300, 134, 678, 200, 781, 571, 773, 192, 836, 172]
                }, {
                    'name': "Year 2008",
                    'data': [973, 914, 500, 400, 349, 108, 372, 726, 638, 927, 621, 364]
                }
            ]
        )

        context = {
                    'bar_plot_view': bar_plot_view,
                  }

    **Template Example**

    ::

        {% load tethys_gizmos %}

        {% gizmo bar_plot_view %}

    """

    def __init__(self, series=[], height='500px', width='500px', engine='d3', title='', subtitle='',
                 horizontal=False, categories=[], axis_title='', axis_units='', group_tools=True,
                 y_min=0, **kwargs):
        """
        Constructor
        """
        # Initialize super class
        super().__init__(height=height, width=width, engine=engine)

        chart = kwargs.pop('chart', None)
        y_axis = kwargs.pop('y_axis', None)

        if not chart:
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

        if not y_axis:
            if axis_units:
                y_axis = {
                    'min': y_min,
                    'title': {
                        'text': '{0} ({1})'.format(axis_title, axis_units)
                    }
                }

            else:
                y_axis = {
                    'min': y_min,
                    'title': {
                        'text': axis_title
                    }
                }

        if group_tools:
            tooltip_format = {
                'headerFormat': '<span style="font-size:10px">{point.key}</span><table>',
                'pointFormat': '<tr><td style="color:{series.color};padding:0">{series.name}: </td>'
                               + '<td style="padding:0"><b>{point.y:.1f} %s </b></td></tr>' % (axis_units),
                'footerFormat': '</table>',
                'shared': True,
                'useHTML': True
            }

        # Initialize super class
        self.plot_object = PlotObject(chart=chart, title=title, subtitle=subtitle, series=series,
                                      plotOptions=plotOptions, tooltip_format=tooltip_format, x_axis=x_axis,
                                      y_axis=y_axis, **kwargs)


class TimeSeries(PlotViewBase):
    """
    Use to create a timeseries plot visualization

    Attributes:
        series(list, required): A list of  series dictionaries.
        height(str): Height of the plot element. Any valid css unit of length.
        width(str): Width of the plot element. Any valid css unit of length.
        engine(str): The plot engine to be used for rendering, either 'd3' or 'highcharts'. Defaults to 'd3'.
        title(str): Title of the plot.
        subtitle(str): Subtitle of the plot.
        y_axis_title(str): Title of the axis.
        y_axis_units(str): Units of the axis.

    **Controller Example**

    ::

        from tethys_sdk.gizmos import TimeSeries

        timeseries_plot = TimeSeries(
            height='500px',
            width='500px',
            engine='highcharts',
            title='Irregular Timeseries Plot',
            y_axis_title='Snow depth',
            y_axis_units='m',
            series=[{
                'name': 'Winter 2007-2008',
                'data': [
                    [datetime(2008, 12, 2), 0.8],
                    [datetime(2008, 12, 9), 0.6],
                    [datetime(2008, 12, 16), 0.6],
                    [datetime(2008, 12, 28), 0.67],
                    [datetime(2009, 1, 1), 0.81],
                    [datetime(2009, 1, 8), 0.78],
                    [datetime(2009, 1, 12), 0.98],
                    [datetime(2009, 1, 27), 1.84],
                    [datetime(2009, 2, 10), 1.80],
                    [datetime(2009, 2, 18), 1.80],
                    [datetime(2009, 2, 24), 1.92],
                    [datetime(2009, 3, 4), 2.49],
                    [datetime(2009, 3, 11), 2.79],
                    [datetime(2009, 3, 15), 2.73],
                    [datetime(2009, 3, 25), 2.61],
                    [datetime(2009, 4, 2), 2.76],
                    [datetime(2009, 4, 6), 2.82],
                    [datetime(2009, 4, 13), 2.8],
                    [datetime(2009, 5, 3), 2.1],
                    [datetime(2009, 5, 26), 1.1],
                    [datetime(2009, 6, 9), 0.25],
                    [datetime(2009, 6, 12), 0]
                ]
            }]
        )

        context = {
                    'timeseries_plot': timeseries_plot,
                  }

    **Template Example**

    ::

        {% load tethys_gizmos %}

        {% gizmo timeseries_plot %}
    """

    def __init__(self, series=[], height='500px', width='500px', engine='d3', title='', subtitle='', y_axis_title='',
                 y_axis_units='', y_min=0, **kwargs):
        """
        Constructor
        """
        # Initialize super class
        super().__init__(height=height, width=width, engine=engine)

        chart = kwargs.pop('chart', None)
        x_axis = kwargs.pop('x_axis', None)
        y_axis = kwargs.pop('y_axis', None)

        if not chart:
            chart = {
                'type': 'area',
                'zoomType': 'x'
            }

        if not x_axis:
            x_axis = {
                'type': 'datetime'
            }

        if not y_axis:
            y_axis = {
                'title': {
                    'text': '{0} ({1})'.format(y_axis_title, y_axis_units)
                },
                'min': y_min
            }

        tooltip_format = {
            'pointFormat': '{point.y} %s' % (y_axis_units)
        }

        # Initialize super class
        self.plot_object = PlotObject(chart=chart, title=title, subtitle=subtitle, series=series,
                                      x_axis=x_axis, y_axis=y_axis, tooltip_format=tooltip_format, **kwargs)


class AreaRange(PlotViewBase):
    """
    Use to create a area range plot visualization.

    Attributes:
        series(list, required): A list of  series dictionaries.
        height(str): Height of the plot element. Any valid css unit of length.
        width(str): Width of the plot element. Any valid css unit of length.
        engine(str): The plot engine to be used for rendering, either 'd3' or 'highcharts'. Defaults to 'd3'.
        title(str): Title of the plot.
        subtitle(str): Subtitle of the plot.
        y_axis_title(str): Title of the axis.
        y_axis_units(str): Units of the axis.

    **Controller Example**

    ::

        from tethys_sdk.gizmos import AreaRange

        averages = [
            [datetime(2009, 7, 1), 21.5], [datetime(2009, 7, 2), 22.1], [datetime(2009, 7, 3), 23],
            [datetime(2009, 7, 4), 23.8], [datetime(2009, 7, 5), 21.4], [datetime(2009, 7, 6), 21.3],
            [datetime(2009, 7, 7), 18.3], [datetime(2009, 7, 8), 15.4], [datetime(2009, 7, 9), 16.4],
            [datetime(2009, 7, 10), 17.7], [datetime(2009, 7, 11), 17.5], [datetime(2009, 7, 12), 17.6],
            [datetime(2009, 7, 13), 17.7], [datetime(2009, 7, 14), 16.8], [datetime(2009, 7, 15), 17.7],
            [datetime(2009, 7, 16), 16.3], [datetime(2009, 7, 17), 17.8], [datetime(2009, 7, 18), 18.1],
            [datetime(2009, 7, 19), 17.2], [datetime(2009, 7, 20), 14.4],
            [datetime(2009, 7, 21), 13.7], [datetime(2009, 7, 22), 15.7], [datetime(2009, 7, 23), 14.6],
            [datetime(2009, 7, 24), 15.3], [datetime(2009, 7, 25), 15.3], [datetime(2009, 7, 26), 15.8],
            [datetime(2009, 7, 27), 15.2], [datetime(2009, 7, 28), 14.8], [datetime(2009, 7, 29), 14.4],
            [datetime(2009, 7, 30), 15], [datetime(2009, 7, 31), 13.6]
        ]

        ranges = [
            [datetime(2009, 7, 1), 14.3, 27.7], [datetime(2009, 7, 2), 14.5, 27.8], [datetime(2009, 7, 3), 15.5, 29.6],
            [datetime(2009, 7, 4), 16.7, 30.7], [datetime(2009, 7, 5), 16.5, 25.0], [datetime(2009, 7, 6), 17.8, 25.7],
            [datetime(2009, 7, 7), 13.5, 24.8], [datetime(2009, 7, 8), 10.5, 21.4], [datetime(2009, 7, 9), 9.2, 23.8],
            [datetime(2009, 7, 10), 11.6, 21.8], [datetime(2009, 7, 11), 10.7, 23.7], [datetime(2009, 7, 12), 11.0, 23.3],
            [datetime(2009, 7, 13), 11.6, 23.7], [datetime(2009, 7, 14), 11.8, 20.7], [datetime(2009, 7, 15), 12.6, 22.4],
            [datetime(2009, 7, 16), 13.6, 19.6], [datetime(2009, 7, 17), 11.4, 22.6], [datetime(2009, 7, 18), 13.2, 25.0],
            [datetime(2009, 7, 19), 14.2, 21.6], [datetime(2009, 7, 20), 13.1, 17.1], [datetime(2009, 7, 21), 12.2, 15.5],
            [datetime(2009, 7, 22), 12.0, 20.8], [datetime(2009, 7, 23), 12.0, 17.1], [datetime(2009, 7, 24), 12.7, 18.3],
            [datetime(2009, 7, 25), 12.4, 19.4], [datetime(2009, 7, 26), 12.6, 19.9], [datetime(2009, 7, 27), 11.9, 20.2],
            [datetime(2009, 7, 28), 11.0, 19.3], [datetime(2009, 7, 29), 10.8, 17.8], [datetime(2009, 7, 30), 11.8, 18.5],
            [datetime(2009, 7, 31), 10.8, 16.1]
        ]

        area_range_plot_object = AreaRange(
            title='July Temperatures',
            y_axis_title='Temperature',
            y_axis_units='*C',
            width='500px',
            height='500px',
            series=[{
                'name': 'Temperature',
                'data': averages,
                'zIndex': 1,
                'marker': {
                    'lineWidth': 2,
                }
            }, {
                'name': 'Range',
                'data': ranges,
                'type': 'arearange',
                'lineWidth': 0,
                'linkedTo': ':previous',
                'fillOpacity': 0.3,
                'zIndex': 0
            }]
        )


        context = {
                    'area_range_plot_object': area_range_plot_object,
                  }

    **Template Example**

    ::

        {% load tethys_gizmos %}

        {% gizmo area_range_plot_object %}

    """  # noqa: E501

    def __init__(self, series=[], height='500px', width='500px', engine='d3', title='', subtitle='',
                 y_axis_title='', y_axis_units='', **kwargs):
        """
        Constructor
        """
        # Initialize super class
        super().__init__(height=height, width=width, engine=engine)

        chart = kwargs.pop('chart', None)
        x_axis = kwargs.pop('x_axis', None)
        y_axis = kwargs.pop('y_axis', None)

        if not chart:
            chart = {
            }

        if not x_axis:
            x_axis = {
                'type': 'datetime'
            }

        if not y_axis:
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
        self.plot_object = PlotObject(chart=chart, title=title, subtitle=subtitle, series=series,
                                      x_axis=x_axis, y_axis=y_axis, tooltip_format=tooltip_format, **kwargs)


class HeatMap(PlotViewBase):
    """
    Use to create a  heat map visualization.

    Attributes:
        series(list, required): A list of  series dictionaries.
        height(str): Height of the plot element. Any valid css unit of length.
        width(str): Width of the plot element. Any valid css unit of length.
        engine(str): The plot engine to be used for rendering, either 'd3' or 'highcharts'. Defaults to 'd3'.
        title(str): Title of the plot.
        subtitle(str): Subtitle of the plot.
        x_categories(list):
        y_categories(list):
        tooltip_phrase_one(str):
        tooltip_phrase_two(str):

    **Controller Example**

    ::

        from tethys_sdk.gizmos import HeatMap

        sales_data = [
            [0, 0, 10], [0, 1, 19], [0, 2, 8], [0, 3, 24], [0, 4, 67], [1, 0, 92],
            [1, 1, 58], [1, 2, 78], [1, 3, 117], [1, 4, 48], [2, 0, 35], [2, 1, 15],
            [2, 2, 123], [2, 3, 64], [2, 4, 52], [3, 0, 72], [3, 1, 132], [3, 2, 114],
            [3, 3, 19], [3, 4, 16], [4, 0, 38], [4, 1, 5], [4, 2, 8], [4, 3, 117],
            [4, 4, 115], [5, 0, 88], [5, 1, 32], [5, 2, 12], [5, 3, 6], [5, 4, 120],
            [6, 0, 13], [6, 1, 44], [6, 2, 88], [6, 3, 98], [6, 4, 96], [7, 0, 31],
            [7, 1, 1], [7, 2, 82], [7, 3, 32], [7, 4, 30], [8, 0, 85], [8, 1, 97],
            [8, 2, 123], [8, 3, 64], [8, 4, 84], [9, 0, 47], [9, 1, 114], [9, 2, 31],
            [9, 3, 48], [9, 4, 91]
        ]

        heat_map_plot = HeatMap(
            width='500px',
            height='500px',
            title='Sales per employee per weekday',
            x_categories=['Alexander', 'Marie', 'Maximilian', 'Sophia', 'Lukas', 'Maria', 'Leon', 'Anna', 'Tim', 'Laura'],
            y_categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
            tooltip_phrase_one='sold',
            tooltip_phrase_two='items on',
            colorAxis={
                'min': 0,
                'minColor': '#FFFFFF',
                'maxColor': '.getOptions().colors[0]'
            },
            legend={
                'align': 'right',
                'layout': 'vertical',
                'margin': 0,
                'verticalAlign': 'top',
                'y': 25,
                'symbolHeight': 280
            },
            series=[{
                        'name': 'Sales per employee',
                        'borderWidth': 1,
                        'data': sales_data,
                        'dataLabels': {
                            'enabled': True,
                            'color': '#000000'
                        }
                    }]
        )


        context = {
                    'heat_map_plot': heat_map_plot,
                  }

    **Template Example**

    ::

        {% load tethys_gizmos %}

        {% gizmo heat_map_plot %}

    """  # noqa: E501

    def __init__(self, series=[], height='500px', width='500px', engine='d3', title='', subtitle='', x_categories=[],
                 y_categories=[], tooltip_phrase_one='', tooltip_phrase_two='', **kwargs):
        """
        Constructor
        """
        # Initialize super class
        super().__init__(height=height, width=width, engine=engine)

        chart = kwargs.pop('chart', None)

        if not chart:
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
            'formatter': 'function() {return "<b>" + this.series.xAxis.categories[this.point.x] + "</b> %s <br><b>" + '
                         'this.point.value + "</b> %s <br><b>" + this.series.yAxis.categories[this.point.y] + "</b>";'
                         % (tooltip_phrase_one, tooltip_phrase_two)
        }

        # Initialize super class
        self.plot_object = PlotObject(chart=chart, title=title, subtitle=subtitle, series=series, x_axis=x_axis,
                                      y_axis=y_axis, tooltip_format=tooltip_format, **kwargs)
