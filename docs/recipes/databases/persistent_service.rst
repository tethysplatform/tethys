.. _persistent_service_recipe:


*************************************************
Getting Started With a Persistent Store Service
*************************************************

**Last Updated:** September 2025

Recommended prerequisite: :ref:`Use Databases <_use_databases_recipe>`

1. Install Dependencies
=======================

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