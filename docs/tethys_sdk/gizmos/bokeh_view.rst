**********
Bokeh View
**********

**Last Updated:** August 2023

.. important::

   This gizmo requires the ``bokeh`` library to be installed. Starting with Tethys 5.0 or if you are using ``micro-tethys-platform``, you will need to install ``bokeh`` using conda or pip as follows:

   .. code-block:: bash

      # conda: conda-forge channel strongly recommended
      conda install -c conda-forge "bokeh<3"

      # pip
      pip install "bokeh<3"

   **Don't Forget**: If you end up using this gizmo in your app, add ``bokeh`` as a requirement to your :file:`install.yml`.

Python
------

.. autoclass:: tethys_sdk.gizmos.BokehView


AJAX
----

Often dynamically loading in plots can be useful. Here is a description of how
to do so with Bokeh.

.. note::

    In order to use this, you will either need to use a ``BokehView`` gizmo on
    the main page or register the dependencies in the main html template page
    using the ``import_gizmo_dependency`` tag with the ``bokeh_view`` name
    in the ``import_gizmos`` block.

    For example:

    .. code-block:: html+django

        {% block import_gizmos %}
            {% import_gizmo_dependency bokeh_view %}
        {% endblock %}

Three elements are required:

1) A controller for the AJAX call with a BokehView gizmo.


.. code-block:: python

    from tethys_sdk.gizmos import BokehView
    from tethys_sdk.routing import controller
    from bokeh.plotting import figure
    from .app import App
        
    @controller(name="bokeh_ajax", url="app-name/bokeh")
    def bokeh_ajax(request):
        """
        Controller for the bokeh ajax request.
        """
        plot = figure(plot_height=300)
        plot.circle([1,2], [3,4], radius=0.5)
        my_bokeh_view = BokehView(plot, height="300px")

        context = {'bokeh_view_input': my_bokeh_view}

        return App.render(request, 'bokeh_ajax.html', context)

2) A template for with the tethys gizmo (e.g. bokeh_ajax.html)

.. code-block:: html+django

    {% load tethys %}

    {% gizmo bokeh_view_input %}

3) The AJAX call in the javascript

.. code-block:: javascript

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
