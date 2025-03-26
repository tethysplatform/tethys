********************
Additional Exercises
********************

**Last Updated:** July 2024

Now that you have completed the THREDDS tutorial, try one of the following exercises on your own to improve the usability of the app:

0. Start From Previous Solution (Optional)
==========================================

If you wish to use the previous solution as a starting point:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-thredds_tutorial
    cd tethysapp-thredds_tutorial
    git checkout -b plot-at-location-solution plot-at-location-solution-|version|

1. Initialize Dataset Select after Page Load
============================================

You may have noticed that it can take several seconds for the app to load. This is because the app is loading the datasets in the controller, which is less than ideal. Create a new controller for loading the datasets and call it after the page load, displaying the map loading indicator while it processes. This will give the use the impression that the app loads quickly, even though it takes the same amount of time.

2. Add Controls to Set the Color Scale Range
============================================

The current implementation uses hard-coded values for the color scale range of the style applied to the layer. See ``update_layer`` method of :file:`public/js/leaflet_map.js`:

.. code-block:: javascript

    update_layer = function() {
        ...
        var proxyWMSURL = `getWMSImageFromServer?main_url=${encodeURIComponent(m_curr_wms_url)}`;

        // Layer
        m_layer = L.tileLayer.wms(proxyWMSURL, {
            layers: m_curr_variable,
            format: 'image/png',
            transparent: true,
            colorscalerange: '250,350',  // Hard-coded color scale range won't work for all layers
            abovemaxcolor: "extend",
            belowmincolor: "extend",
            numcolorbands: 100,
            styles: m_curr_style
        });

The hard-coded values work well for the temperature layers, but are inappropriate for many of the other layers. Add controls (e.g. input fields of type number) for setting the minimum and maximum values that define the color scale range. Then implement the appropriate javascript to update the style appropriately.

3. Dynamic Scale on the Legend Image
====================================

As implemented in this tutorial, the legend image always displays the default scale from -50 to 50. Investigate the ``GetLegendGraphic`` request for THREDDS WMS services to see if you can modify the legend to show the scale of the current layer. The current URL that is used can be found in the ``src`` attribute of the legend image and will be something like this:

.. code-block:: html

    <img src="https://thredds.ucar.edu/thredds/wms/grib/NCEP/GFS/Global_0p5deg/TwoD?REQUEST=GetLegendGraphic&LAYER=Temperature_isobaric&PALETTE=rainbow">

The URL for the legend image is set in the ``update_legend`` method in :file:`public/js/leaflet_map.js`.

4. Set Color Scale Range Automatically
======================================

Use the Siphon client to determine the minimum and maximum values of the layer dynamically when retrieving metadata about the layer. Then use these values to set the color scale range and legend image in `:file:`public/js/leaflet_map.js`.

5. Visualize with Other Mapping Library
=======================================

Try implementing a new page that visualizes the THREDDS data with a different map view provided by Tethys such as the :ref:`map-view` or :ref:`cesium-map-view`. For a challenge, try visualizing the data using Bokeh/Panel approach (see: :ref:`bokeh-tutorial`).
