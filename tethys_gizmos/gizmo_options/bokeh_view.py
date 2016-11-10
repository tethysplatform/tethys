# coding=utf-8
from bokeh.embed import components

from .base import TethysGizmoOptions

__all__ = ['BokehView']


class BokehView(TethysGizmoOptions):
    """
    Simple options object for plotly view.
    
    .. info:: See https://plot.ly/python for Plotly API

    Attributes:
        plot_input(bokeh figure): A bokeh figure to be plotted.
        height(Optional[str]): Height of the plot element. Any valid css unit of length.
        width(Optional[str]): Width of the plot element. Any valid css unit of length.
        attributes(Optional[dict]): Dictionary of attributed to add to the outer div.
        classes(Optional[str]): Space separated string of classes to add to the outer div.
        hidden(Optional[bool]): If True, the plot will be hidden. Default is False.
        show_link(Optional[bool]): If True, the link to export plot to view in plotly is shown. Default is False.
        load_js(Optional[bool]): If False, then it will not include the javascript.  
                                 An example case of setting to False is using AJAX to add another chart.
                                 Default is True.
                                 
    Controller Code Example::
    
        from tethys_sdk.gizmos import BokehView
        from bokeh.plotting import figure
        
        plot = figure()
        plot.circle([1,2], [3,4])

        my_bokeh_view = BokehView(plot)

        context = {'bokeh_view_input': my_bokeh_view}
        
    Template Code Example::
    
        {% load tethys_gizmos %}
        
        {% block register_gizmos %}
          {% register_gizmo_dependency bokeh_view %}
        {% endblock %}
    
        {% gizmo bokeh_view bokeh_view_input %}
    """
    def __init__(self, plot_input, height='520px', width='100%', 
                 attributes='', classes='', divid='', hidden=False,
                 show_link=False):
        """
        Constructor
        """
        # Initialize the super class
        super(BokehView, self).__init__()
        self.script, self.div = components(plot_input)
        self.height = height
        self.width = width
        self.attributes = attributes
        self.classes = classes
        self.divid = divid
        self.hidden = hidden



