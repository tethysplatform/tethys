*****************
Fetch Climate Map
*****************

**Last Updated:** August 10, 2015

.. autoclass:: tethys_sdk.gizmos.FetchClimateMap

FetchClimateURLParameter
------------------------

.. autoclass:: tethys_sdk.gizmos.FetchClimateURLParameter

FetchClimateMapData
-------------------

.. autoclass:: tethys_sdk.gizmos.FetchClimateMapData

FetchClimateMapParameters
-------------------------

.. autoclass:: tethys_sdk.gizmos.FetchClimateMapParameters

FetchClimatePlotParameters
--------------------------

.. autoclass:: tethys_sdk.gizmos.FetchClimatePlotParameters

FetchClimateVariableParameters
------------------------------

.. autoclass:: tethys_sdk.gizmos.FetchClimateVariableParameters

FetchClimateGridParameters
--------------------------

.. autoclass:: tethys_sdk.gizmos.FetchClimateGridParameters

FetchClimatePointParameters
---------------------------

.. autoclass:: tethys_sdk.gizmos.FetchClimatePointParameters

JavaScript API
--------------

For advanced features, the JavaScript API can be used to get the data once the request is complete.

*This is also available if you use the plot feature. To use it, replace all 'date' or 'DATE' in the names with 'plot' or 'PLOT' (except for 'fcDataRequestComplete' or 'fcOneDataRequestComplete').*

FETCHCLIMATE_DATA.getAllData()
++++++++++++++++++++++++++++++

ONCE THE AJAX CALLS ARE COMPLETE - This method returns an object with the initial key level as the variable names and the next level as the grid/point names with the data inside of the grid name key. However, if the AJAX calls are not complete, it returns -1.

**How to know when the AJAX calls are complete? - The Event Listener**

When *ALL* requests are complete - 'e.detail' contains all of the data returned from the AJAX calls:

::

    //The Entire Request Complete Event Listener</p>
    jQuery('#fetchclimate_data')[0].addEventListener('fcDataRequestComplete', function(e) {
        console.log(e.detail);
    });

When *ONE* of the requests is complete - 'e.detail' contains all of the data returned from the AJAX calls:

::

    //The Single Request Complete Event Listener</p>
    jQuery('#fetchclimate_data')[0].addEventListener('fcOneDataRequestComplete', function(e) {
        console.log(e.detail);
    });