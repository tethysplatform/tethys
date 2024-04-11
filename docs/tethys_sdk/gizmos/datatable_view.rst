**************
DataTable View
**************

**Last Updated:** November 11, 2016

.. autoclass:: tethys_sdk.gizmos.DataTableView

AJAX
----

Often dynamically loading in the DataTable can be useful. Here is a description of how
to do so with the DataTableView gizmo.

.. note::

    In order to use this, you will either need to use a ``DataTableView`` gizmo on
    the main page or register the dependencies in the main html template page
    using the ``import_gizmo_dependency`` tag with the ``datatable_view`` name
    in the ``import_gizmos`` block.

    For example:
    ::

        {% block import_gizmos %}
            {% import_gizmo_dependency datatable_view %}
        {% endblock %}

Three elements are required:

1) A controller for the AJAX call with a DataTableView gizmo.

.. code-block:: python

    import json
    from .app import App

    @controller
    def datatable_ajax(request):
        """
        Controller for the datatable ajax request.
        """

        searching = False    
        if request.GET.get("searching") is not None:
            searching = json.loads(request.GET.get("searching"))
            if searching != True and searching != False:
                searching = False
        
        datatable_default = DataTableView(column_names=("Name", "Age", "Job"),
                                          rows=[("Bill", 30, "contractor"),
                                                ("Fred", 18, "programmer"),
                                                ("Bob", 26, "boss")],
                                          searching=searching,
                                          orderClasses=False,
                                          lengthMenu=[ [10, 25, 50, -1], [10, 25, 50, "All"] ],
                                          )

        context = {"datatable_options": datatable_default}

        return App.render(request, "datatable_ajax.html", context)

2) A template for with the tethys gizmo (e.g. datatable_ajax.html)

.. code-block:: html+django

    {% load tethys %}

    {% gizmo datatable_options %}


3) The AJAX call in the javascript

.. code-block:: javascript

    $(function() { //wait for page to load

        $.ajax({
            url: 'datatable_ajax',
            method: 'GET',
            data: {
                'searching': false, //example data to pass to the controller
            },
            success: function(data) {
                //add DataTable  to page
               $("#datatable_div").html(data);

                //Initialize DataTable
                $("#datatable_div").find('.data_table_gizmo_view').DataTable();
             }
        });

    });
