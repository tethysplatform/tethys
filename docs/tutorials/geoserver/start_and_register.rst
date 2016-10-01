******************
Start and Register
******************

**Last Updated:** September 30, 2016


Start GeoServer Docker
======================

Start up your :doc:`../../software_suite/geoserver` container:

::

	$ tethys docker start -c geoserver


Register GeoServer Docker
=========================

Get the endpoint for your GeoServer Docker container:

::

	$ tethys docker ip

Register the GeoServer with Tethys in the Portal admin page. Select the dropdown menu next to your username in the top right-hand corner of the screen and select the "Site Admin" link. Select the "Spatial Dataset Servics" link from the "Tethys Services" section and then press the "Add Spatial Dataset Service" button. Create a new Spatial Dataset Service named "default" of type GeoServer, enter the endpoint and public endpoint as the same from the print out in the terminal, and fill out the username and password.


.. note::

	The default username and password for GeoServer is "admin" and "geoserver", respectfully. You do not need to enter an API key.


GeoServer Web Admin Interface
=============================

Explore the GeoServer web admin interface by visiting link: `<http://localhost:8181/geoserver/web/>`_.

Scaffold New App
================

Create a new app and install it:

::

    $ tethys scaffold geoserver_app
    $ cd tethysapp-geoserver_app
    $ python setup.py develop


Download Test Files
===================

Download the sample shapefiles that you will use to test your app:

:download:`geoserver_app_data.zip`

