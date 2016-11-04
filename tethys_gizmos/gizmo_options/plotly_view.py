# coding=utf-8
import plotly.offline as opy

from .base import TethysGizmoOptions

__all__ = ['PlotlyView']


class PlotlyView(TethysGizmoOptions):
    """
    Simple options object for plotly view.
    
    .. info:: See https://plot.ly/python for Plotly API

    Attributes:
        plot_input(plotly graph_objs): A plotly graph_objs to be plotted.
        height(Optional[str]): Height of the plot element. Any valid css unit of length.
        width(Optional[str]): Width of the plot element. Any valid css unit of length.
        attributes(Optional[dict]): Dictionary of attributed to add to the outer div.
        classes(Optional[str]): Space separated string of classes to add to the outer div.
        hidden(Optional[bool]): If True, the plot will be hidden. Default is False.
        show_link(Optional[bool]): If True, the link to export plot to view in plotly is shown. Default is False.
        load_js(Optional[bool]): If False, then it will not include the javascript.  
                                 An example case of setting to False is using AJAX to add another chart.
                                 Default is True.
                                 
    Controller Code Example 1::
    
        import datetime as datetime
        import plotly.graph_objs as go
        from tethys_sdk.gizmos import PlotlyView

        x = [datetime(year=2013, month=10, day=04),
             datetime(year=2013, month=11, day=05),
             datetime(year=2013, month=12, day=06)]
    
        my_plotly_view = PlotlyView([go.Scatter(x=x, y=[1, 3, 6])])
        
        context = {'plotly_view_input': my_plotly_view}
        
    Controller Code Example 2::
    
        import numpy as np
        import pandas as pd
        from tethys_sdk.gizmos import PlotlyView
        
        df = pd.DataFrame(np.random.randn(1000, 2), columns=['A', 'B']).cumsum()

        my_plotly_view = PlotlyView(df.iplot(asFigure=True))

        context = {'plotly_view_input': my_plotly_view}
        
    Template Code::
    
        {% load tethys_gizmos %}
    
        {% gizmo plotly_view plotly_view_input %}
    """
    js_loaded = False
    
    def __init__(self, plot_input, height='520px', width='100%', 
                 attributes='', classes='', divid='', hidden=False,
                 show_link=False, load_js=True):
        """
        Constructor
        """
        # Initialize the super class
        super(PlotlyView, self).__init__()
        
        include_plotlyjs = load_js
        
        if load_js:
            #to ensure that there are no other instances 
            #loaded so there is not duplicate loads of javascript
            #on the page
            include_plotlyjs = not self.__class__.js_loaded
            if not self.__class__.js_loaded:
                self.__class__.js_loaded = True

        self.plotly_div = opy.plot(plot_input, 
                                   auto_open=False, 
                                   output_type='div',
                                   include_plotlyjs=include_plotlyjs,
                                   show_link=show_link)
        self.height = height
        self.width = width
        self.attributes = attributes
        self.classes = classes
        self.divid = divid
        self.hidden = hidden



