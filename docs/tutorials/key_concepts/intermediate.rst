.. _key_concepts_intermediate_tutorial:

*********************
Intermediate Concepts
*********************

**Last Updated:** July 2024

This tutorial introduces intermediate concepts for Tethys developers. The topics covered include:

* HTML Forms and User Input
* Introduction to the Model
* File IO and Workspaces
* Rendering Spatial Data on the Map Layout

.. figure:: ../../images/tutorial/advanced/key-concepts-intermediate-screenshot.png
    :width: 800px
    :align: center

0. Start From Beginner Solution (Optional)
==========================================

If you wish to use the beginner solution of the last tutorial as a starting point:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-dam_inventory
    cd tethysapp-dam_inventory
    git checkout -b beginner-solution beginner-|version|

1. Forms and User Input
=======================

HTML forms are the primary mechanism for obtaining input from users of your app. In the next few sections, you'll learn how to create forms in the template and process the data submitted through the form in the controller. For this example, we'll create a form for adding new dams to the inventory.

    a. Add a form to the Add Dam page by modifying the ``/templates/dam_inventory/add_dam.html`` template as follows:

    .. code-block:: html+django
        :emphasize-lines: 6-12

        {% extends tethys_app.package|add:"/base.html" %}
        {% load tethys %}

        {% block app_content %}
        <h1>Add Dam</h1>
        <form id="add-dam-form" method="post">
            {% csrf_token %}
            {% gizmo name_input %}
            {% gizmo owner_input %}
            {% gizmo river_input %}
            {% gizmo date_built_input %}
        </form>
        {% endblock %}

        {% block app_actions %}
        {% gizmo cancel_button %}
        {% gizmo add_button %}
        {% endblock %}

    The form is composed of the the HTML ``<form>`` tag and various input gizmos inside it. We'll use the ``add_button`` gizmo to submit the form. Also note the use of the ``csrf_token`` tag in the form. This is a security precaution that is required to be included in all the forms of your app (see the `Cross Site Forgery protection <https://docs.djangoproject.com/en/2.2/ref/csrf/>`_ article in the Django documentation for more details).

    Also note that the ``method`` attribute of the ``<form>`` element is set to ``post``. This means the form will use the POST HTTP method to submit and transmit the data to the server. For an introduction to HTTP methods, see `The Definitive Guide to GET vs POST <https://blog.teamtreehouse.com/the-definitive-guide-to-get-vs-post>`_.

b. Define the options for the form gizmos in the controller and change the ``add_button`` gizmo to be a submit button for the form in the ``add_dam`` controller:

    .. code-block:: python
        :emphasize-lines: 1, 11-38, 45-46, 56-59

        from tethys_sdk.gizmos import TextInput, DatePicker, SelectInput

        ...

        @controller(url='dams/add')
        def add_dam(request):
            """
            Controller for the Add Dam page.
            """
            # Define form gizmos
            name_input = TextInput(
                display_text='Name',
                name='name'
            )

            owner_input = SelectInput(
                display_text='Owner',
                name='owner',
                multiple=False,
                options=[('Reclamation', 'Reclamation'), ('Army Corp', 'Army Corp'), ('Other', 'Other')],
                initial=['Reclamation']
            )

            river_input = TextInput(
                display_text='River',
                name='river',
                placeholder='e.g.: Mississippi River'
            )

            date_built = DatePicker(
                name='date-built',
                display_text='Date Built',
                autoclose=True,
                format='MM d, yyyy',
                start_view='decade',
                today_button=True,
                initial='February 15, 2017'
            )

            add_button = Button(
                display_text='Add',
                name='add-button',
                icon='plus-square',
                style='success',
                attributes={'form': 'add-dam-form'},
                submit=True
            )

            cancel_button = Button(
                display_text='Cancel',
                name='cancel-button',
                href=App.reverse('home')
            )

            context = {
                'name_input': name_input,
                'owner_input': owner_input,
                'river_input': river_input,
                'date_built_input': date_built,
                'add_button': add_button,
                'cancel_button': cancel_button,
            }

            return App.render(request, 'add_dam.html', context)

2. Handle Form Submission
=========================

At this point the form will be functional, but the app is not doing anything with the data when the user submits the form. In this section we'll implement a pattern for handling the form submission and validating the form.

a. Change the ``add_dam`` controller to handle the form data using the form validation pattern:

    .. code-block:: python
        :emphasize-lines: 1-2, 10-52, 58-59, 67-68, 75-76, 86-87

        from django.contrib import messages

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

            # Errors
            name_error = ''
            owner_error = ''
            river_error = ''
            date_error = ''

            # Handle form submission
            if request.POST and 'add-button' in request.POST:
                # Get values
                has_errors = False
                name = request.POST.get('name', None)
                owner = request.POST.get('owner', None)
                river = request.POST.get('river', None)
                date_built = request.POST.get('date-built', None)

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

                if not has_errors:
                    # Do stuff here
                    return App.redirect(App.reverse('home'))

                messages.error(request, "Please fix errors.")

            # Define form gizmos
            name_input = TextInput(
                display_text='Name',
                name='name',
                initial=name,
                error=name_error
            )

            owner_input = SelectInput(
                display_text='Owner',
                name='owner',
                multiple=False,
                options=[('Reclamation', 'Reclamation'), ('Army Corp', 'Army Corp'), ('Other', 'Other')],
                initial=owner,
                error=owner_error
            )

            river_input = TextInput(
                display_text='River',
                name='river',
                placeholder='e.g.: Mississippi River',
                initial=river,
                error=river_error
            )

            date_built = DatePicker(
                name='date-built',
                display_text='Date Built',
                autoclose=True,
                format='MM d, yyyy',
                start_view='decade',
                today_button=True,
                initial=date_built,
                error=date_error
            )

            add_button = Button(
                display_text='Add',
                name='add-button',
                icon='plus-square',
                style='success',
                attributes={'form': 'add-dam-form'},
                submit=True
            )

            cancel_button = Button(
                display_text='Cancel',
                name='cancel-button',
                href=App.reverse('home')
            )

            context = {
                'name_input': name_input,
                'owner_input': owner_input,
                'river_input': river_input,
                'date_built_input': date_built,
                'add_button': add_button,
                'cancel_button': cancel_button,
            }

            return App.render(request, 'add_dam.html', context)

.. tip::

    **Form Validation Pattern**: The example above implements a common pattern for handling and validating form input. Generally, the steps are:

    1. **Define a "value" variable for each input in the form and assign it the initial value for the input**
    2. **Define an "error" variable for each input to handle error messages and initially set them to the empty string**
    3. **Check to see if the form is submitted and if the form has been submitted:**
        a. Extract the value of each input from the GET or POST parameters and overwrite the appropriate value variable from step 1
        b. Validate the value of each input, assigning an error message (if any) to the appropriate error variable from step 2 for each input with errors.
        c. If there are no errors, save or process the data, and then redirect to a different page
        d. If there are errors continue on and re-render the form with error messages
    4. **Define all gizmos and variables used to populate the form:**
        a. Pass the value variable created in step 1 to the ``initial`` argument of the corresponding gizmo
        b. Pass the error variable created in step 2 to the ``error`` argument of the corresponding gizmo
    5. **Render the page, passing all gizmos to the template through the context**

3. Create the Model and File IO
===============================

Now that we are able to get information about new dams to add to the dam inventory from the user, we need to save or persist the data so we can load it in future page loads. It's time to create the Model for the app.

In this tutorial we will start with a simple file database model to illustrate how to work with files in Tethys apps. In the :doc:`./advanced` tutorial we will convert this file database model to an SQL database model. Here is an overview of the file-based model:

* One text file will be created per dam
* The name of the file will be the id of the dam (e.g.: *a1e26591-d6bb-4194-b4a7-1222fe0195fd.json*)
* The files will be stored in the **app workspace** (a directory provided by the app for storing files).
* Each file will contain a single JSON object with the following structure:

    ::

        {
          "id": "a1e26591-d6bb-4194-b4a7-1222fe0195fd",
          "name": "Deer Creek",
          "owner": "Reclamation",
          "river": "Provo River",
          "date_built": "June 16, 2017"
        }



.. tip::

    For more information on file workspaces see the :ref:`tethys_paths_api`.

.. warning::

    File database models can be problematic for web applications, especially in a production environment. We recommend using a SQL or other type of database that can handle concurrent requests and heavy traffic.

a. Create a new file called ``model.py`` in the ``dam_inventory`` directory and add a new function called ``add_new_dam``:

    .. code-block:: python

        import json
        import os
        import uuid
        from pathlib import Path


        def add_new_dam(db_directory: Path | str, name: str, owner: str, river: str, date_built: str):
            """
            Persist new dam.
            """
            # Serialize data to json
            new_dam_id = uuid.uuid4()
            dam_dict = {
                'id': str(new_dam_id),
                'name': name,
                'owner': owner,
                'river': river,
                'date_built': date_built
            }

            dam_json = json.dumps(dam_dict)

            # Write to file in {{db_directory}}/dams/{{uuid}}.json
            # Make dams dir if it doesn't exist
            dams_dir = Path(db_directory) / 'dams'
            if not dams_dir.exists():
                os.makedirs(dams_dir, exist_ok=True)

            # Name of the file is its id
            file_name = str(new_dam_id) + '.json'
            file_path = dams_dir / file_name

            # Write json
            with file_path.open('w') as f:
                f.write(dam_json)

b. Modify ``add_dam`` controller to use the new ``add_new_dam`` model function to persist the dam data:

    .. code-block:: python
        :emphasize-lines: 1, 5-6, 49-55

        from .model import add_new_dam

        ...

        @controller(url='dams/add', app_workspace=True)
        def add_dam(request, app_workspace):
            """
            Controller for the Add Dam page.
            """
            # Default Values
            name = ''
            owner = 'Reclamation'
            river = ''
            date_built = ''

            # Errors
            name_error = ''
            owner_error = ''
            river_error = ''
            date_error = ''

            # Handle form submission
            if request.POST and 'add-button' in request.POST:
                # Get values
                has_errors = False
                name = request.POST.get('name', None)
                owner = request.POST.get('owner', None)
                river = request.POST.get('river', None)
                date_built = request.POST.get('date-built', None)

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

                if not has_errors:
                    add_new_dam(
                        db_directory=app_workspace.path,
                        name=name,
                        owner=owner,
                        river=river,
                        date_built=date_built
                    )
                    return App.redirect(App.reverse('home'))

                messages.error(request, "Please fix errors.")

            # Define form gizmos
            name_input = TextInput(
                display_text='Name',
                name='name',
                initial=name,
                error=name_error
            )

            owner_input = SelectInput(
                display_text='Owner',
                name='owner',
                multiple=False,
                options=[('Reclamation', 'Reclamation'), ('Army Corp', 'Army Corp'), ('Other', 'Other')],
                initial=owner,
                error=owner_error
            )

            river_input = TextInput(
                display_text='River',
                name='river',
                placeholder='e.g.: Mississippi River',
                initial=river,
                error=river_error
            )

            date_built = DatePicker(
                name='date-built',
                display_text='Date Built',
                autoclose=True,
                format='MM d, yyyy',
                start_view='decade',
                today_button=True,
                initial=date_built,
                error=date_error
            )

            add_button = Button(
                display_text='Add',
                name='add-button',
                icon='plus-square',
                style='success',
                attributes={'form': 'add-dam-form'},
                submit=True
            )

            cancel_button = Button(
                display_text='Cancel',
                name='cancel-button',
                href=App.reverse('home')
            )

            context = {
                'name_input': name_input,
                'owner_input': owner_input,
                'river_input': river_input,
                'date_built_input': date_built,
                'add_button': add_button,
                'cancel_button': cancel_button,
            }

            return App.render(request, 'add_dam.html', context)

c. Use the Add Dam page to add several dams for the Dam Inventory app.

d. Navigate to ``workspaces/app_workspace/dams`` to see the JSON files that are being written.

4. Develop Table View Page
==========================

Now that the data is being persisted in our make-shift inventory database, let's create useful views of the data in our inventory. First, we'll create a new page that lists all of the dams in our inventory database in a table, which will provide a good review of Model View Controller:

a. Open ``model.py`` and add a model method for listing the dams called ``get_all_dams``:

    .. code-block:: python

        def get_all_dams(db_directory: Path | str):
            """
            Get all persisted dams.
            """
            # Write to file in {{db_directory}}/dams/{{uuid}}.json
            # Make dams dir if it doesn't exist
            dams_dir = Path(db_directory) / 'dams'
            if not dams_dir.exists():
                os.makedirs(dams_dir, exist_ok=True)

            dams = []

            # Open each json file and convert contents to python dictionaries
            for dam_json in dams_dir.glob('*.json'):
                with dam_json.open('r') as f:
                    dam_dict = json.loads(f.read())
                    dams.append(dam_dict)

            return dams

b. Add a new template ``/templates/dam_inventory/list_dams.html`` with the following contents:

    .. code-block:: html+django

        {% extends tethys_app.package|add:"/base.html" %}
        {% load tethys %}

        {% block app_content %}
        <h1>Dams</h1>
        {% gizmo dams_table %}
        {% endblock %}

c. Create a new controller function in ``controllers.py`` called ``list_dams``:

    .. code-block:: python

        from tethys_sdk.gizmos import DataTableView
        from .model import get_all_dams

        ...

        @controller(name='dams', url='dams', app_workspace=True)
        def list_dams(request, app_workspace):
            """
            Show all dams in a table view.
            """
            dams = get_all_dams(app_workspace.path)
            table_rows = []

            for dam in dams:
                table_rows.append(
                    (
                        dam['name'], dam['owner'],
                        dam['river'], dam['date_built']
                    )
                )

            dams_table = DataTableView(
                column_names=('Name', 'Owner', 'River', 'Date Built'),
                rows=table_rows,
                searching=False,
                orderClasses=False,
                lengthMenu=[ [10, 25, 50, -1], [10, 25, 50, "All"] ],
            )

            context = {
                'dams_table': dams_table
            }

            return App.render(request, 'list_dams.html', context)
        
    .. note::

        The ``name`` argument can be used to set a custom name for the route that maps a URL to a controller as shown above. The default name is the same name as the controller function. This name is used to look up the URL of the controller using either the ``url`` tag in templates (see next step) or the ``reverse`` function in Python code.

d. Open ``/templates/dam_inventory/base.html`` and add a header button and a navigation link for the Dams table view page:

    .. code-block:: html+django
        :emphasize-lines: 4, 8-10

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
          <div class="header-button glyphicon-button">
            <a href="{{ add_dam_url }}" title="Add Dam"><i class="bi bi-plus-circle"></i></a>
          </div>
        {% endblock %}

    .. code-block:: html+django
        :emphasize-lines: 4, 7

        {% block app_navigation_items %}
          {% url tethys_app|url:'home' as home_url %}
          {% url tethys_app|url:'add_dam' as add_dam_url %}
          {% url tethys_app|url:'dams' as list_dam_url %}
          <li class="nav-item title">Navigation</li>
          <li class="nav-item"><a class="nav-link{% if request.path == home_url %} active{% endif %}" href="{{ home_url }}">Map</a></li>
          <li class="nav-item"><a class="nav-link{% if request.path == list_dam_url %} active{% endif %}" href="{{ list_dam_url }}">Dams</a></li>
          <li class="nav-item"><a class="nav-link{% if request.path == add_dam_url %} active{% endif %}" href="{{ add_dam_url }}">Add Dam</a></li>
        {% endblock %}


5. Spatial Input with Forms
===========================

In this section, we'll add a Map View gizmo to the Add Dam form to allow users to provide the location of the dam as another attribute.

a. Open ``/templates/dam_inventory/add_dam.html`` and add the ``location_input`` gizmo to the form:

    .. code-block:: html+django
        :emphasize-lines: 8-12

        {% extends tethys_app.package|add:"/base.html" %}
        {% load tethys %}

        {% block app_content %}
        <h1>Add Dam</h1>
        <form id="add-dam-form" method="post">
            {% csrf_token %}
            <div class="form-group{% if location_error %} has-error{% endif %}">
                <label class="control-label">Location</label>
                {% gizmo location_input %}
                {% if location_error %}<p class="help-block">{{ location_error }}</p>{% endif %}
            </div>
            {% gizmo name_input %}
            {% gizmo owner_input %}
            {% gizmo river_input %}
            {% gizmo date_built_input %}
        </form>
        {% endblock %}

        {% block app_actions %}
        {% gizmo add_button %}
        {% gizmo cancel_button %}
        {% endblock %}

b. Add the definition of the ``location_input`` gizmo and validation code to the ``add_dam`` controller in ``controllers.py``:

    .. code-block:: python
        :emphasize-lines: 1, 15, 22, 32, 51-53, 58, 104-123, 145-146

        from tethys_sdk.gizmos import MapView, MVDraw, MVView

        ...

        @controller(url='dams/add', app_workspace=True)
        def add_dam(request, app_workspace):
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
                        db_directory=app_workspace.path,
                        location=location,
                        name=name,
                        owner=owner,
                        river=river,
                        date_built=date_built
                    )
                    return App.redirect(App.reverse('home'))

                messages.error(request, "Please fix errors.")

            # Define form gizmos
            name_input = TextInput(
                display_text='Name',
                name='name',
                initial=name,
                error=name_error
            )

            owner_input = SelectInput(
                display_text='Owner',
                name='owner',
                multiple=False,
                options=[('Reclamation', 'Reclamation'), ('Army Corp', 'Army Corp'), ('Other', 'Other')],
                initial=owner,
                error=owner_error
            )

            river_input = TextInput(
                display_text='River',
                name='river',
                placeholder='e.g.: Mississippi River',
                initial=river,
                error=river_error
            )

            date_built = DatePicker(
                name='date-built',
                display_text='Date Built',
                autoclose=True,
                format='MM d, yyyy',
                start_view='decade',
                today_button=True,
                initial=date_built,
                error=date_error
            )

            initial_view = MVView(
                projection='EPSG:4326',
                center=[-98.6, 39.8],
                zoom=3.5
            )

            drawing_options = MVDraw(
                controls=['Modify', 'Delete', 'Move', 'Point'],
                initial='Point',
                output_format='GeoJSON',
                point_color='#FF0000'
            )

            location_input = MapView(
                height='300px',
                width='100%',
                basemap=['OpenStreetMap'],
                draw=drawing_options,
                view=initial_view
            )

            add_button = Button(
                display_text='Add',
                name='add-button',
                icon='plus-square',
                style='success',
                attributes={'form': 'add-dam-form'},
                submit=True
            )

            cancel_button = Button(
                display_text='Cancel',
                name='cancel-button',
                href=App.reverse('home')
            )

            context = {
                'name_input': name_input,
                'owner_input': owner_input,
                'river_input': river_input,
                'date_built_input': date_built,
                'location_input': location_input,
                'location_error': location_error,
                'add_button': add_button,
                'cancel_button': cancel_button,
            }

            return App.render(request, 'add_dam.html', context)

c. Modify the ``add_new_dam`` Model Method to store spatial data:

    .. code-block:: python
        :emphasize-lines: 1, 5-6, 12

        def add_new_dam(db_directory, location, name, owner, river, date_built):
            """
            Persist new dam.
            """
            # Convert GeoJSON to Python dictionary
            location_dict = json.loads(location)

            # Serialize data to json
            new_dam_id = uuid.uuid4()
            dam_dict = {
                'id': str(new_dam_id),
                'location': location_dict['geometries'][0],
                'name': name,
                'owner': owner,
                'river': river,
                'date_built': date_built
            }

            dam_json = json.dumps(dam_dict)

            # Write to file in {{db_directory}}/dams/{{uuid}}.json
            # Make dams dir if it doesn't exist
            dams_dir = os.path.join(db_directory, 'dams')
            if not os.path.exists(dams_dir):
                os.mkdir(dams_dir)

            # Name of the file is its id
            file_name = str(new_dam_id) + '.json'
            file_path = os.path.join(dams_dir, file_name)

            # Write json
            with open(file_path, 'w') as f:
                f.write(dam_json)

d. Navigate to ``workspaces/app_workspace/dams`` and delete all JSON files now that the model has changed, so that all the files will be consistent.

e. Create several new entries using the updated Add Dam form.

6. Render Spatial Data on Map
=============================

Finally, we'll add logic to the home ``HomeMap`` controller to display all of the dams in our dam inventory on the map.

a. Modify the ``HomeMap`` controller in ``controllers.py`` to map the list of dams:

    .. code-block:: python
        :emphasize-lines: 1, 8, 10-134

        @controller(name="home", app_workspace=True)
        class HomeMap(MapLayout):
            app = App
            base_template = f'{App.package}/base.html'
            map_title = 'Dam Inventory'
            map_subtitle = 'Tutorial'
            basemaps = ['OpenStreetMap', 'ESRI']
            show_properties_popup = True

            def compose_layers(self, request, map_view, app_workspace, *args, **kwargs):
                # Get list of dams and create dams MVLayer:
                dams = get_all_dams(app_workspace.path)
                features = []

                # Define GeoJSON Features
                for dam in dams:
                    dam_location = dam.get('location')
                    dam_feature = {
                        'type': 'Feature',
                        'geometry': {
                            'type': dam_location['type'],
                            'coordinates': dam_location['coordinates'],
                        },
                        'properties': {
                            'id': dam['id'],
                            'name': dam['name'],
                            'owner': dam['owner'],
                            'river': dam['river'],
                            'date_built': dam['date_built']
                        }
                    }

                    features.append(dam_feature)

                # Define GeoJSON FeatureCollection
                dams_feature_collection = {
                    'type': 'FeatureCollection',
                    'crs': {
                        'type': 'name',
                        'properties': {
                            'name': 'EPSG:4326'
                        }
                    },
                    'features': features
                }

                # Compute zoom extent for the dams layer
                layer_extent = self.compute_dams_extent(dams)

                dam_layer = self.build_geojson_layer(
                    geojson=dams_feature_collection,
                    layer_name='dams',
                    layer_title='Dams',
                    layer_variable='dams',
                    extent=layer_extent,
                    visible=True,
                    selectable=True,
                    plottable=True,
                )

                layer_groups = [
                    self.build_layer_group(
                        id='all-layers',
                        display_name='Layers',
                        layer_control='checkbox',
                        layers=[dam_layer]
                    )
                ]

                # Update the map view with the new extent
                map_view.view = MVView(
                    projection='EPSG:4326',
                    extent=layer_extent,
                    maxZoom=self.max_zoom,
                    minZoom=self.min_zoom,
                )

                return layer_groups

            def build_map_extent_and_view(self, request, app_workspace, *args, **kwargs):
                """
                Builds the default MVView and BBOX extent for the map.

                Returns:
                    MVView, 4-list<float>: default view and extent of the project.
                """
                dams = get_all_dams(app_workspace.path)
                extent = self.compute_dams_extent(dams)

                # Construct the default view
                view = MVView(
                    projection="EPSG:4326",
                    extent=extent,
                    maxZoom=self.max_zoom,
                    minZoom=self.min_zoom,
                )

                return view, extent

            def compute_dams_extent(self, dams):
                """Compute the extent/bbox of the given dams."""
                lat_list = []
                lng_list = []

                # Define GeoJSON Features
                for dam in dams:
                    dam_location = dam.get('location')
                    lat_list.append(dam_location['coordinates'][1])
                    lng_list.append(dam_location['coordinates'][0])

                if len(lat_list) > 1:
                    # Compute the bounding box of all the dams
                    min_x = min(lng_list)
                    min_y = min(lat_list)
                    max_x = max(lng_list)
                    max_y = max(lat_list)
                    x_dist = max_x - min_x
                    y_dist = max_y - min_y

                    # Buffer the bounding box
                    buffer_factor = 0.1
                    x_buffer = x_dist * buffer_factor
                    y_buffer = y_dist * buffer_factor
                    min_xb = min_x - x_buffer
                    min_yb = min_y - y_buffer
                    max_xb = max_x + x_buffer
                    max_yb = max_y + y_buffer

                    # Bounding box for the view
                    extent = [min_xb, min_yb, max_xb, max_yb]
                else:
                    extent = [-125.771484, 24.527135, -66.005859, 49.667628]  # CONUS

                return extent

    .. tip::

        Here are some key points to note about the changes made to the ``HomeMap`` controller:

        * The ``compose_layers`` method has been added to define layers that should be displayed on the map. The method builds a GeoJSON FeatureCollection from the list of dams and then creates a GeoJSON layer from the FeatureCollection.
        * The ``build_map_extent_and_view`` method has been added to define the default view and zoom extent of the map. The method computes the bounding box of the dams and returns a view and extent for the map.
        * The ``compute_dams_extent`` method has been added to compute the bounding box of the dams. The method calculates the bounding box of the dams and then buffers the bounding box to ensure that all the dams are visible on the map. It is used by both the ``compose_layers`` and ``build_map_extent_and_view`` methods.
        * The ``show_properties_popup`` attribute has been set to ``True`` to enable the display of a popup with the properties of the dams when they are clicked on the map.
  
b. Save your changes to ``controllers.py`` and navigate to the home page to see the dams displayed on the map.

7. Solution
===========

This concludes the Intermediate Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-dam_inventory>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-dam_inventory
    cd tethysapp-dam_inventory
    git checkout -b intermediate-solution intermediate-|version|
