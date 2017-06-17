*****************
Advanced Concepts
*****************

**Last Updated:** June 2017

This tutorial introduces advanced concepts for Tethys developers. The topics covered include:

* Tethys Services API
* PersistentStores API
* Gizmo JavaScript APIs
* JavaScript and AJAX
* Permissions API
* Advanced HTML forms - File Upload
* Plot View Gizmos
* REST API

0. Start From Intermediate Solution (Optional)
==============================================

If you wish to use the intermediate solution as a starting point:

::

    $ git clone https://github.com/tethysplatform/tethysapp-dam_inventory.git
    $ cd tethysapp-dam_inventory
    $ git checkout intermediate-solution

1. Persistent Store Database
============================

In the :doc:`./intermediate` tutorial we implemented a file-based database as the persisting mechanism for the app. However, simple file based databases typically don't perform well in a web application environment, because of the possibility of many concurrent requests trying to access the file. In this section we'll refactor the Model to use an SQL database, rather than files.

a. Create a ``PersistentStoreDatabaseSetting``, which can be assigned a connection to the database. Open the ``app.py`` and define a new ``PersistentStoreDatabaseSetting`` by adding the ``persistent_store_settings`` method to your app class:

::

    from tethys_sdk.app_settings import PersistentStoreDatabaseSetting

    class DamInventory(TethysAppBase):
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


Next, we need to define the tables of the database. Tethys provides the library SQLAlchemy as an interface with SQL databases. SQLAlchemy provides an Object Relational Mapper (ORM) API, which allows data models to be defined using Python and an object-oriented approach. In other words, you are able to harness the power of SQL databases without writing SQL. As a primer to SQLAlchemy ORM, we highly recommend you complete the `Object Relational Tutorial <http://docs.sqlalchemy.org/en/latest/orm/tutorial.html>`_.

b. Define a table called ``dams`` by creating a new class in ``model.py`` called ``Dam``:

::

    import json
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import Column, Integer, Float, String
    from sqlalchemy.orm import sessionmaker

    from .app import DamInventory as app

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

c. Refactor the ``add_new_dam`` and ``get_all_dams`` functions in ``model.py`` to use the SQL database instead of the files:

::

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
        engine = app.get_persistent_store_database('primary_db')
        Session = sessionmaker(bind=engine)
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
        engine = app.get_persistent_store_database('primary_db')
        Session = sessionmaker(bind=engine)
        session = Session()

        # Query for all dam records
        dams = session.query(Dam).all()
        session.close()

        return dams

d. Create a new function called ``init_primary_db`` at the bottom of ``model.py``. This function is used to initialize the data database by creating the tables and adding any initial data.

::

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



e. Refactor ``home`` controller in ``controllers.py`` to use new model objects:

::

    @login_required()
    def home(request):
        """
        Controller for the app home page.
        """
        # Get list of dams and create dams MVLayer:
        dams = get_all_dams()
        features = []
        lat_list = []
        lng_list = []

        for dam in dams:
            lat_list.append(dam.latitude)
            lng_list.append(dam.longitude)

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
            features.append(dam_feature)

        ...

f. Add **Persistent Store Service** to Tethys Portal:

    a. Go to Tethys Portal Home in a web browser (e.g. http://localhost:8000/apps/)
    b. Select **Site Admin** from the drop down next to your username.
    c. Scroll down to **Tethys Services** section and select **Persistent Store Services** link.
    d. Click on the **Add Persistent Store Service** button.
    e. Give the **Persistent Store Service** a name and fill out the connection information.

.. important::

    The username and password for the persistent store service must be a superuser to use spatial persistent stores.

g. Assign **Persistent Store Service** to Dam Inventory App:

    a. Go to Tethys Portal Home in a web browser (e.g. http://localhost:8000/apps/)
    b. Select **Site Admin** from the drop down next to your username.
    c. Scroll down to **Tethys Apps** section and select **Installed App** link.
    d. Select the **Dam Inventory** link.
    e. Scroll down to the **Persistent Store Database Settings** section.
    f. Assign the **Persistent Store Service** that you created in Step 4 to the **primary_db**.

h. Execute **syncstores** command to initialize Persistent Store database:

    ::

        (tethys) $ tethys syncstores dam_inventory

2. Use Custom Settings
======================

In the :doc:`./beginner` tutorial, we created a custom setting named `max_dams`. In this section, we'll show you how to use the custom setting in one of your controllers.

a. Modify the `add_dam` controller, such that it won't add a new dam if the `max_dams` limit has been reached:

::

    from .model import add_new_dam, get_all_dams, Dam
    from .app import DamInventory as app

    ...

    @login_required()
    def add_dam(request):
        """
        Controller for the Add Dam page.
        """

        ...

        # Handle form submission
        if request.POST and 'add-button' in request.POST:

            ...

            if not has_errors:
                # Get value of max_dams custom setting
                max_dams = app.get_custom_setting('max_dams')

                # Query database for count of dams
                Session = app.get_persistent_store_database('primary_db', as_sessionmaker=True)
                session = Session()
                num_dams = session.query(Dam).count()

                # Only add the dam if we have not exceed max_dams
                if num_dams < max_dams:
                    add_new_dam(location=location, name=name, owner=owner, river=river, date_built=date_built)
                else:
                    messages.warning(request, 'Unable to add dam "{0}", because the inventory is full.'.format(name))
                return redirect(reverse('dam_inventory:home'))

            messages.error(request, "Please fix errors.")

        ...


.. tip::

    For more information on app settings, see :doc:`../../tethys_sdk/app_settings`.


3. Use JavaScript APIs
======================

JavaScript is the programming language that is used to program web browsers. You can use JavaScript in you Tethys apps to enrich the user experience and add dynamic effects. Many of the Tethys Gizmos include JavaScript APIs to allow you to access the underlying JavaScript objects and library to customize them. In this section, we'll use the JavaScript API of the Map View gizmo to add pop-ups to the map whenever the users clicks on one of the dams.

a. Modify the MVLayer in the ``home`` controller to make the layer selectable:

::

    ...

    dams_layer = MVLayer(
        source='GeoJSON',
        options=dams_feature_collection,
        legend_title='Dams',
        layer_options={
            'style': {
                'image': {
                    'circle': {
                        'radius': 10,
                        'fill': {'color':  '#d84e1f'},
                        'stroke': {'color': '#ffffff', 'width': 1},
                    }
                }
            }
        },
        feature_selection=True
    )

    ...



b. Create a new file called ``/public/js/map.js`` and add the following contents:

::

    $(function()
    {
        // Create new Overlay with the #popup element
        var popup = new ol.Overlay({
            element: document.getElementById('popup')
        });

        // Get the Open Layers map object from the Tethys MapView
        var map = TETHYS_MAP_VIEW.getMap();

        // Get the Select Interaction from the Tethys MapView
        var select_interaction = TETHYS_MAP_VIEW.getSelectInteraction();

        // Add the popup overlay to the map
        map.addOverlay(popup);

        // When selected, call function to display properties
        select_interaction.getFeatures().on('change:length', function(e)
        {
            var popup_element = popup.getElement();

            if (e.target.getArray().length > 0)
            {
                // this means there is at least 1 feature selected
                var selected_feature = e.target.item(0); // 1st feature in Collection

                // Get coordinates of the point to set position of the popup
                var coordinates = selected_feature.getGeometry().getCoordinates();

                var popup_content = '<div class="dam-popup">' +
                                        '<p><b>' + selected_feature.get('name') + '</b></p>' +
                                        '<table class="table  table-condensed">' +
                                            '<tr>' +
                                                '<th>Owner:</th>' +
                                                '<td>' + selected_feature.get('owner') + '</td>' +
                                            '</tr>' +
                                            '<tr>' +
                                                '<th>River:</th>' +
                                                '<td>' + selected_feature.get('river') + '</td>' +
                                            '</tr>' +
                                            '<tr>' +
                                                '<th>Date Built:</th>' +
                                                '<td>' + selected_feature.get('date_built') + '</td>' +
                                            '</tr>' +
                                        '</table>' +
                                    '</div>';

                // Clean up last popup and reinitialize
                $(popup_element).popover('destroy');
                popup.setPosition(coordinates);

                $(popup_element).popover({
                  'placement': 'top',
                  'animation': true,
                  'html': true,
                  'content': popup_content
                });
                $(popup_element).popover('show');
            } else {
                // remove pop up when selecting nothing on the map
                $(popup_element).popover('destroy');
            }
        });
    });

c. Open ``/templates/dam_inventory/home.html``, add a new ``div`` element to the ``app_content`` area of the page with an id ``popup``, and load the ``map.js`` script to the bottom of the page:

::

    ...

    {% block app_content %}
      {% gizmo dam_inventory_map %}
      <div id="popup"></div>
    {% endblock %}

    ...

    {% block scripts %}
      {{ block.super }}
      <script src="{% static 'dam_inventory/js/map.js' %}" type="text/javascript"></script>
    {% endblock %}

d. Open ``public/css/map.css`` and add the following contents:

::

    ...

    .popover-content {
        width: 240px;
    }

4. App Permissions
==================

By default, any user logged into the app can access any part of it. You may want to restrict access to certain areas of the app to privileged users. This can be done using the :doc:`../../tethys_sdk/permissions`. Let's modify the app so that only admin users of the app can add dams to the app.

a. Define permissions for the app by adding the ``permissions`` method to the app class in the ``app.py``:

::

    ...

    from tethys_sdk.permissions import Permission, PermissionGroup

    class DamInventory(TethysAppBase):
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

b. Protect the Add Dam view with the ``add_dams`` permission by replacing the ``login_required`` decorator with the ``permission_required`` decorator to the ``add_dams`` controller:

::

    from tethys_sdk.permissions import permission_required

    ...

    @permission_required('add_dams')
    def add_dam(request):
        """
        Controller for the Add Dam page.
        """
        ...

c. Add a context variable called ``can_add_dams`` to the context of each controller with the value of the return value of the ``has_permission`` function:

::

    from tethys_sdk.permissions import permission_required, has_permission

    @login_required()
    def home(request):
        """
        Controller for the app home page.
        """
        ...

        context = {
            ...
            'can_add_dams': has_permission(request, 'add_dams')
        }

        return render(request, 'dam_inventory/home.html', context)


    @permission_required('add_dams')
    def add_dam(request):
        """
        Controller for the Add Dam page.
        """
        ...

        context = {
            ...
            'can_add_dams': has_permission(request, 'add_dams')
        }

        return render(request, 'dam_inventory/add_dam.html', context)


    @login_required()
    def list_dams(request):
        """
        Show all dams in a table view.
        """
        dams = get_all_dams()
        context = {
            ...
            'can_add_dams': has_permission(request, 'add_dams')
        }
        return render(request, 'dam_inventory/list_dams.html', context)

d. Use the ``can_add_dams`` variable to determine whether to show or hide the navigation link to the Add Dam View in ``base.html``:

::

    {% block app_navigation_items %}
      ...
      <li class="{% if request.path == home_url %}active{% endif %}"><a href="{{ home_url }}">Home</a></li>
      <li class="{% if request.path == list_dam_url %}active{% endif %}"><a href="{{ list_dam_url }}">Dams</a></li>
      {% if can_add_dams %}
      <li class="{% if request.path == add_dam_url %}active{% endif %}"><a href="{{ add_dam_url }}">Add Dam</a></li>
      {% endif %}
    {% endblock %}

e. Use the ``can_add_dams`` variable to determine whether to show or hide the "Add Dam" button in ``home.html``:

::

    {% block app_actions %}
      {% if can_add_dams %}
        {% gizmo add_dam_button %}
      {% endif %}
    {% endblock %}

f. The ``admin`` user of Tethys is a superuser and has all permissions. To test the permissions, create two new users: one with the ``admin`` permissions group and one without it. Then login with these users:

    a. Go to Tethys Portal Home in a web browser (e.g. http://localhost:8000/apps/)
    b. Select **Site Admin** from the drop down next to your username.
    c. Scroll to the **Authentication and Authorization** section.
    d. Select the **Users** link.
    e. Press the **Add User** button.
    f. Enter "diadmin" as the username and enter a password. Take note of the password for later.
    g. Press the **Save** button.
    h. Scroll down to the **Groups** section.
    i. Select the **dam_inventory:admin** group and press the right arrow to add the user to that group.
    j. Press the **Save** button.
    k. Repeat steps e-f for user named "diviewer". DO NOT add "diviewer" user to any groups.
    l. Press the **Save** button.

g. Log in each user. If the permission has been applied correctly, "diviewer" should not be able to see the Add Dam link and should be redirected if the Add Dam view is linked to directly. "diadmin" should be able to add dams.

.. tip::

    For more details on Permissions, see: :doc:`../../tethys_sdk/permissions`.

5. Persistent Store Related Tables
==================================

Add Flood Hydrograph table

a. Define two new tables to ``models.py`` for storing the hydrograph and hydrograph points. Also, establish relationships between the tables. Each dam will have only one hydrograph and each hydrograph can have multiple hydrograph points.

::

    from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
    from sqlalchemy.orm import sessionmaker, relationship

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
        datetime = Column(DateTime)
        flow = Column(Float)

        # Relationships
        hydrograph = relationship('Hydrograph', back_populates='points')

b. Execute **syncstores** command again to add the new tables to the database:

    ::

        (tethys) $ tethys syncstores dam_inventory


6. File Upload
==============

CSV File Upload
Create new page for uploading the hydrograph.

a. New Template

::

    {% extends "dam_inventory/base.html" %}
    {% load tethys_gizmos %}

    {% block app_content %}
      <h1>Add Hydrograph</h1>
      <form id="add-hydrograph-form" method="post" enctype="multipart/form-data">
        {% csrf_token %}
        <p>Select a file to upload. File should be a csv with two columns: time and flow.</p>
        <input type="file" name="file">
      </form>
    {% endblock %}

    {% block app_actions %}
      {% gizmo cancel_button %}
      {% gizmo add_button %}
    {% endblock %}

b. New Controller

::



c. New UrlMap

::

    class DamInventory(TethysAppBase):
        """
        Tethys app class for Dam Inventory.
        """

        ...

        def url_maps(self):
            """
            Add controllers
            """
            UrlMap = url_map_maker(self.root_url)

            url_maps = (
                UrlMap(
                    name='home',
                    url='dam-inventory',
                    controller='dam_inventory.controllers.home'
                ),
                UrlMap(
                    name='add_dam',
                    url='dam-inventory/dams/add',
                    controller='dam_inventory.controllers.add_dam'
                ),
                UrlMap(
                    name='dams',
                    url='dam-inventory/dams',
                    controller='dam_inventory.controllers.list_dams'
                ),
                UrlMap(
                    name='add_hydrograph',
                    url='dam-inventory/hydrographs/add',
                    controller='dam_inventory.controllers.add_hydrograph'
                )
            )

            return url_maps

d. Update navigation

::

    {% block app_navigation_items %}
      <li class="title">App Navigation</li>
      ...
      {% url 'dam_inventory:add_hydrograph' as add_hydrograph_url %}
      ...
      <li class="{% if request.path == add_hydrograph_url %}active{% endif %}"><a href="{{ add_dam_url }}">Add Hydrograph</a></li>
    {% endblock %}

e. Test upload with these files:

:download:`Sample Hydrograph CSVs <./hydrographs.zip>`

7. Plot Flood Hydrograph Page
=============================

8. Dynamic Hydrograph Plot in Pop-Ups
=====================================

9. REST API
===========

Create a rest API for adding new dams to dam inventory

10. Solution
============

This concludes the Advanced Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-dam_inventory>`_ or clone it as follows:

::

    $ git clone https://github.com/tethysplatform/tethysapp-dam_inventory.git
    $ cd tethysapp-dam_inventory
    $ git checkout advanced-solution
