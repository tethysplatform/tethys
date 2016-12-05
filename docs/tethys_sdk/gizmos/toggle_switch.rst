*************
Toggle Switch
*************

**Last Updated:** August 10, 2015

.. autoclass:: tethys_sdk.gizmos.ToggleSwitch

AJAX
----

Often dynamically loading in the ToggleSwitch can be useful. Here is a description of how
to do so with the ToggleSwitch gizmo.

.. note::

    In order to use this, you will either need to use a ``ToggleSwitch`` gizmo on
    the main page or register the dependencies in the main html template page
    using the ``import_gizmo_dependency`` tag with the ``toggle_switch`` name
    in the ``import_gizmos`` block.

    For example:
    ::

        {% block import_gizmos %}
            {% import_gizmo_dependency toggle_switch %}
        {% endblock %}

Four elements are required:

1) A controller for the AJAX call with a ToggleSwitch gizmo.
::

    import json

    @login_required()
    def toggle_ajax(request):
        """
        Controller for the datatable ajax request.
        """

        toggle_switch = ToggleSwitch(display_text='Defualt Toggle',
                                     name='toggle1')

        context = {'toggle_switch': toggle_switch}

        return render(request, 'app_name/toggle_ajax.html', context)

2) A template for with the tethys gizmo (e.g. toggle_ajax.html)
::

    {% load tethys_gizmos %}

    {% gizmo toggle_switch %}

3) A url map to the controller in app.py
::

    ...
        UrlMap(name='toggle_ajax',
               url='app-name/toggle_ajax',
               controller='app_name.controllers.toggle_ajax'),
    ...



4) The AJAX call in the javascript
::

    $(function() { //wait for page to load

        $.ajax({
            url: 'toggle_ajax',
            method: 'GET',
            success: function(data) {
                //add DataTable  to page
               $("#toggle_div").html(data);

                //Initialize DataTable
                $("#toggle_div").find('.bootstrap-switch').bootstrapSwitch();
             }
        });

    });