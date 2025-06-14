********************
PGAdmin III Tutorial
********************

**Last Updated:** November 20, 2014

All of the SQL databases used in Tethys Platform are `PostregSQL <https://www.postgresql.org/>`_ databases. An excellent graphical client for PostgreSQL. It is available for Windows, OSX, and many Linux distributions. Please visit the `Download <https://www.pgadmin.org/download/>`_ page to learn how to install it for your particular operating system. After it is installed, you can connect to your Tethys Platform databases by using the credentials for the ``tethys_super`` database user you defined during installation.

To create a new connection to your PostgreSQL database using PGAdmin:

1. Open PGAdmin III and click on the ``Add New Connection`` button.

  .. figure:: ../images/pgadmin_tutorial_1.png
      :width: 550px

      **Figure 1.** Click the ``Add New Connection`` button.

2. In the New Server Registration dialog that appears, fill out the form with the appropriate credentials. Provide a meaningful name for the connection like "tethys". If you have installed PostgreSQL with the Docker containers, the host will be either ``localhost`` if you are on Linux or ``192.168.59.103`` if you are on Mac or Windows. Use the ``tethys docker ip`` command to get the port for PostgreSQL (PostGIS). Fill in the username as ``tethys_super`` and enter the password you gave the user during installation. Click ``OK`` to close the window.

  .. figure:: ../images/pgadmin_tutorial_2.png
      :width: 550px

      **Figure 2.** Fill out the New Server Registration dialog.

3. To connect to the PostgreSQL database server, double-click on the "tethys" connection listed under the ``Servers`` dropdown menu. You will see a list of the databases on the server. Expand the menus to view each database. The tables will be located under ``Schemas > public > Tables``.

  .. figure:: ../images/pgadmin_tutorial_3.png
      :width: 550px

      **Figure 3.** Browse the databases using the graphical interface.

