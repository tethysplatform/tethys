**********************
Visualize with Leaflet
**********************

**Last Updated:** December 2019

In this tutorial we will learn how to add a `Leaflet <https://leafletjs.com/>`_ map to a Tethys App for visualizing layers from a THREDDS server. The following topics will be covered in this tutorial:

* Adding 3rd Party JavaScript libraries and CSS to Tethys Apps
* Introduction to Leaflet Map
* Using Leaflet Plugins
* Visualizing Time-varying THREDDS layers with Leaflet

0. Start From Previous Solution (Optional)
==========================================

If you wish to use the previous solution as a starting point:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-thredds_tutorial.git
    cd tethysapp-thredds_tutorial
    git checkout -b thredds-service-solution thredds-service-solution-|version|


1. Add Leaflet Map to Home View
===============================

1. Add leaflet libraries to your app. Leaflet can be added a number of different ways as documented on their `Download page<https://leafletjs.com/download.html>'_. For this tutorial we will use the CDN option. Replace the contents of :file:`templates/thredds_tutorial/home.html` with:

.. code-block:: html+django

    {% extends "thredds_tutorial/base.html" %}
    {% load tethys_gizmos %}

    {% block styles %}
      {{ block.super }}
      <link rel="stylesheet" href="https://unpkg.com/leaflet@1.6.0/dist/leaflet.css"
       integrity="sha512-xwE/Az9zrjBIphAcBb3F6JVqxf46+CDLwfLMHloNu6KEQCAWi6HcDUbeOfBIptF7tcCzusKFjFw2yuvEpDL9wQ=="
       crossorigin=""/>
    {% endblock %}

    {% block global_scripts %}
      {{ block.super }}
      <script src="https://unpkg.com/leaflet@1.6.0/dist/leaflet.js"
       integrity="sha512-gZwIG9x3wUXg2hdXF6+rVkLF/0Vi9U8D2Ntg4Ga5I5BZpVkVxlJWbSQtXPSiUTtC0TjtGOmxa1AJPuV0CPthew=="
       crossorigin=""></script>
    {% endblock %}

    {% block header_buttons %}
    {% endblock %}

    {% block app_content %}
      <div id="leaflet-map"></div>
    {% endblock %}

    {% block app_actions_override %}
    {% endblock %}

.. todo::

    Add explanation on the differences between the different blocks:

        * styles vs. content_dependent_styles
        * scripts vs. global_scripts

2. Create :file:`public/js/leaflet_map.js`, with the following contents:

.. code-block:: javascript

    /*****************************************************************************
     * FILE:      Leaflet Map Module for THREDDS Tutorial
     * DATE:      13 December 2019
     * AUTHOR:    Nathan Swain
     * COPYRIGHT: (c) Aquaveo 2019
     * LICENSE:   BSD 2-Clause
     *****************************************************************************/

    /*****************************************************************************
     *                      LIBRARY WRAPPER
     *****************************************************************************/

    var LEAFLET_MAP = (function() {
        "use strict"; // And enable strict mode for this library

        /************************************************************************
        *                      MODULE LEVEL / GLOBAL VARIABLES
        *************************************************************************/
        var public_interface,				// Object returned by the module
            m_map;					        // The Leaflet Map
        /************************************************************************
        *                    PRIVATE FUNCTION DECLARATIONS
        *************************************************************************/
        var init_map;

        /************************************************************************
        *                    PRIVATE FUNCTION IMPLEMENTATIONS
        *************************************************************************/
        init_map = function() {
            // Create Map
            m_map = L.map('leaflet-map', {
                zoom: 5,
                center: [38.0, 15.0],
                fullscreenControl: true,
            });

            // Add Basemap
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(m_map);
        };

        /************************************************************************
        *                        DEFINE PUBLIC INTERFACE
        *************************************************************************/
        /*
         * Library object that contains public facing functions of the package.
         * This is the object that is returned by the library wrapper function.
         * See below.
         * NOTE: The functions in the public interface have access to the private
         * functions of the library because of JavaScript function scope.
         */
        public_interface = {};

        /************************************************************************
        *                  INITIALIZATION / CONSTRUCTOR
        *************************************************************************/

        // Initialization: jQuery function that gets called when
        // the DOM tree finishes loading
        $(function() {
            init_map();
        });

        return public_interface;

    }()); // End of package wrapper

.. todo::

    Change initial view to match data that will be demoed.

3. Create :file:`public/css/leaflet_map.css` with the following contents:

.. code-block:: css

    /* Map Format */
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

4. Link the new stylesheet and JavaScript modules in :file:`templates/thredds_tutorial/home.html`:

.. code-block:: html+django

    {% load tethys_gizmos static %}

    {% block styles %}
      {{ block.super }}
      <link rel="stylesheet" href="https://unpkg.com/leaflet@1.6.0/dist/leaflet.css"
       integrity="sha512-xwE/Az9zrjBIphAcBb3F6JVqxf46+CDLwfLMHloNu6KEQCAWi6HcDUbeOfBIptF7tcCzusKFjFw2yuvEpDL9wQ=="
       crossorigin=""/>
      <link rel="stylesheet" href="{% static 'thredds_tutorial/css/leaflet_map.css' %}"/>
    {% endblock %}

    {% block global_scripts %}
      {{ block.super }}
      <script src="https://unpkg.com/leaflet@1.6.0/dist/leaflet.js"
       integrity="sha512-gZwIG9x3wUXg2hdXF6+rVkLF/0Vi9U8D2Ntg4Ga5I5BZpVkVxlJWbSQtXPSiUTtC0TjtGOmxa1AJPuV0CPthew=="
       crossorigin=""></script>
    {% endblock %}

    {% block scripts %}
      {{ block.super }}
      <script src="{% static 'thredds_tutorial/js/leaflet_map.js' %}" type="text/javascript"></script>
    {% endblock %}

.. tip::

    Load the ``static`` library and use the ``static`` tag to reference scripts, stylesheets, and other resources in your ``public`` directory.

2. Visualize Time-Varying THREDDS Layer on Leaflet Map
======================================================

This example is adapted from Time Dimension `Example 1 <https://github.com/socib/Leaflet.TimeDimension/blob/master/examples/js/example1.js>`_.

1. Add the `Time-Dimension <https://github.com/socib/Leaflet.TimeDimension>`_ Leaflet plugin libraries to :file:`templates/thredds_tutorial/home.html`:

.. code-block:: html+django

    {% block styles %}
      {{ block.super }}
      <link rel="stylesheet" href="https://unpkg.com/leaflet@1.6.0/dist/leaflet.css"
       integrity="sha512-xwE/Az9zrjBIphAcBb3F6JVqxf46+CDLwfLMHloNu6KEQCAWi6HcDUbeOfBIptF7tcCzusKFjFw2yuvEpDL9wQ=="
       crossorigin=""/>
      <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet-timedimension@1.1.1/dist/leaflet.timedimension.control.min.css" />
      <link rel="stylesheet" href="{% static 'thredds_tutorial/css/leaflet_map.css' %}"/>
    {% endblock %}

    {% block global_scripts %}
      {{ block.super }}
      <script src="https://unpkg.com/leaflet@1.6.0/dist/leaflet.js"
       integrity="sha512-gZwIG9x3wUXg2hdXF6+rVkLF/0Vi9U8D2Ntg4Ga5I5BZpVkVxlJWbSQtXPSiUTtC0TjtGOmxa1AJPuV0CPthew=="
       crossorigin=""></script>
      <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/iso8601-js-period@0.2.1/iso8601.min.js"></script>
      <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/leaflet-timedimension@1.1.1/dist/leaflet.timedimension.min.js"></script>
    {% endblock %}

2. Enable the Time Dimension control and set options when initializing the map in :file:`public/js/leaflet_map.js`:

.. code-block:: javascript

    init_map = function() {
 	    // Create Map
 	    m_map = L.map('leaflet-map', {
 	        zoom: 5,
 	        center: [38.0, 15.0],
 	        fullscreenControl: true,
            timeDimension: true,
            timeDimensionControl: true
 	    });

        // Add Basemap
 	    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(m_map);
 	};

3. Create a new method :file:`public/js/leaflet_map.js` in that will add a wms tile layer to the Leaflet map:

.. code-block:: javascript

    /************************************************************************
 	*                    PRIVATE FUNCTION DECLARATIONS
 	*************************************************************************/
 	var init_map, init_layers, add_wms_layer;

.. code-block:: javascript

    add_wms_layer = function(wms_layer, update_td) {
 	    // Wrap WMS layer in Time Dimension Layer
 	    let td_layer = L.timeDimension.layer.wms(wms_layer, {
 	        updateTimeDimension: update_td
 	    });

 	    // Add Time-Dimension-Wrapped WMS layer to the Map
 	    td_layer.addTo(m_map);

 	    return td_layer;
    };

.. code-block:: javascript

    init_layers = function() {
        let wms_url = "http://thredds.socib.es/thredds/wms/observational/satellite/altimetry/aviso/madt/sealevel_med_phy_nrt_L4_agg/sealevel_med_phy_nrt_L4_agg_best.ncd"

        // Height Layer
        let height_layer = L.tileLayer.wms(wms_url, {
            layers: 'adt',
            format: 'image/png',
            transparent: true,
            colorscalerange: '-0.4,0.4',
            abovemaxcolor: "extend",
            belowmincolor: "extend",
            numcolorbands: 100,
            styles: 'boxfill/rainbow'
        });

        let td_height_layer = add_wms_layer(height_layer, true);

        // Height Contour Layer
        let height_contour_layer = L.tileLayer.wms(wms_url, {
            layers: 'adt',
            format: 'image/png',
            transparent: true,
            colorscalerange: '-0.5,0.5',
            numcontours: 11,
            styles: 'contour/rainbow'
        });

        let td_height_contour_layer = add_wms_layer(height_contour_layer, false);

        // Velocity Layer
        let velocity_layer = L.tileLayer.wms(wms_url, {
            layers: 'surface_geostrophic_sea_water_velocity',
            format: 'image/png',
            transparent: true,
            colorscalerange: '-20,100',
            markerscale: 10,
            markerspacing: 8,
            abovemaxcolor: "extend",
            belowmincolor: "extend",
            numcolorbands: 100,
            styles: 'prettyvec/greyscale'
        });

        let td_velocity_layer = add_wms_layer(velocity_layer, false);

        // Layer Controls
        var overlay_layers = {
            "AVISO - Sea surface height above geoid": td_height_layer,
            "AVISO - Sea surface height above geoid (Contour)": td_height_contour_layer,
            "AVISO - Surface geostrophic sea water velocity": td_velocity_layer
        };

        L.control.layers([], overlay_layers).addTo(m_map);
    };

.. code-block:: javascript

    // Initialization: jQuery function that gets called when
    // the DOM tree finishes loading
    $(function() {
        init_map();
        init_layers();
    });

4. Solution
===========

This concludes the New App Project portion of the THREDDS Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-thredds_tutorial/tree/thredds-service-solution-3.0>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-thredds_tutorial.git
    cd tethysapp-thredds_tutorial
    git checkout -b visualize-leaflet-solution visualize-leaflet-solution-|version|