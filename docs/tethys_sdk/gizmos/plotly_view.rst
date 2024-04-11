.. _plotly_view_gizmo:

***********
Plotly View
***********

**Last Updated:** August 2023


.. important::

    This gizmo requires the ``plotly`` library to be installed. Starting with Tethys 5.0 or if you are using ``micro-tethys-platform``, you will need to install ``plotly`` using conda or pip as follows:

    .. code-block:: bash

        # conda: conda-forge channel strongly recommended
        conda install -c conda-forge plotly

        # pip
        pip install plotly
    
    **Don't Forget**: If you end up using this gizmo in your app, add ``plotly`` as a requirement to your :file:`install.yml`.

Python
------

.. autoclass:: tethys_sdk.gizmos.PlotlyView

AJAX
----

Often dynamically loading in plots can be useful. Here is a description of how
to do so with PlotlyView.

.. note::

    In order to use this, you will either need to use a ``PlotlyView`` gizmo on
    the main page or register the dependencies in the main html template page
    using the ``import_gizmo_dependency`` tag with the ``plotly_view`` name
    in the ``import_gizmos`` block.

    For example:
    ::

        {% block import_gizmos %}
            {% import_gizmo_dependency plotly_view %}
        {% endblock %}

Three elements are required:

1) A controller for the AJAX call with a PlotlyView gizmo.

.. code-block:: python

    from datetime import datetime
    import plotly.graph_objs as go
    from tethys_sdk.gizmos import PlotlyView
    from tethys_sdk.routing import controller
    from .app import App

        
    @controller(name='plotly_ajax', url='app-name/plotly')
    def plotly_ajax(request):
        """
        Controller for the plotly ajax request.
        """
        x = [datetime(year=2013, month=10, day=04),
             datetime(year=2013, month=11, day=05),
             datetime(year=2013, month=12, day=06)]
        
        my_plotly_view = PlotlyView([go.Scatter(x=x, y=[1, 3, 6])])

        context = {'plotly_view_input': my_plotly_view}

        return App.render(request, 'plotly_ajax.html', context)

2) A template for with the tethys gizmo (e.g. plotly_ajax.html)

.. code-block:: html+django

    {% load tethys %}

    {% gizmo plotly_view_input %}

3) The AJAX call in the javascript

.. code-block:: javascript

    $(function() { //wait for page to load

        $.ajax({
            url: 'plotly',
            method: 'GET',
            data: {
                'plot_height': 500, //example data to pass to the controller
            },
            success: function(data) {
                // add plot to page
                $("#plotly_plot_div").html(data);

                //NOTE: IF USING MODAL/MESSAGE BOX NEED A TIMEOUT BEFORE DISPLAY
                //$('#modal_div').modal('show');   
                //setTimeout(function(){ 
                //    $("#modal_div").find('.modal-body').html(data);
                //}, 100);

            }
        });

    });