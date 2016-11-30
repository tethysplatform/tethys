**********
Bokeh View
**********

**Last Updated:** November 11, 2016

.. autoclass:: tethys_sdk.gizmos.BokehView


AJAX
----

Often dynamically loading in plots can be useful. Here is a description of how
to do so with Bokeh

.. note::

    In order to use this, you will either need to use a ``BokehView`` gizmo on
    the main page or register the dependencies in the main html template page
    using the ``import_gizmo_dependency`` tag with the ``bokeh_view`` name
    in the ``import_gizmos`` block.

    For example:
    ::

        {% block import_gizmos %}
            {% import_gizmo_dependency bokeh_view %}
        {% endblock %}

Four elements are required:

1) A controller for the AJAX call with a BokehView gizmo.
::

    from tethys_sdk.gizmos import BokehView
    from bokeh.plotting import figure
        
    @login_required()
    def bokeh_ajax(request):
        """
        Controller for the bokeh ajax request.
        """
        plot = figure(plot_height=300)
        plot.circle([1,2], [3,4])
        my_bokeh_view = BokehView(plot, height="300px")

        context = {'bokeh_view_input': my_bokeh_view}

        return render(request, 'app_name/bokeh_ajax.html', context)

2) A template for with the tethys gizmo (e.g. bokeh_ajax.html)
::

    {% load tethys_gizmos %}

    {% gizmo bokeh_view_input %}

3) A url map to the controller in app.py
::

    ...
        UrlMap(name='bokeh_ajax',
               url='app_name/bokeh',
               controller='app_name.controllers.bokeh_ajax'),
    ...

4) The AJAX call in the javascript
::

    $(function() { //wait for page to load

        $.ajax({
            url: 'bokeh',
            method: 'GET',
            data: {
                'plot_height': 500, //example data to pass to the controller
            },
            success: function(data) {
                // add plot to page
                $("#bokeh_plot_div").html(data);
            }
        });

    });
