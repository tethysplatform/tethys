********************
App Basics: Advanced
********************

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

Configure App to Use a Persistent Store Database
================================================

Intro to persistent stores...

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
                  'properties': {
                      'name': dam.name,
                      'owner': dam.owner,
                      'river': dam.river,
                      'date_built': dam.date_built
                   }
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

6. Execute **syncstores** command to initialize database:

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

2. Create a new file called ``map.js`` in the ``public/js/`` directory and add these contents:

::

    $(function() {
        // Get the Select Interaction
        var select_interaction = TETHYS_MAP_VIEW.getSelectInteraction();

        //when selected, call function to make hydrograph
        select_interaction.getFeatures().on('change:length', function(e) {
          if (e.target.getArray().length > 0) {
            // this means there is at least 1 feature selected
            var selected_feature = e.target.item(0); // 1st feature in Collection

          }
        });
    });

3. Open ``templates/dam_inventory/home.html``, load the ``staticfiles`` module and add the ``map.js`` script to the page:

::

    {% extends "dam_inventory/base.html" %}
    {% load tethys_gizmos staticfiles %}

    {% block app_content %}
      {% gizmo dam_inventory_map %}
    {% endblock %}

    {% block app_actions %}
      {% gizmo add_dam_button %}
    {% endblock %}

    {% block scripts %}
      {{ block.super }}
      <script src="{% static 'dam_inventory/js/map.js' %}" type="text/javascript"></script>
    {% endblock %}


Use CSS and JavaScript to Make Map Fit Fill Screen
==================================================

Add Flood Hydrograph Model
==========================


Add Flood Hydrograph Form
=========================

Add Flood Hydrograph Plot
=========================


Create Permissions Groups
=========================


Narrative
* Introduce Tethys Services API
* Refactor to use PersistentStores API, rather than JSON files
* Add hydrograph table
* Create form for uploading hydrograph files and show how to use that on server and load into database
* Plot hydrographs
* Use JavaScript APIs to create dynamic pop-ups that show attributes of dam when clicked on
* Use CSS to make map fit full screen
* Create two permissions groups: viewers and admins -- only allow admins to add new dams
