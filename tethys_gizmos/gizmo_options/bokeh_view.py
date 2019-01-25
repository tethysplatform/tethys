# coding=utf-8
from bokeh.embed import components
from bokeh.resources import CDN

from .base import TethysGizmoOptions

__all__ = ['BokehView']


class BokehView(TethysGizmoOptions):
    """
    Simple options object for Bokeh plotting.

    .. note:: For more information about Bokeh and for Python examples, see http://bokeh.pydata.org.

    Attributes:
        plot_input(bokeh figure): A bokeh figure to be plotted.
        height(Optional[str]): Height of the plot element. Any valid css unit of length.
        width(Optional[str]): Width of the plot element. Any valid css unit of length.
        attributes(Optional[dict]): Dictionary of attributed to add to the outer div.
        classes(Optional[str]): Space separated string of classes to add to the outer div.
        hidden(Optional[bool]): If True, the plot will be hidden. Default is False.

    Controller Code Example::

        from tethys_sdk.gizmos import BokehView
        from bokeh.plotting import figure

        plot = figure(plot_height=300)
        plot.circle([1,2], [3,4])
        my_bokeh_view = BokehView(plot, height="300px")

        context = {'bokeh_view_input': my_bokeh_view}

    Template Code Example::

        {% load tethys_gizmos %}

        {% gizmo bokeh_view_input %}
    """
    gizmo_name = "bokeh_view"

    def __init__(self, plot_input, height='520px', width='100%',
                 attributes='', classes='', divid='', hidden=False):
        """
        Constructor
        """
        # Initialize the super class
        super().__init__(attributes, classes)
        self.script, self.div = components(plot_input)
        self.height = height
        self.width = width
        self.divid = divid
        self.hidden = hidden

    @staticmethod
    def get_vendor_css():
        """
        JavaScript vendor libraries to be placed in the
        {% block global_scripts %} block
        """
        return CDN.css_files

    @staticmethod
    def get_vendor_js():
        """
        JavaScript vendor libraries to be placed in the
        {% block global_scripts %} block
        """
        return CDN.js_files
