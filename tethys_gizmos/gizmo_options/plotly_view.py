# coding=utf-8
import plotly.offline as opy

from .base import TethysGizmoOptions

__all__ = ['PlotlyView']


class PlotlyView(TethysGizmoOptions):
    """
    Simple options object for plotly view.

    .. note:: Information about the Plotly API can be found at https://plot.ly/python.

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
    """
    gizmo_name = "plotly_view"

    def __init__(self, plot_input, height='520px', width='100%',
                 attributes='', classes='', divid='', hidden=False,
                 show_link=False):
        """
        Constructor
        """
        # Initialize the super class
        super().__init__()

        self.plotly_div = opy.plot(plot_input,
                                   auto_open=False,
                                   output_type='div',
                                   include_plotlyjs=False,
                                   show_link=show_link)
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
        return ('://plotly-load_from_python.js',)
