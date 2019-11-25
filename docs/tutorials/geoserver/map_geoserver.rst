********************
Map GeoServer Layers
********************

**Last Updated:** November 2019


1. Map Page UrlMap
==================

Add a new ``UrlMap`` to the ``url_maps`` method of the :file:`app.py` module:

::

    UrlMap(
        name='map',
        url='geoserver-app/map',
        controller='geoserver_app.controllers.map'
    ),


2. Map Page Controller
======================

Add a new controller to the :file:`controller.py` module:

::

    @login_required()
    def map(request):
        """
        Controller for the map page
        """
        geoserver_engine = app.get_spatial_dataset_service(name='main_geoserver', as_engine=True)

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
                    'url': 'http://localhost:8181/geoserver/wms',
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
            view=view_options
        )

        context = {'map_options': map_options,
                   'select_options': select_options}

        return render(request, 'geoserver_app/map.html', context)

3. Map Page Template
====================

Create a new :file:`map.html` template in your template directory and add the following contents:

::

    {% extends "geoserver_app/base.html" %}
    {% load tethys_gizmos %}

    {% block app_content %}
        <h1>GeoServer Layers</h1>
        <form method="post">
            {% csrf_token %}
            {% gizmo select_input select_options %}
            <input name="submit" type="submit" value="Update" class="btn btn-default">
        </form> 
        {% gizmo map_options %}
    {% endblock %}


4. Test Map Page
================

Navigate to the map page (`<http://localhost:8000/apps/geoserver-app/map/>`_). Use the select box to select a layer to display on the map. Press the submit button to effect the change.