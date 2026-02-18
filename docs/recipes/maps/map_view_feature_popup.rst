.. _map_view_feature_popup_recipe:

*********************
MapView Feature Popup
*********************

**Last Updated:** October 2025

This recipe will show you how to implement click detection on your map view map with a feature popup that appears.

This recipe builds on the :ref:`GeoJSON Layer on Map View Recipe <geojson_layer_map_view_recipe>`

Begin by adding this to your page's template in after_app_content block

.. code-block:: html+django

    {% block after_app_content %}
        <div id="popup" class="ol-popup">
            <a href="#" id="popup-closer" class="ol-popup-closer"></a>
            <div id="popup-content"></div>
        </div>
    {% endblock %}

This popup will be used to show extra data once you click on a feature on your map. 

Next, create a new javascript file, for this recipe's sake, you can name this file :file:`home.js` and placing that file in the ``public/js`` folder

.. code-block:: javascript

    $(document).ready(function() {
    
        const container = document.getElementById('popup');
        const content = document.getElementById('popup-content');
        const closer = document.getElementById('popup-closer');

        const overlay = new Overlay({
        element: container,
        autoPan: {
            animation: {
            duration: 250,
            },
        },
        });

        closer.onclick = function () {
            overlay.setPosition(undefined);
            closer.blur();
            return false;
        };

        let map = TETHYS_MAP_VIEW.getMap();
        map.addOverlay(overlay);

        let selectInteraction = TETHYS_MAP_VIEW.getSelectInteraction();
        selectInteraction.on('select', function(event) {
            let feature = event.selected[0];
            console.log("Feature properties: ", feature.getProperties());
            console.log("Metadata: ", feature);
            const coordinate = feature.getGeometry().getCoordinates();
            
            console.log("Coordinate: ", coordinate);

            content.innerHTML = `
                <h3>${feature.get("name")}</h3>
                <table class="table table-striped table-bordered">
                    <tr>
                        <td>Longitude</td>
                        <td>${coordinate[0].toFixed(3)}</td>
                    </tr>
                    <tr>
                        <td>Latitude</td>
                        <td>${coordinate[1].toFixed(3)}</td>
                    </tr>
                    <tr>
                        <td>Country</td>
                        <td>${feature.get("country")}</td>
                    </tr>
                </table>
                `;
            overlay.setPosition(coordinate);
        });
    });

Now, just go ahead and make sure this file is loaded into your page by making the following addition in :file:`home.html`:


.. code-block:: html+django
    :emphasize-lines: 3

        {% block scripts %}
            {{ block.super }}
            <script src="{% static tethys_app|public:'js/home.js' %}" type="text/javascript"></script>
        {% endblock %}

Now, reload your app and click on a feature. You should see something like this:

.. figure:: ../../images/recipes/feature_popup.png
    :width: 500px
    :align: center

