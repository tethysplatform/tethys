************
Select Input
************

**Last Updated:** August 10, 2015

.. autoclass:: tethys_sdk.gizmos.SelectInput

AJAX
----

Often dynamically loading in a select input can be useful. Here is a description of how
to do so with the SelectInput gizmo.

.. note::

    In order to use this, you will either need to use a ``SelectInput`` gizmo on
    the main page or register the dependencies in the main html template page
    using the ``import_gizmo_dependency`` tag with the ``select_input`` name
    in the ``import_gizmos`` block.

    For example:

    .. code-block:: html+django

        {% block import_gizmos %}
            {% import_gizmo_dependency select_input %}
        {% endblock %}

Three elements are required:

1) A controller for the AJAX call with a SelectInput gizmo.

.. code-block:: python

    from tethys_sdk.gizmos import SelectInput
    from .app import App
        
    @controller(
        url="app_name/select",
    )
    def select_input_ajax(request):
        """
        Controller for the bokeh ajax request.
        """
        select_input2 = SelectInput(display_text="Select2",
                                    name="select2",
                                    multiple=False,
                                    options=[("One", "1"), ("Two", "2"), ("Three", "3")],
                                    initial=["Three"])

        context = {"select_input2": select_input2}

        return App.render(request, "select_input_ajax.html", context)

2) A template for with the tethys gizmo (e.g. select_input_ajax.html)

.. code-block:: html+django

    {% load tethys %}

    {% gizmo select_input2 %}

3) The AJAX call in the javascript

.. note:: You only need to call the init function if you are using select2.

.. code-block:: javascript

    $(function() { //wait for page to load

        $.ajax({
            url: 'select',
            method: 'GET',
            success: function(data) {
                // add to page
                $("#select_div").html(data);
                // initialize if using select2
                $("#select_div").find('.select2').select2();
            }
        });

    });