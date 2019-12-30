********************
Additional Exercises
********************

**Last Updated:** December 2019

Now that you have completed the THREDDS tutorial, try one of the following exercises on your own to improve the usability of the app:

0. Start From Previous Solution (Optional)
==========================================

If you wish to use the previous solution as a starting point:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-thredds_tutorial.git
    cd tethysapp-thredds_tutorial
    git checkout -b plot-at-location-solution plot-at-location-solution-|version|

1. Add Controls to Set the Color Scale Range
============================================

The current implementation uses hard-coded values for the color scale range of the style applied to the layer. See ``update_layer`` method of :file:`public/js/leaflet_map.js`:

.. code-block:: javascript

    update_layer = function() {
        ...
        // Layer
        m_layer = L.tileLayer.wms(m_curr_wms_url, {
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

2. Dynamic Scale on the Legend Image
====================================

As implemented in this tutorial, the legend image always displays the default scale from -50 to 50. Investigate the ``GetLegendGraphic`` request for THREDDS WMS services to see if you can modify the legend to show the scale of the current layer. The current URL that is used can be found in the ``src`` attribute of the legend image and will be something like this:

.. code-block:: html

    <img src="https://thredds.ucar.edu/thredds/wms/grib/NCEP/GFS/Global_0p5deg/TwoD?REQUEST=GetLegendGraphic&LAYER=Temperature_isobaric&PALETTE=rainbow">

The URL for the legend image is set in the ``update_legend`` method in :file:`public/js/leaflet_map.js`.

3. Set Color Scale Range Automatically
======================================

Use the Siphon client to determine the minimum and maximum values of the layer dynamically when retrieving metadata about the layer. Then use these values to set the color scale range and legend image in `:file:`public/js/leaflet_map.js`.