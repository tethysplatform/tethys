.. _key_concepts_advanced_tutorial:

*****************
Advanced Concepts
*****************

**Last Updated:** July 2024

This tutorial introduces advanced concepts for Tethys developers. The topics covered include:

* Tethys Services API
* PersistentStores API
* Permissions API
* Advanced HTML Forms - File Upload
* Plotting Gizmos

.. figure:: ../../images/tutorial/advanced/key-concepts-advanced-screenshot.png
    :width: 800px
    :align: center

0. Start From Intermediate Solution (Optional)
==============================================

If you wish to use the intermediate solution as a starting point:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-dam_inventory
    cd tethysapp-dam_inventory
    git checkout -b intermediate-solution intermediate-|version|

1. Install PostgreSQL with PostGIS
==================================

The peristent store API currently only works with the PostgreSQL databases. However, the default installation of Tethys Platform uses SQLite as the database backend. In this section you will reconfigure your Tethys installation to use a PostgreSQL database instead of SQLite. There are many ways to install PostgreSQL, but for this tutorial you will learn how to install PostgreSQL using Docker.

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

2. Persistent Store Database
============================

    In the :doc:`./intermediate` tutorial we implemented a file-based database as the persisting mechanism for the app. However, simple file based databases typically don't perform well in a web application environment, because of the possibility of many concurrent requests trying to access the file. In this section we'll refactor the Model to use an SQL database, rather than files.

    a. Add necessary dependencies:

    Persistent stores is an optional feature in Tethys, and requires that the ``sqlalchemy<2`` and ``psycopg2`` libraries are installed. Install these libraries using one of the following commands:

    .. code-block:: bash

            # conda: conda-forge channel strongly recommended
            conda install -c conda-forge "sqlalchemy<2" psycopg2

            # pip
            pip install "sqlalchemy<2" psycopg2

    Now add the new dependencies to your :file:`install.yml` as follows so that the app will work when installed in a new environment:

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


b. Open the ``app.py`` and define a new ``PersistentStoreDatabaseSetting`` by adding the ``persistent_store_settings`` method to your app class:

    .. code-block:: python

        from tethys_sdk.app_settings import PersistentStoreDatabaseSetting

        class App(TethysAppBase):
            """
            Tethys app class for Dam Inventory.
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
                        initializer='dam_inventory.model.init_primary_db',
                        required=True
                    ),
                )

                return ps_settings


Tethys provides the library SQLAlchemy as an interface with SQL databases. SQLAlchemy provides an Object Relational Mapper (ORM) API, which allows data models to be defined using Python and an object-oriented approach. With SQLAlchemy, you can harness the power of SQL databases without writing SQL. As a primer to SQLAlchemy ORM, we highly recommend you complete the `Unified Tutorial <https://docs.sqlalchemy.org/en/20/tutorial/index.html#unified-tutorial>`_.

c. Define a table called ``dams`` by creating a new class in ``model.py`` called ``Dam``:

    .. code-block:: python

        import json
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy import Column, Integer, Float, String
        from sqlalchemy.orm import sessionmaker

        from .app import App

        Base = declarative_base()


        # SQLAlchemy ORM definition for the dams table
        class Dam(Base):
            """
            SQLAlchemy Dam DB Model
            """
            __tablename__ = 'dams'

            # Columns
            id = Column(Integer, primary_key=True)
            latitude = Column(Float)
            longitude = Column(Float)
            name = Column(String)
            owner = Column(String)
            river = Column(String)
            date_built = Column(String)

    .. tip::

        **SQLAlchemy Data Models**: Each class in an SQLAlchemy data model defines a table in the database. The model you defined above consists of a single table called "dams", as denoted by the ``__tablename__`` property of the ``Dam`` class. The ``Dam`` class inherits from a ``Base`` class that we created in the previous lines from the ``declarative_base`` function. This inheritance notifies SQLAlchemy that the ``Dam`` class is part of the data model.

        The class defines seven other properties that are instances of SQLAlchemy ``Column`` class: *id*, *latitude*, *longitude*, *name*, *owner*, *river*, *date_built*. These properties define the columns of the "dams" table. The column type and options are defined by the arguments passed to the ``Column`` class. For example, the *latitude* column is of type ``Float`` while the *id* column is of type ``Integer``. The ``id`` column is flagged as the primary key for the table. IDs will be generated for each object when they are committed.

        This class is not only used to define the tables for your persistent store, it is also used to create new entries and query the database.

        For more information on Persistent Stores, see: :doc:`../../tethys_sdk/tethys_services/persistent_store`.

d. Replace the ``add_new_dam`` and ``get_all_dams`` functions in ``model.py`` with versions that use the SQL database instead of the files:

    .. code-block:: python

        def add_new_dam(location, name, owner, river, date_built):
            """
            Persist new dam.
            """
            # Convert GeoJSON to Python dictionary
            location_dict = json.loads(location)
            location_geometry = location_dict['geometries'][0]
            longitude = location_geometry['coordinates'][0]
            latitude = location_geometry['coordinates'][1]

            # Create new Dam record
            new_dam = Dam(
                latitude=latitude,
                longitude=longitude,
                name=name,
                owner=owner,
                river=river,
                date_built=date_built
            )

            # Get connection/session to database
            Session = App.get_persistent_store_database('primary_db', as_sessionmaker=True)
            session = Session()

            # Add the new dam record to the session
            session.add(new_dam)

            # Commit the session and close the connection
            session.commit()
            session.close()


        def get_all_dams():
            """
            Get all persisted dams.
            """
            # Get connection/session to database
            Session = App.get_persistent_store_database('primary_db', as_sessionmaker=True)
            session = Session()

            # Query for all dam records
            dams = session.query(Dam).all()
            session.close()

            return dams

    .. important::

        Don't forget to close your ``session`` objects when you are done. Eventually you will run out of connections to the database if you don't, which will cause unsightly errors.

e. Create a new function called ``init_primary_db`` at the bottom of ``model.py``. This function is used to initialize the database by creating the tables and adding any initial data.

    .. code-block:: python

        def init_primary_db(engine, first_time):
            """
            Initializer for the primary database.
            """
            # Create all the tables
            Base.metadata.create_all(engine)

            # Add data
            if first_time:
                # Make session
                Session = sessionmaker(bind=engine)
                session = Session()

                # Initialize database with two dams
                dam1 = Dam(
                    latitude=40.406624,
                    longitude=-111.529133,
                    name="Deer Creek",
                    owner="Reclamation",
                    river="Provo River",
                    date_built="April 12, 1993"
                )

                dam2 = Dam(
                    latitude=40.598168,
                    longitude=-111.424055,
                    name="Jordanelle",
                    owner="Reclamation",
                    river="Provo River",
                    date_built="1941"
                )

                # Add the dams to the session, commit, and close
                session.add(dam1)
                session.add(dam2)
                session.commit()
                session.close()

f. Refactor ``HomeMap`` controller in ``controllers.py`` to use the updated model methods:

    .. code-block:: python
        :emphasize-lines: 1, 10, 12, 20-21, 24-28

        @controller(name="home")
        class HomeMap(MapLayout):
            app = App
            base_template = f'{App.package}/base.html'
            map_title = 'Dam Inventory'
            map_subtitle = 'Tutorial'
            basemaps = ['OpenStreetMap', 'ESRI']
            show_properties_popup = True

            def compose_layers(self, request, map_view, *args, **kwargs):
                # Get list of dams and create dams MVLayer:
                dams = get_all_dams()
                features = []

                # Define GeoJSON Features
                for dam in dams:
                    dam_feature = {
                        'type': 'Feature',
                        'geometry': {
                            'type': 'Point',
                            'coordinates': [dam.longitude, dam.latitude],
                        },
                        'properties': {
                            'id': dam.id,
                            'name': dam.name,
                            'owner': dam.owner,
                            'river': dam.river,
                            'date_built': dam.date_built
                        }
                    }

            ...

g. Refactor the ``add_dam`` controller to use the updated model methods:

    .. code-block:: python
        :emphasize-lines: 1-2, 52-58

        @controller(url='dams/add')
        def add_dam(request):
            """
            Controller for the Add Dam page.
            """
            # Default Values
            name = ''
            owner = 'Reclamation'
            river = ''
            date_built = ''
            location = ''

            # Errors
            name_error = ''
            owner_error = ''
            river_error = ''
            date_error = ''
            location_error = ''

            # Handle form submission
            if request.POST and 'add-button' in request.POST:
                # Get values
                has_errors = False
                name = request.POST.get('name', None)
                owner = request.POST.get('owner', None)
                river = request.POST.get('river', None)
                date_built = request.POST.get('date-built', None)
                location = request.POST.get('geometry', None)

                # Validate
                if not name:
                    has_errors = True
                    name_error = 'Name is required.'

                if not owner:
                    has_errors = True
                    owner_error = 'Owner is required.'

                if not river:
                    has_errors = True
                    river_error = 'River is required.'

                if not date_built:
                    has_errors = True
                    date_error = 'Date Built is required.'

                if not location:
                    has_errors = True
                    location_error = 'Location is required.'

                if not has_errors:
                    add_new_dam(
                        location=location,
                        name=name,
                        owner=owner,
                        river=river,
                        date_built=date_built
                    )
                    return App.redirect(App.reverse('home'))

                messages.error(request, "Please fix errors.")

            ...

h. Refactor the ``list_dams`` controller to use updated model methods:

    .. code-block:: python
        :emphasize-lines: 1-2, 6, 12-13

        @controller(name='dams', url='dams')
        def list_dams(request):
            """
            Show all dams in a table view.
            """
            dams = get_all_dams()
            table_rows = []

            for dam in dams:
                table_rows.append(
                    (
                        dam.name, dam.owner,
                        dam.river, dam.date_built
                    )
                )

            ...

i. Remove references to workspace in ``build_map_extent_and_view`` method: 

.. code-block:: python
    :emphasize-lines: 1, 8

    def build_map_extent_and_view(self, request, *args, **kwargs):
        """
        Builds the default MVView and BBOX extent for the map.

        Returns:
            MVView, 4-list<float>: default view and extent of the project.
        """
        dams = get_all_dams()
        extent = self.compute_dams_extent(dams)

        ...

j. Refactor the ``compute_dams_extent`` method to use updated model methods:

.. code-block:: python
    :emphasize-lines: 8-9

    def compute_dams_extent(self, dams):
        """Compute the extent/bbox of the given dams."""
        lat_list = []
        lng_list = []

        # Define GeoJSON Features
        for dam in dams:
            lat_list.append(dam.latitude)
            lng_list.append(dam.longitude)
        
        ...

k. Add a **Persistent Store Service** to Tethys Portal:

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

l. Assign the new **Persistent Store Service** to the Dam Inventory App:

    a. Go to Tethys Portal Home in a web browser (e.g. http://localhost:8000/apps/)
    b. Select **Site Admin** from the drop down next to your username.
    c. Scroll down to the **Tethys Apps** section and select the **Installed App** link.
    d. Select the **Dam Inventory** link.
    e. Scroll down to the **Persistent Store Database Settings** section.
    f. Assign the **Persistent Store Service** that you created in Step 2 to the **primary_db** setting.
    g. Press **Save** to save the settings.

.. figure:: ../../images/tutorial/advanced/Assign_Persistent_Store_Service.png
    :width: 100%
    :align: center

m. Execute the **syncstores** command to create the tables in the Persistent Store database:

    .. code-block:: bash

        tethys syncstores dam_inventory

3. Use Custom Settings
======================

In the :doc:`./beginner` tutorial, we created a custom setting named `max_dams`. In this section, we'll show you how to use the custom setting in one of your controllers.

a. Modify the `add_dam` controller, such that it won't add a new dam if the `max_dams` limit has been reached:

    .. code-block:: python
        :emphasize-lines: 1-2, 57-75

        from .model import Dam
        from .app import App

        ...

        @controller(url='dams/add')
        def add_dam(request):
            """
            Controller for the Add Dam page.
            """
            # Default Values
            name = ''
            owner = 'Reclamation'
            river = ''
            date_built = ''
            location = ''

            # Errors
            name_error = ''
            owner_error = ''
            river_error = ''
            date_error = ''
            location_error = ''

            # Handle form submission
            if request.POST and 'add-button' in request.POST:
                # Get values
                has_errors = False
                name = request.POST.get('name', None)
                owner = request.POST.get('owner', None)
                river = request.POST.get('river', None)
                date_built = request.POST.get('date-built', None)
                location = request.POST.get('geometry', None)

                # Validate
                if not name:
                    has_errors = True
                    name_error = 'Name is required.'

                if not owner:
                    has_errors = True
                    owner_error = 'Owner is required.'

                if not river:
                    has_errors = True
                    river_error = 'River is required.'

                if not date_built:
                    has_errors = True
                    date_error = 'Date Built is required.'

                if not location:
                    has_errors = True
                    location_error = 'Location is required.'

                if not has_errors:
                    # Get value of max_dams custom setting
                    max_dams = App.get_custom_setting('max_dams')

                    # Query database for count of dams
                    Session = App.get_persistent_store_database('primary_db', as_sessionmaker=True)
                    session = Session()
                    num_dams = session.query(Dam).count()

                    # Only add the dam if custom setting doesn't exist or we have not exceed max_dams
                    if not max_dams or num_dams < max_dams:
                        add_new_dam(
                            location=location,
                            name=name,
                            owner=owner,
                            river=river,
                            date_built=date_built
                        )
                    else:
                        messages.warning(request, 'Unable to add dam "{0}", because the inventory is full.'.format(name))

                    return App.redirect(reverse('home'))

                messages.error(request, "Please fix errors.")

            ...


    .. tip::

        For more information on app settings, see :doc:`../../tethys_sdk/app_settings`.

4. App Permissions
==================

By default, any user logged into the app can access any part of it. You may want to restrict access to certain areas of the app to privileged users. This can be done using the :doc:`../../tethys_sdk/permissions`. Let's modify the app so that only admin users of the app can add dams to the app.

a. Define permissions for the app by adding the ``permissions`` method to the app class in the ``app.py``:

    .. code-block:: python

        ...

        from tethys_sdk.permissions import Permission, PermissionGroup

        class App(TethysAppBase):
            """
            Tethys app class for Dam Inventory.
            """
            ...

            def permissions(self):
                """
                Define permissions for the app.
                """
                add_dams = Permission(
                    name='add_dams',
                    description='Add dams to inventory'
                )

                admin = PermissionGroup(
                    name='admin',
                    permissions=(add_dams,)
                )

                permissions = (admin,)

                return permissions

b. Protect the Add Dam view with the ``add_dams`` permission by setting the ``permissions_required`` argument of the ``controller`` decorator:

    .. code-block:: python
        :emphasize-lines: 1

        @controller(url='dams/add', permission_required='add_dams')
        def add_dam(request):
            """
            Controller for the Add Dam page.
            """
            ...

c. Add a context variable called ``can_add_dams`` to the context of each controller with the value of the return value of the ``has_permission`` function:

    .. code-block:: python
        :emphasize-lines: 1, 14-22, 36, 51

        from tethys_sdk.permissions import has_permission

        ...

        @controller(name="home")
        class HomeMap(MapLayout):
            app = App
            base_template = f'{App.package}/base.html'
            map_title = 'Dam Inventory'
            map_subtitle = 'Tutorial'
            basemaps = ['OpenStreetMap', 'ESRI']
            show_properties_popup = True

            def get_context(self, request, context, *args, **kwargs):
                # Add custom context variables
                context.update({
                    'can_add_dams': has_permission(request, 'add_dams'),
                })

                # Call the MapLayout get_context method to initialize the map view
                context = super().get_context(request, context, *args, **kwargs)
                return context

            ...


        @controller(url='dams/add', permission_required='add_dams')
        def add_dam(request):
            """
            Controller for the Add Dam page.
            """
            ...

            context = {
                ...
                'can_add_dams': has_permission(request, 'add_dams')
            }

            return App.render(request, 'add_dam.html', context)


        @controller(name='dams', url='dams')
        def list_dams(request):
            """
            Show all dams in a table view.
            """
            ...

            context = {
                ...
                'can_add_dams': has_permission(request, 'add_dams')
            }
            return App.render(request, 'list_dams.html', context)

d. Use the ``can_add_dams`` variable to determine whether to show or hide the header button and navigation link to the Add Dam View in ``base.html``:

    .. code-block:: html+django
        :emphasize-lines: 11, 15

        {% block header_buttons %}
          {% url tethys_app|url:'home' as home_url %}
          {% url tethys_app|url:'add_dam' as add_dam_url %}
          {% url tethys_app|url:'dams' as list_dam_url %}
          <div class="header-button glyphicon-button">
            <a href="{{ home_url }}" title="Map"><i class="bi bi-map"></i></a>
          </div>
          <div class="header-button glyphicon-button">
            <a href="{{ list_dam_url }}" title="Dams"><i class="bi bi-list-ul"></i></a>
          </div>
          {% if can_add_dams %}
          <div class="header-button glyphicon-button">
            <a href="{{ add_dam_url }}" title="Add Dam"><i class="bi bi-plus-circle"></i></a>
          </div>
          {% endif %}
        {% endblock %}

    .. code-block:: html+django
        :emphasize-lines: 8, 10

        {% block app_navigation_items %}
          {% url tethys_app|url:'home' as home_url %}
          {% url tethys_app|url:'add_dam' as add_dam_url %}
          {% url tethys_app|url:'dams' as list_dam_url %}
          <li class="nav-item title">Navigation</li>
          <li class="nav-item"><a class="nav-link{% if request.path == home_url %} active{% endif %}" href="{{ home_url }}">Home</a></li>
          <li class="nav-item"><a class="nav-link{% if request.path == list_dam_url %} active{% endif %}" href="{{ list_dam_url }}">Dams</a></li>
          {% if can_add_dams %}
          <li class="nav-item"><a class="nav-link{% if request.path == add_dam_url %} active{% endif %}" href="{{ add_dam_url }}">Add Dam</a></li>
          {% endif %}
        {% endblock %}

e. The ``admin`` user of Tethys is a superuser and has all permissions. To test the permissions, create two new users: one with the ``admin`` permissions group and one without it. Then login with these users:

    a. Go to Tethys Portal Home in a web browser (e.g. http://localhost:8000/apps/)
    b. Select **Site Admin** from the drop down next to your username.
    c. Scroll to the **Authentication and Authorization** section.
    d. Select the **Users** link.
    e. Press the **Add User** button.
    f. Enter "diadmin" as the username and enter a password. Take note of the password for later.
    g. Press the **Save and continue editing** button.
    h. Scroll down to the **Groups** section.
    i. Select the **dam_inventory:admin** group and press the right arrow to add the user to that group.
    j. Press the **Save and add another** button.
    k. Enter "diviewer" as the username and enter a password. Take note of the password for later. **DO NOT add "diviewer" user to any groups.**
    l. Press the **Save** button.

f. Log in with each user account. If the permission has been applied correctly, "diviewer" should not be able to see the Add Dam link and should be redirected if the Add Dam view is linked to directly. "diadmin" should be able to add dams.

.. tip::

    For more details on Permissions, see: :doc:`../../tethys_sdk/permissions`.

5. Persistent Store Related Tables
==================================

Add Flood Hydrograph table

a. Define two new tables to ``model.py`` for storing the hydrograph and hydrograph points. Also, establish relationships between the tables. Each dam will have only one hydrograph and each hydrograph can have multiple hydrograph points.

    .. code-block:: python

        from sqlalchemy import ForeignKey
        from sqlalchemy.orm import relationship

        ...

        class Dam(Base):
            """
            SQLAlchemy Dam DB Model
            """
            ...

            # Relationships
            hydrograph = relationship('Hydrograph', back_populates='dam', uselist=False)


        class Hydrograph(Base):
            """
            SQLAlchemy Hydrograph DB Model
            """
            __tablename__ = 'hydrographs'

            # Columns
            id = Column(Integer, primary_key=True)
            dam_id = Column(ForeignKey('dams.id'))

            # Relationships
            dam = relationship('Dam', back_populates='hydrograph')
            points = relationship('HydrographPoint', back_populates='hydrograph')


        class HydrographPoint(Base):
            """
            SQLAlchemy Hydrograph Point DB Model
            """
            __tablename__ = 'hydrograph_points'

            # Columns
            id = Column(Integer, primary_key=True)
            hydrograph_id = Column(ForeignKey('hydrographs.id'))
            time = Column(Integer)  #: hours
            flow = Column(Float)  #: cfs

            # Relationships
            hydrograph = relationship('Hydrograph', back_populates='points')

b. Execute **syncstores** command again to add the new tables to the database:

    .. code-block:: bash

        tethys syncstores dam_inventory


6. File Upload
==============

CSV File Upload
Create new page for uploading the hydrograph.

a. New Model function

    .. code-block:: python

        def assign_hydrograph_to_dam(dam_id, hydrograph_file):
            """
            Parse hydrograph file and add to database, assigning to appropriate dam.
            """
            # Parse file
            hydro_points = []

            try:
                for line in hydrograph_file:
                    line = line.decode('utf-8')
                    sline = line.split(',')

                    try:
                        time = int(sline[0])
                        flow = float(sline[1])
                        hydro_points.append(HydrographPoint(time=time, flow=flow))
                    except ValueError:
                        continue

                if len(hydro_points) > 0:
                    Session = App.get_persistent_store_database('primary_db', as_sessionmaker=True)
                    session = Session()

                    # Get dam object
                    dam = session.query(Dam).get(int(dam_id))

                    # Overwrite old hydrograph
                    hydrograph = dam.hydrograph

                    # Create new hydrograph if not assigned already
                    if not hydrograph:
                        hydrograph = Hydrograph()
                        dam.hydrograph = hydrograph

                    # Remove old points if any
                    for hydro_point in hydrograph.points:
                        session.delete(hydro_point)

                    # Assign points to hydrograph
                    hydrograph.points = hydro_points

                    # Persist to database
                    session.commit()
                    session.close()

            except Exception as e:
                # Careful not to hide error. At the very least log it to the console
                print(e)
                return False

            return True

b. New Template: ``assign_hydrograph.html``

    .. code-block:: html+django

        {% extends tethys_app.package|add:"/base.html" %}
        {% load tethys %}

        {% block app_content %}
        <h1>Assign Hydrograph</h1>
        <p>Select a dam and a hydrograph file to assign to that dam. The file should be a csv with two columns: time (hours) and flow (cfs).</p>
        <form id="add-hydrograph-form" method="post" enctype="multipart/form-data">
            {% csrf_token %}
            {% gizmo dam_select_input %}
            <div class="form-group{% if hydrograph_file_error %} has-error{% endif %}">
            <label class="control-label">Hydrograph File</label>
            <input type="file" name="hydrograph-file">
            {% if hydrograph_file_error %}<p class="help-block">{{ hydrograph_file_error }}</p>{% endif %}
            </div>
        </form>
        {% endblock %}

        {% block app_actions %}
        {% gizmo cancel_button %}
        {% gizmo add_button %}
        {% endblock %}


c. New Controller

    .. code-block:: python

        from .model import assign_hydrograph_to_dam
        from .app import App

        ...

        @controller(url='hydrographs/assign')
        def assign_hydrograph(request):
            """
            Controller for the Add Hydrograph page.
            """
            # Get dams from database
            Session = App.get_persistent_store_database('primary_db', as_sessionmaker=True)
            session = Session()
            all_dams = session.query(Dam).all()

            # Defaults
            dam_select_options = [(dam.name, dam.id) for dam in all_dams]
            selected_dam = None
            hydrograph_file = None

            # Errors
            dam_select_errors = ''
            hydrograph_file_error = ''

            # Case where the form has been submitted
            if request.POST and 'add-button' in request.POST:
                # Get Values
                has_errors = False
                selected_dam = request.POST.get('dam-select', None)

                if not selected_dam:
                    has_errors = True
                    dam_select_errors = 'Dam is Required.'

                # Get File
                if request.FILES and 'hydrograph-file' in request.FILES:
                    # Get a list of the files
                    hydrograph_file = request.FILES.getlist('hydrograph-file')

                if not hydrograph_file and len(hydrograph_file) > 0:
                    has_errors = True
                    hydrograph_file_error = 'Hydrograph File is Required.'

                if not has_errors:
                    # Process file here
                    success = assign_hydrograph_to_dam(selected_dam, hydrograph_file[0])

                    # Provide feedback to user
                    if success:
                        messages.info(request, 'Successfully assigned hydrograph.')
                    else:
                        messages.info(request, 'Unable to assign hydrograph. Please try again.')
                    return App.redirect(App.reverse('home'))

                messages.error(request, "Please fix errors.")

            dam_select_input = SelectInput(
                display_text='Dam',
                name='dam-select',
                multiple=False,
                options=dam_select_options,
                initial=selected_dam,
                error=dam_select_errors
            )

            add_button = Button(
                display_text='Add',
                name='add-button',
                icon='plus-square',
                style='success',
                attributes={'form': 'add-hydrograph-form'},
                submit=True
            )

            cancel_button = Button(
                display_text='Cancel',
                name='cancel-button',
                href=App.reverse('home')
            )

            context = {
                'dam_select_input': dam_select_input,
                'hydrograph_file_error': hydrograph_file_error,
                'add_button': add_button,
                'cancel_button': cancel_button,
                'can_add_dams': has_permission(request, 'add_dams')
            }

            session.close()

            return App.render(request, 'assign_hydrograph.html', context)

d. Update header buttons and navigation

    .. code-block:: html+django
        :emphasize-lines: 5, 16-18

        {% block header_buttons %}
          {% url tethys_app|url:'home' as home_url %}
          {% url tethys_app|url:'add_dam' as add_dam_url %}
          {% url tethys_app|url:'dams' as list_dam_url %}
          {% url tethys_app|url:'assign_hydrograph' as assign_hydrograph_url %}
          <div class="header-button glyphicon-button">
            <a href="{{ home_url }}" title="Map"><i class="bi bi-map"></i></a>
          </div>
          <div class="header-button glyphicon-button">
            <a href="{{ list_dam_url }}" title="Dams"><i class="bi bi-list-ul"></i></a>
          </div>
          {% if can_add_dams %}
          <div class="header-button glyphicon-button">
            <a href="{{ add_dam_url }}" title="Add Dam"><i class="bi bi-plus-circle"></i></a>
          </div>
          <div class="header-button glyphicon-button">
            <a href="{{ assign_hydrograph_url }}" title="Assign Hydrograph"><i class="bi bi-graph-up"></i></a>
          </div>
          {% endif %}
        {% endblock %}

    .. code-block:: html+django
        :emphasize-lines: 5, 11

        {% block app_navigation_items %}
          {% url tethys_app|url:'home' as home_url %}
          {% url tethys_app|url:'add_dam' as add_dam_url %}
          {% url tethys_app|url:'dams' as list_dam_url %}
          {% url tethys_app|url:'assign_hydrograph' as assign_hydrograph_url %}
          <li class="nav-item title">Navigation</li>
          <li class="nav-item"><a class="nav-link{% if request.path == home_url %} active{% endif %}" href="{{ home_url }}">Home</a></li>
          <li class="nav-item"><a class="nav-link{% if request.path == list_dam_url %} active{% endif %}" href="{{ list_dam_url }}">Dams</a></li>
          {% if can_add_dams %}
          <li class="nav-item"><a class="nav-link{% if request.path == add_dam_url %} active{% endif %}" href="{{ add_dam_url }}">Add Dam</a></li>
          <li class="nav-item"><a class="nav-link{% if request.path == assign_hydrograph_url %} active{% endif %}" href="{{ assign_hydrograph_url }}">Assign Hydrograph</a></li>
          {% endif %}
        {% endblock %}

.. _sample_hydrographs:

e. Test upload with these files:

    :download:`Sample Hydrograph CSVs <./hydrographs.zip>`

7. URL Variables and Plotting
=============================

Create a new page with hydrograph plotted for selected Dam

a. Add necessary dependencies:

    In order to plot the hydrograph, you will need to install the ``plotly`` library. Install this library using one of the following commands:

    .. code-block:: bash

            # conda: conda-forge channel strongly recommended
            conda install -c conda-forge plotly

            # pip
            pip install plotly

    Now add the new dependencies to your :file:`install.yml` as follows so that the app will work when installed in a new environment:

    .. code-block:: yaml
        :emphasize-lines: 17

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
            - plotly

        pip:

        npm:

        post:

b. Create Template ``hydrograph.html``

    .. code-block:: html+django

        {% extends tethys_app.package|add:"/base.html" %}
        {% load tethys %}

        {% block app_navigation_items %}
        <li class="nav-item title">App Navigation</li>
        <li class="nav-item "><a class="nav-link" href="{% url tethys_app|url:'dams' %}">Back</a></li>
        {% endblock %}

        {% block app_content %}
        {% gizmo hydrograph_plot %}
        {% endblock %}

c. Create ``helpers.py``

    .. code-block:: python

        from .app import App
        from .model import Hydrograph


        def create_hydrograph(hydrograph_id):
            """
            Generates a plotly view of a hydrograph.
            """
            # Get objects from database
            Session = App.get_persistent_store_database('primary_db', as_sessionmaker=True)
            session = Session()
            hydrograph = session.query(Hydrograph).get(int(hydrograph_id))
            dam = hydrograph.dam
            time = []
            flow = []
            for hydro_point in hydrograph.points:
                time.append(hydro_point.time)
                flow.append(hydro_point.flow)

            # Build up Plotly plot
            data =[
                dict(
                    x=time,
                    y=flow,
                    name=f'Hydrograph for {dam.name}',
                    line={'color': '#0080ff', 'width': 4, 'shape': 'spline'},
                )
            ]
            layout = {
                'title': f'Hydrograph for {dam.name}',
                'xaxis': {'title': 'Time (hr)'},
                'yaxis': {'title': 'Flow (cfs)'},
            }
            session.close()
            return data, layout

d. Create Controller

    .. code-block:: python

        from tethys_sdk.gizmos import PlotlyView
        from .helpers import create_hydrograph

        ...

        @controller(url='hydrographs/{hydrograph_id}')
        def hydrograph(request, hydrograph_id):
            """
            Controller for the Hydrograph Page.
            """
            data, layout = create_hydrograph(hydrograph_id)
            figure = {'data': data, 'layout': layout}
            hydrograph_plot = PlotlyView(figure, height="500px", width="100%")
            context = {
                'hydrograph_plot': hydrograph_plot,
                'can_add_dams': has_permission(request, 'add_dams')
            }
            return App.render(request, 'hydrograph.html', context)

.. tip::

    For more information about plotting in Tethys apps, see :doc:`../../tethys_sdk/gizmos/plotly_view`, :doc:`../../tethys_sdk/gizmos/bokeh_view`, and :doc:`../../tethys_sdk/gizmos/plot_view`.

e. Add ``get_hydrograph`` helper function to ``model.py``

    .. code-block:: python

        def get_hydrograph(dam_id):
            """
            Get hydrograph id from dam id.
            """
            Session = App.get_persistent_store_database('primary_db', as_sessionmaker=True)
            session = Session()

            # Query if hydrograph exists for dam
            hydrograph = session.query(Hydrograph).filter_by(dam_id=dam_id).first()
            session.close()

            if hydrograph:
                return hydrograph.id
            else:
                return None

f. Modify ``list_dams`` controller (and add needed imports):

    .. code-block:: python
        :emphasize-lines: 14-20, 16, 26, 31

        from django.utils.html import format_html
        from .model import get_hydrograph
        ...

        @controller(name='dams', url='dams')
        def list_dams(request):
            """
            Show all dams in a table view.
            """
            dams = get_all_dams()
            table_rows = []

            for dam in dams:
                hydrograph_id = get_hydrograph(dam.id)
                if hydrograph_id:
                    url = App.reverse('hydrograph', kwargs={'hydrograph_id': hydrograph_id})
                    dam_hydrograph = format_html('<a class="btn btn-primary" href="{}">Hydrograph Plot</a>'.format(url))
                else:
                    dam_hydrograph = format_html('<a class="btn btn-primary disabled" title="No hydrograph assigned" '
                                                'style="pointer-events: auto;">Hydrograph Plot</a>')

                table_rows.append(
                    (
                        dam.name, dam.owner,
                        dam.river, dam.date_built,
                        dam_hydrograph
                    )
                )

            dams_table = DataTableView(
                column_names=('Name', 'Owner', 'River', 'Date Built', 'Hydrograph'),
                rows=table_rows,
                searching=False,
                orderClasses=False,
                lengthMenu=[[10, 25, 50, -1], [10, 25, 50, "All"]],
            )

            context = {
                'dams_table': dams_table,
                'can_add_dams': has_permission(request, 'add_dams')
            }

            return App.render(request, 'list_dams.html', context)

g. Test by going to the Dams page and clicking on the new ``Hydrograph Plot`` button in the table for a dam that has already been assigned a hydrograph.

8. Dynamic Hydrograph Plot in Pop-Ups
=====================================

Add Hydrographs plot button to map pop-ups.

a. Update the ``HomeMap`` controller to include the hydrograph plot button in the pop-up:

    .. code-block:: python
        :emphasize-lines: 9, 13-35

        @controller(name="home")
        class HomeMap(MapLayout):
            app = App
            base_template = f'{App.package}/base.html'
            map_title = 'Dam Inventory'
            map_subtitle = 'Tutorial'
            basemaps = ['OpenStreetMap', 'ESRI']
            show_properties_popup = True
            plot_slide_sheet = True

            ...

            def get_plot_for_layer_feature(self, request, layer_name, feature_id, layer_data, feature_props, *args, **kwargs):
                """
                Retrieves plot data for given feature on given layer.

                Args:
                    layer_name (str): Name/id of layer.
                    feature_id (str): ID of feature.
                    layer_data (dict): The MVLayer.data dictionary.
                    feature_props (dict): The properties of the selected feature.

                Returns:
                    str, list<dict>, dict: plot title, data series, and layout options, respectively.
                """
                Session = App.get_persistent_store_database('primary_db', as_sessionmaker=True)
                session = Session()
                dam = session.query(Dam).get(int(feature_id))

                if dam.hydrograph:
                    data, layout = create_hydrograph(dam.hydrograph.id)
                else:
                    data, layout = [], {}
                session.close()
                return f'Hydrograph for {dam.name}', data, layout


9. Solution
============

This concludes the Advanced Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-dam_inventory>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-dam_inventory
    cd tethysapp-dam_inventory
    git checkout -b advanced-solution advanced-|version|
