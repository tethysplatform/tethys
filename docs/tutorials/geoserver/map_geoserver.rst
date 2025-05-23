********************
Map GeoServer Layers
********************

**Last Updated:** July 2024

1. Map Page Controller
======================

Add a new controller to the :file:`controller.py` module:

.. code-block:: python

    @controller
    def map(request):
        """
        Controller for the map page
        """
        geoserver_engine = App.get_spatial_dataset_service(name='main_geoserver', as_engine=True)

        options = []

        response = geoserver_engine.list_layers(with_properties=False)

        if response['success']:
            for layer in response['result']:
                options.append((layer.title(), layer))

        select_options = SelectInput(
            display_text='Choose Layer',
            name='layer',
            multiple=False,
            options=options
        )

        map_layers = []

        if request.POST and 'layer' in request.POST:
            selected_layer = request.POST['layer']
            legend_title = selected_layer.title()

            geoserver_layer = MVLayer(
                source='ImageWMS',
                options={
                    'url': geoserver_engine.get_wms_endpoint(),
                    'params': {'LAYERS': selected_layer},
                    'serverType': 'geoserver'
                },
                legend_title=legend_title,
                legend_extent=[-114, 36.5, -109, 42.5],
                legend_classes=[
                    MVLegendClass('polygon', 'County', fill='#999999'),
            ])

            map_layers.append(geoserver_layer)


        view_options = MVView(
            projection='EPSG:4326',
            center=[-100, 40],
            zoom=4,
            maxZoom=18,
            minZoom=2
        )

        map_options = MapView(
            height='500px',
            width='100%',
            layers=map_layers,
            legend=True,
            view=view_options,
            basemap='OpenStreetMap'
        )

        context = {
            'map_options': map_options,
            'select_options': select_options
        }

        return App.render(request, 'map.html', context)

2. Map Page Template
====================

Create a new :file:`map.html` template in your template directory and add the following contents:

.. code-block:: html+django

    {% extends tethys_app.package|add:"/base.html" %}
    {% load tethys %}

    {% block app_content %}
        <h1>GeoServer Layers</h1>
        <form method="post" class="mb-3">
            {% csrf_token %}
            {% gizmo select_input select_options %}
            <input name="submit" type="submit" value="Update" class="btn btn-secondary">
        </form> 
        {% gizmo map_options %}
    {% endblock %}


3. Test Map Page
================

Navigate to the map page (`<http://localhost:8000/apps/geoserver-app/map/>`_). Use the select box to select a layer to display on the map. Press the submit button to effect the change.

4. Solution
===========

This concludes the this part of the GeoServer tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-geoserver_app>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-geoserver_app
    cd tethysapp-geoserver_app
    git checkout -b map-geoserver-solution map-geoserver-solution-|version|