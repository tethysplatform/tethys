*********************************
THREDDS Engine (Siphon) Reference
*********************************

**Last Updated**: December 2019

This guide introduces `Siphon <https://unidata.github.io/siphon/latest/index.html>`_, the which is used as the engine for the THREDDS spatial dataset service. Siphon is a 3rd-party library developed by Unidata for interacting with data on remote services, currently focused on THREDDS services. Siphon does not implement the ``SpatialDatasetEngine`` pattern.

Example Usage
=============

The ``get_spatial_dataset_service()`` method of the app class returns a ``siphon.catalog.TDSCatalog`` object when the ``as_engine=True`` option is provided. The ``TDSCatalog`` object can be used to query the datasets on the THREDDS server.

NCSS Query Time Series
----------------------

This example is adapted from the `Siphon NCSS Time Series Example <https://unidata.github.io/siphon/latest/examples/ncss/NCSS_Timeseries_Examples.html>`_

.. code-block:: python

    import datetime
    from netCDF4 import num2date
    from my_first_app.app import MyFirstApp as app

    # This returns a siphon.catalog.TDSCatalog bound to the THREDDS service
    catalog = app.get_spatial_dataset_service('primary_thredds', as_engine=True)

    # Retrieve a dataset
    datasets = catalog.datasets
    a_dataset = datasets[0]

    # Get the NCSS access point
    ncss = a_dataset.subset()

    # Create a new query
    query = ncss.query()

    # Construct a query at a location specified by the latitude and longitude and time range
    # and return it in the NetCDF4 format
    now = datetime.utcnow()
    query.lonlat_point(-105, 40).time_range(now, now + timedelta(days=7))
    query.variables('streamflow').accept('netcdf')

    # Execute the query
    data = ncss.get_data(query)

    # Extract arrays
    streamflow = data.variables['streamflow']
    time = data.variables['time']

    # Convert times to Python datetime objects
    time_objects = num2date(time[:].squeeze(), time.units)


.. tip::

    Refer to the `Siphon Examples <https://unidata.github.io/siphon/latest/examples/index.html>`_ documentation for more example usage.

References
==========

* Siphon Home: https://unidata.github.io/siphon/latest/index.html
* Siphon Examples: https://unidata.github.io/siphon/latest/examples/index.html

