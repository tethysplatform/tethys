.. _add_leaflet_map_recipe :

*****************
Add a Leaflet Map
*****************

** Last Updated:** June 2026

This recipe will go over how to implement a Leaflet Map inside your Tethys app.

1. Link to CDN Files
Before you can place a Leaflet map inside your app, you'll need to link to Leaflet's JavaScript and CSS files inside your template.
To do so, add the following to your template(HTML) file:

.. code-block:: html+django

    {% block styles %}
        {{ block.super }}
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
        integrity="sha512-Zcn6bjR/8RZbLEpLIeOwNtzREBAJnUKESxces60Mpoj+2okopSAcSUIUOseddDm0cxnGQzxIR7vJgsLZbdLE3w=="
        crossorigin=""/>
    {% endblock %}

    {% block global_scripts %}
        {{ block.super }}
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
        integrity="sha512-BwHfrr4c9kmRkLw6iXFdzcdWV/PGkVgiIyIWLLlTSXzWQzxuSg4DiQUCpauz/EWjgk5TYQqX/kvn9pG1NpYfqg=="
        crossorigin=""></script>
    {% endblock %}

2. Add a Map Container to Template
Next, you'll need to place a container in your template to house your Leaflet map. For this example, we'll give that container an id 'leaflet-map' like so:

.. code-block:: html+django

    {% block app_content %}
        <div id="leaflet-map"></div>
    {% endblock %}

3. Initialize Map with JavaScript
Next, you'll need to add a new JavaScript file in which you will initialize the Leaflet map and add a basemap to it. First, add a file named 'leaflet_map.js' with the following contents:

.. code-block:: javascript

    var init_map = function() {
        // Create Map inside container
        m_map = L.map('leaflet-map', {
            zoom: 3,
            center: [0, 0],
            fullscreenControl: true,
        });

        // Add Basemap
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(m_map);
    };

    $(function() {
        init_map();
    });

4. Add CSS File
Lastly, you'll need to add a simple CSS file to style everything to make sure your map fills the available space in your app:

.. code-block:: css

    #app-content-wrapper #app-content {
        height: 100%;
    }

    #inner-app-content {
        height: 100%;
        padding: 0;
    }

    #leaflet-map {
        height: 100%;
    }

    /* Remove padding on bottom where app-actions section used to be */
    #app-content-wrapper #app-content {
        padding-bottom: 0;
    }

That's it! You've now added a leaflet map to your app.