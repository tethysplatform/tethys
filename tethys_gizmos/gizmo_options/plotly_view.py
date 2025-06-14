# coding=utf-8
from .base import TethysGizmoOptions
from tethys_portal.optional_dependencies import optional_import

# optional imports
opy = optional_import("plotly.offline")

__all__ = ["PlotlyView"]


class PlotlyView(TethysGizmoOptions):
    """
    Simple options object for plotly view.

    .. note:: Information about the Plotly API can be found at https://plotly.com/python/.

    Attributes:
        plot_input(plotly graph_objs): A plotly graph_objs to be plotted.
        height(Optional[str]): Height of the plot element. Any valid css unit of length.
        width(Optional[str]): Width of the plot element. Any valid css unit of length.
        attributes(Optional[dict]): Dictionary of attributed to add to the outer div.
        classes(Optional[str]): Space separated string of classes to add to the outer div.
        hidden(Optional[bool]): If True, the plot will be hidden. Default is False.
        show_link(Optional[bool]): If True, the link to export plot to view in plotly is shown. Default is False.

    Controller Code Basic Example::

        from datetime import datetime
        import plotly.graph_objs as go
        from tethys_sdk.gizmos import PlotlyView

        x = [datetime(year=2013, month=10, day=04),
             datetime(year=2013, month=11, day=05),
             datetime(year=2013, month=12, day=06)]

        my_plotly_view = PlotlyView([go.Scatter(x=x, y=[1, 3, 6])])

        context = {'plotly_view_input': my_plotly_view}

    Controller Code Pandas Example::

        import numpy as np
        import pandas as pd
        from tethys_sdk.gizmos import PlotlyView

        df = pd.DataFrame(np.random.randn(1000, 2), columns=['A', 'B']).cumsum()

        my_plotly_view = PlotlyView(df.iplot(asFigure=True))

        context = {'plotly_view_input': my_plotly_view}

    Template Code::

        {% load tethys_gizmos %}

        {% gizmo plotly_view_input %}

    More examples::

        import numpy as np
        import pandas as pd

        np.random.seed(1)

        # Scatter
        scatter_plot = PlotlyView([
            go.Scatter(
                y=np.random.randn(500),
                mode='markers',
                marker=dict(
                    size=16,
                    color=np.random.randn(500), #set color equal to a variable
                    colorscale='Viridis', # one of plotly colorscales
                    showscale=True
                )
            )
        ])

        # Line
        N = 100
        random_x = np.linspace(0, 1, N)
        random_y0 = np.random.randn(N) + 5
        random_y1 = np.random.randn(N)
        random_y2 = np.random.randn(N) - 5

        line_plot = PlotlyView([
            go.Scatter(
                x=random_x, y=random_y0,
                mode='markers',
                name='markers'
            ),
            go.Scatter(
                x=random_x, y=random_y1,
                mode='lines+markers',
                name='lines+markers'
            ),
            go.Scatter(
                x=random_x, y=random_y2,
                mode='lines',
                name='lines'
            )
        ])

        # Pie
        pie_plot = PlotlyView([
            go.Pie(
                labels=['Oxygen','Hydrogen','Carbon_Dioxide','Nitrogen'],
                values=[4500, 2500, 1053, 500]
            )
        ])

        # Bar
        years = [1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003,
                 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=years,
            y=[219, 146, 112, 127, 124, 180, 236, 207, 236, 263,
                350, 430, 474, 526, 488, 537, 500, 439],
            name='Rest of world',
            marker_color='rgb(55, 83, 109)'
        ))
        fig.add_trace(go.Bar(
            x=years,
            y=[16, 13, 10, 11, 28, 37, 43, 55, 56, 88, 105, 156, 270,
                299, 340, 403, 549, 499],
            name='China',
            marker_color='rgb(26, 118, 255)'
        ))
        fig.update_layout(
            title='US Export of Plastic Scrap',
            xaxis_tickfont_size=14,
            yaxis=dict(
                title='USD (millions)',
                titlefont_size=16,
                tickfont_size=14,
            ),
            legend=dict(
                x=0,
                y=1.0,
                bgcolor='rgba(255, 255, 255, 0)',
                bordercolor='rgba(255, 255, 255, 0)'
            ),
            barmode='group',
            bargap=0.15, # gap between bars of adjacent location coordinates.
            bargroupgap=0.1 # gap between bars of the same location coordinate.
        )
        bar_chart = PlotlyView(fig)

        # Time series
        timeseries_df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')
        timeseries_fig = px.line(
            timeseries_df,
            x='Date',
            y='AAPL.High',
            title='Time Series with Range Slider and Selectors'
        )

        timeseries_fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        time_series_plot = PlotlyView(timeseries_fig)

        # Heat map
        heat_x = np.random.randn(500)
        heat_y = np.random.randn(500)+1

        heat_fig = go.Figure(go.Histogram2d(
            x=heat_x,
            y=heat_y
        ))
        heat_map = PlotlyView(heat_fig)

        context = {
            'scatter_plot': scatter_plot,
            'line_plot': line_plot,
            'pie_plot': pie_plot,
            'bar_chart': bar_chart,
            'time_series_plot': time_series_plot,
            'heat_map': heat_map,
        }

    Template Code::

        {% load tethys_gizmos %}

        {% gizmo scatter_plot %}
        {% gizmo line_plot %}
        {% gizmo pie_plot %}
        {% gizmo bar_chart %}
        {% gizmo time_series_plot %}
        {% gizmo heat_map %}

    """

    gizmo_name = "plotly_view"

    def __init__(
        self,
        plot_input,
        height=None,
        width="100%",
        attributes="",
        classes="",
        divid="",
        hidden=False,
        show_link=False,
    ):
        """
        Constructor
        """
        # Initialize the super class
        super().__init__()

        self.plotly_div = opy.plot(
            plot_input,
            auto_open=False,
            output_type="div",
            include_plotlyjs=False,
            show_link=show_link,
        )
        self.height = height
        self.width = width
        self.attributes = attributes
        self.classes = classes
        self.divid = divid
        self.hidden = hidden

    @staticmethod
    def get_vendor_js():
        """
        JavaScript vendor libraries to be placed in the
        {% block global_scripts %} block
        """
        return ("://plotly-load_from_python.js",)
