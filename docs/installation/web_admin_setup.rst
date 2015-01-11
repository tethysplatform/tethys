***************
Web Admin Setup
***************

**Last Updated:** January 10, 2015

The final step required to setup your Tethys Platform is to link it to the software that is running in the Docker containers. This is done using the Tethys Portal Admin console.

1. Access Tethys Portal Admin Console
-------------------------------------

The Tethys Portal Admin Console is only accessible to users with administrator rights. When you initialized the database, you were prompted to create the default admin user. Use these credentials to log in for the first time.

a. Use the "Log In" link on the Tethys Portal homepage to log in as an administrator. Use the username and password that you setup when you initialized the database.

  .. figure:: ../images/site_admin/log_in.png
      :width: 600px
      :align: center

      **Figure 1.** Log In link for Tethys Portal.

b. Select "Site Admin" from the user drop down menu (Figure 1).

  .. figure:: ../images/site_admin/select_site_admin.png
      :width: 600px
      :align: center

      **Figure 2.** Select "Site Admin" from the user dropdown menu.


You will now be looking at the Tethys Portal Web Admin Console. The Web Admin console can be used to manage user accounts, customize the homepage of your Tethys Portal, and configure the software included in Tethys Platform. Take a moment to familiarize yourself with the different options that are available in the Web Admin (Figure 2).

  .. figure:: ../images/site_admin/home.png
      :width: 600px
      :align: center

      **Figure 3.** The Tethys Portal Web Admin Console.


2. Link to 52 North WPS Docker
------------------------------

The built in 52 North Web Processing Service (WPS) is provided as one mechanism for Geoprocessing in apps. It exposes the GRASS GIS and Sextante geoprocessing libraries as web services. See :doc:`../tethys_sdk/geoprocessing` documentation for more details about how to use 52 North WPS processing in apps. Complete the following steps to link Tethys with the 52 North WPS:

a. Select "Web Processing Services" from the options listed on the Tethys Portal Admin Console.

b. Click on the "Add Web Processing Service" button to create a new link to the web processing service.

  .. figure:: ../images/site_admin/wps_services.png
      :width: 600px
      :align: center

      **Figure 4.** Select the "Add Web Processing Service" button.

c. Provide a unique name for the web processing service.

d. Provide an endpoint to the 52 North WPS that is running in Docker. The endpoint is a URL pointing to the WPS. The endpoint will be similar to this:

  ::

    http://<host>:<port>/wps/WebProcessingService

  To determine the endpoint host and port for your docker, use the :doc:`../tethys_sdk/tethys_cli`:

  ::

    $ tethys docker ip

  When you are done you will have something similar to this:

  .. figure:: ../images/site_admin/wps_service_edit.png
    :width: 600px
    :align: center

    **Figure 5.** Fill out the form to register a new Web Processing Service.

e. Press "Save" to save the WPS configuration.


What's Next?
------------

Head over to :doc:`../getting_started` and create your first app. You can also check out the :doc:`../tethys_sdk` documentation to familiarize yourself with all the features that are available.