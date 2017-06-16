*****************
Advanced Concepts
*****************

**Last Updated:** May 2017

.. warning::

   UNDER CONSTRUCTION

Concepts
========
* Tethys Services API
* Model and PersistentStores API
* JavaScript with Gizmos - dynamic pop-ups and selection
* JavaScript AJAX
* Permissions API
* Custom Styling - make map fit full screen
* Advanced HTML forms - File Upload

Start From Intermediate Solution
================================

If you wish to use the solution as a starting point:

::

    $ mkdir ~/tethysdev
    $ cd ~/tethysdev
    $ git clone https://github.com/tethysplatform/tethysapp-dam_inventory.git
    $ cd tethysapp-dam_inventory
    $ git checkout intermediate-solution
    $ t
    (tethys)$ python setup.py develop

Start the Development Server
============================

If you have not already started the development server, start it now:

::

    (tethys) $ tethys manage start

    OR

    (tethys) $ tms

Configure App to Use a Custom Setting
=====================================

Intro to App Settings... :doc:`../../tethys_sdk/app_settings`





Configure App to Use a Persistent Store Database
================================================

Intro to persistent stores... :doc:`../../tethys_sdk/tethys_services/persistent_store`

1. Open the ``app.py`` and define a new ``PersistentStoreDatabaseSetting`` by adding the ``persistent_store_settings`` method to your app class:

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


2. Refactor the dams model to use the Persistent Store Database instead of the JSON files (``models.py``):

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


    def init_primary_db(engine, first_time):
        """
        Initializer for the primary database.
        """
        Base.metadata.create_all(engine)

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



3. Refactor ``home`` controller in ``controllers.py`` to use new model objects:

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

4. Add **Persistent Store Service** to Tethys Portal:

    a. Go to Tethys Portal Home in a web browser (e.g. http://localhost:8000/apps/)
    b. Select **Site Admin** from the drop down next to your username.
    c. Scroll down to **Tethys Services** section and select **Persistent Store Services** link.
    d. Click on the **Add Persistent Store Service** button.
    e. Give the **Persistent Store Service** a name and fill out the connection information.

**IMPORTANT**: The username and password for the persistent store service must be a superuser to use spatial persistent stores.

5. Assign **Persistent Store Service** to Dam Inventory App:

    a. Go to Tethys Portal Home in a web browser (e.g. http://localhost:8000/apps/)
    b. Select **Site Admin** from the drop down next to your username.
    c. Scroll down to **Tethys Apps** section and select **Installed App** link.
    d. Select the **Dam Inventory** link.
    e. Scroll down to the **Persistent Store Database Settings** section.
    f. Assign the **Persistent Store Service** that you created in Step 4 to the **primary_db**.

6. Execute **syncstores** command to initialize Persistent Store database:

::

    (tethys) $ tethys syncstores dam_inventory


Use JavaScript APIs to Create Dynamic Pop-Ups
=============================================

1. Modify MVLayer in ``home`` controller to make the layer selectable:

::

    ...

    dams_layer = MVLayer(
        source='GeoJSON',
        options=dams_feature_collection,
        legend_title='Dams',
        feature_selection=True
    )

    ...

2. Create a new file called ``map.js`` in the ``public/js/`` directory and add the following contents:

::

    $(function()
    {
        // Get the Select Interaction
        var select_interaction = TETHYS_MAP_VIEW.getSelectInteraction();

        // When selected, call function to display properties
        select_interaction.getFeatures().on('change:length', function(e)
        {

            if (e.target.getArray().length > 0)
            {
                // this means there is at least 1 feature selected
                var selected_feature = e.target.item(0); // 1st feature in Collection in the case of multi-select

                console.log(selected_feature.get('name'));
                console.log(selected_feature.get('owner'));
                console.log(selected_feature.get('river'));
                console.log(selected_feature.get('date_built'));

            }
        });
    });

3. Open ``templates/dam_inventory/home.html``, load the ``staticfiles`` module and add the ``map.js`` script to the page:

::

    {% extends "dam_inventory/base.html" %}
    {% load tethys_gizmos staticfiles %}

    ...

    {% block scripts %}
      {{ block.super }}
      <script src="{% static 'dam_inventory/js/map.js' %}" type="text/javascript"></script>
    {% endblock %}

4. Add a new element to the ``app_content`` area of the page with an id of ``popup``:

::

    {% block app_content %}
      {% gizmo dam_inventory_map %}
      <div id="popup"></div>
    {% endblock %}

5. Modify the ``public/js/map.js`` script to add the pop-up to the map when a point is selected and display the properties of that point:

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


6. Add Custom CSS to style the pop-up. Create a new file ``public/css/map.css`` and add the following contentss:

::

    .popover-content {
        width: 240px;
    }

    #inner-app-content {
        padding: 0;
    }

    #app-content, #inner-app-content, #map_view_outer_container {
        height: 100%;
    }

7. Add ``public/css/map.css`` to the ``templates/dam_inventory/home.html`` file:

::


    {% block styles %}
        {{ block.super }}
        <link href="{% static 'dam_inventory/css/map.css' %}" rel="stylesheet"/>
    {% endblock %}


Create Permissions Groups
=========================

Intro to permissions... :doc:`../../tethys_sdk/permissions`

1. Define permissions for the app by adding the ``permissions`` method to the app class in the ``app.py``:

::

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

2. Protect the Add Dam view with the ``add_dams`` permission by adding the ``permission_required`` decorator to the ``add_dams`` controller:

::

    from tethys_sdk.permissions import permission_required

    ...

    @permission_required('add_dams')
    def add_dam(request):
        """
        Controller for the Add Dam page.
        """
        ...

3. Add a context variable called ``can_add_dams`` to the context of each controller with the value of the return value of the ``has_permission`` function:

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

4. Use the ``can_add_dams`` method to show or hide the navigation link to the Add Dam View. Modify ``templates/dam_inventory/base.html``:

::

    {% block app_navigation_items %}
      ...
      <li class="{% if request.path == home_url %}active{% endif %}"><a href="{{ home_url }}">Home</a></li>
      <li class="{% if request.path == list_dam_url %}active{% endif %}"><a href="{{ list_dam_url }}">Dams</a></li>
      {% if can_add_dams %}
      <li class="{% if request.path == add_dam_url %}active{% endif %}"><a href="{{ add_dam_url }}">Add Dam</a></li>
      {% endif %}
    {% endblock %}

5. Use the ``can_add_dams`` method to show or hide the "Add Dam" button on the home page:

::

    {% block app_actions %}
      {% if can_add_dams %}
        {% gizmo add_dam_button %}
      {% endif %}
    {% endblock %}

5. Superusers have all permissions. To test the permissions, create two new users: one with the ``admin`` permissions group and one without it. Then login with these users:

    a. Go to Tethys Portal Home in a web browser (e.g. http://localhost:8000/apps/)
    b. Select **Site Admin** from the drop down next to your username.
    c. Scroll to the **Authentication and Authorization** section.
    d. Select the **Users** link.
    e. Press the **Add User** button.
    f. Enter "di_admin" as the username and enter a password. Take note of the password for later.
    g. Press the **Save** button.
    h. Scroll down to the **Groups** section.
    i. Select the **dam_inventory:admin** group and press the right arrow to add the user to that group.
    j. Press the **Save** button.
    k. Repeat steps e-f for user named "di_viewer". DO NOT add "di_viewer" user to any groups.
    l. Press the **Save** button.

6. Log in each user. If the permission has been applied correctly, "di_viewer" should not be able to see the Add Dam link and should be redirected if the Add Dam view is linked to directly. "di_admin" should be able to add dams.


Add Flood Hydrograph Model
==========================

Add Flood Hydrograph Form
=========================

Add Flood Hydrograph Plot
=========================
