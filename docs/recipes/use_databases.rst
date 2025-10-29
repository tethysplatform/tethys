.. _use_databases_recipe :

*************
Use Databases
*************

**Last Updated:** September 2025

In this recipe you will configure your Tethys installation to use a Postgre SQL database.  There are many ways to install PostgreSQL, but for this recipe you will install it using Docker.

a. Install PostgreSQL database with the PostGIS extension using Docker:

    a. Install `Docker Desktop <https://www.docker.com/products/docker-desktop>`_ or `Docker Engine <https://docs.docker.com/engine/install/>`_.  Open Docker and have it run in the background while you complete the tutorial.

    b. Open a terminal and run the following command to create a new PostgreSQL with PostGIS Docker container:

    .. code-block:: bash

        docker run -d --name tethys_postgis -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 postgis/postgis

    c. Verify in Docker desktop that you have a new container running with the name "tethys_postgis" on port ``5432`` (**5432**:5432).

b. Add necessary Python dependencies:

    To use the PostgreSQL database you need to install the ``psycopg2`` library. Install it using one of the following commands:

    .. code-block:: bash

            # conda: conda-forge channel strongly recommended
            conda install -c conda-forge psycopg2

            # pip
            pip install psycopg2

c. Configure Tethys to use PostgreSQL database:

    a. Stop the Tethys development server if it is running by pressing :kbd:`CTRL-C` in the terminal.

    b. Configure the Tethys Portal to use the new Docker database using the ``tethys settings`` command:

    .. code-block:: bash

        tethys settings --set DATABASES.default.ENGINE django.db.backends.postgresql --set DATABASES.default.NAME tethys_platform --set DATABASES.default.USER tethys_default --set DATABASES.default.PASSWORD pass --set DATABASES.default.HOST localhost --set DATABASES.default.PORT 5432

    c. Run the correct ``tethys db configure`` command for your system to prepare the database for use by the Tethys portal:

    .. code-block:: bash
       
        # Windows System
        set PGPASSWORD=mysecretpassword
        tethys db configure

        # Unix System
        PGPASSWORD=mysecretpassword tethys db configure

    
    
    The default password for the ``postgis/postgis`` container is "mysecretpassword". If you changed it, you will need to replace it in the command above.

    .. Note::

        Command line interfaces will not show the keystrokes when entering passwords.  Don't worry if you are typing the password into the terminal and nothing shows up on the screen.


    d. Start Tethys the development server (``tethys start``) and verify that the app is still working.

.. important::

    You will now need to start the "tethys_postgis" container each time you want to start the Tethys development server. You can do this using the Docker Desktop application or by running the following command:

    .. code-block:: bash

        docker start tethys_postgis
