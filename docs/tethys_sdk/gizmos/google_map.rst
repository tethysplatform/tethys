***************
Google Map View
***************

**Last Updated:** August 10, 2015

.. autoclass:: tethys_sdk.gizmos.GoogleMapView

JavaScript API
--------------

For advanced features, the JavaScript API can be used to interact with the editable map. If you need capabilities beyond the scope of this API, we recommend using the Google Maps version 3 API to create your own map.

TETHYS_GOOGLE_MAP_VIEW.getMap()
+++++++++++++++++++++++++++++++

This method returns the Google Map object for direct manipulation through JavaScript.

TETHYS_GOOGLE_MAP_VIEW.getGeoJson()
+++++++++++++++++++++++++++++++++++

This method returns the GeoJSON object representing all of the overlays on the map.

TETHYS_GOOGLE_MAP_VIEW.getGeoJsonString()
+++++++++++++++++++++++++++++++++++++++++

This method returns a stringified GeoJSON object representing all of the overlays on the map.

TETHYS_GOOGLE_MAP_VIEW.getWktJson()
+++++++++++++++++++++++++++++++++++

This method returns a Well Known Text JSON object representing all of the overlays on the map.

TETHYS_GOOGLE_MAP_VIEW.getWktJsonString()
+++++++++++++++++++++++++++++++++++++++++

This method returns a stringified Well Known Text JSON object representing all of the overlays on the map.

TETHYS_GOOGLE_MAP_VIEW.swapKmlService(kml_service)
++++++++++++++++++++++++++++++++++++++++++++++++++

Use this method to swap out the current reference kml layers for new ones.

* **kml_service** *(string)* = URL endpoint that returns a JSON object with a property called 'kml_link' that is an array of publicly accessible URLs to kml or kmz documents

TETHYS_GOOGLE_MAP_VIEW.swapOverlayService(overlay_service, clear_overlays)
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Use this method to add new overlays to the map dynamically without reloading the page.

* **overlay_service** *(string)* = URL endpoint that returns a JSON object with a property called 'overlay_json' that has a value of a WKT or GeoJSON object in the same format as is used for input_overlays
* **clear_overlays** *(boolean)* = if true, will clear all overlays from the map prior to adding the new overlays. Otherwise all overlays will be retained.

