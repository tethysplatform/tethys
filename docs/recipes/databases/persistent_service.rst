.. _persistent_service:


*************************************************
Getting Started With a Persistent Storage Service
*************************************************

**Last Updated:** September 2025

1. Install PostgreSQL with PostGIS
==================================

The peristent store API currently only works with the PostgreSQL databases. However, the default installation of Tethys Platform uses SQLite as the database backend. Here you will reconfigure your Tethys installation to use a PostgreSQL database instead of SQLite. There are many ways to install PostgreSQL, but for this tutorial you will learn how to install PostgreSQL using Docker.

a. Install PostgreSQL database with the PostGIS extension using Docker:

    a. Install `Docker Desktop <https://www.docker.com/products/docker-desktop>`_ or `Docker Engine <https://docs.docker.com/engine/install/>`_.

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

    c. Run the ``tethys db configure`` command to prepare the database for use by the Tethys portal:

    .. code-block:: bash

        PGPASSWORD=mysecretpassword tethys db configure

    The default password for the ``postgis/postgis`` container is "mysecretpassword". If you changed it, you will need to replace it in the command above.

    d. Start Tethys the development server (``tethys manage start``) and verify that the app is still working.

.. important::

    You will now need to start the "tethys_postgis" container each time you want to start the Tethys development server. You can do this using the Docker Desktop application or by running the following command:

    .. code-block:: bash

        docker start tethys_postgis

d. Add necessary dependencies:

    Persistent stores is an optional feature in Tethys, and requires that the ``sqlalchemy<2`` and ``psycopg2`` libraries are installed. Install these libraries using one of the following commands:

    .. code-block:: bash

            # conda: conda-forge channel strongly recommended
            conda install -c conda-forge "sqlalchemy<2" psycopg2

            # pip
            pip install "sqlalchemy<2" psycopg2

    If you'd like to install your app somewhere else, it will help to add these libraries to the app's dependencies. Add the new dependencies to your :file:`install.yml` as follows:

    .. code-block:: yaml
        :emphasize-lines: 13, 15-16

        # This file should be committed to your app code.
        version: 1.1
        # This should be greater or equal to your tethys-platform in your environment
        tethys_version: ">=4.0.0"
        # This should match the app - package name in your setup.py
        name: dam_inventory

        requirements:
        # Putting in a skip true param will skip the entire section. Ignoring the option will assume it be set to False
        skip: false
        conda:
            channels:
            - conda-forge
            packages:
            - sqlalchemy<2
            - psycopg2

        pip:

        npm:

        post:

2. Connecting to Your Persistent Store Service
==============================================


a. In your preferred text editor, open ``app.py`` and define a new ``PersistentStoreDatabaseSetting`` by adding the ``persistent_store_settings`` method to your app class:

    .. code-block:: python

        from tethys_sdk.app_settings import PersistentStoreDatabaseSetting

        class App(TethysAppBase):
            """
            Tethys app class for your application.
            """
            ...
            def persistent_store_settings(self):
                """
                Define Persistent Store Settings.
                """
                ps_settings = (
                    PersistentStoreDatabaseSetting(
                        name='primary_db',
                        description='primary database',
                        initializer='your_app.model.init_primary_db',
                        required=True
                    ),
                )

                return ps_settings


b. Add a **Persistent Store Service** to Tethys Portal:

    a. Go to Tethys Portal Home in a web browser (e.g. http://localhost:8000/apps/)
    b. Select **Site Admin** from the drop down next to your username.
    c. Scroll down to the **Tethys Services** section and select **Persistent Store Services** link.
    d. Click on the **Add Persistent Store Service** button.
    e. Give the **Persistent Store Service** any name and fill out the connection information.
    f. Press **Save** to create the new **Persistent Store Service**.


.. figure:: ../../images/tutorial/advanced/Persistent_Store_Service.png
    :width: 100%
    :align: center

.. important::

    The username and password for the persistent store service must be a user with permissions to create databases to use spatial persistent stores. The ``tethys db configure`` command creates a superuser named "tethys_super", password: "pass".

c. Assign the Persistent Store Service to Your App

    1. Go to Tethys Portal Home in a web browser (e.g. http://localhost:8000/apps/)

    2. Select Site Admin from the drop down next to your username.

    3. Scroll down to the Tethys Apps section and select the Installed App link.

    4. Select the link for your app.

    5. Scroll down to the Persistent Store Database Settings section.

    6. Assign the Persistent Store Service that you created in Step 4 to the primary_db setting.

    7. Press Save to save the settings.

.. figure:: ../../images/tutorial/advanced/Assign_Persistent_Store_Service.png
    :width: 100%
    :align: center

d. If you've already defined tables for the database in your app, you'll need to run the **syncstores** command to create them in your new Persistent Store database:

    .. code-block:: bash

        tethys syncstores your_app