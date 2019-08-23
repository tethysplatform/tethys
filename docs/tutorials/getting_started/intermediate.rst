*********************
Intermediate Concepts
*********************

**Last Updated:** June 2017

This tutorial introduces intermediate concepts for Tethys developers. The topics covered include:

* HTML Forms and User Input
* Handling Form Submissions in Controllers
* Form Validation Pattern
* Introduction to the Model
* File IO and Workspaces
* Intermediate Template Gizmos
* Review of Model View Controller
* Spatial Inputs in Forms
* Rendering Spatial Data on the Map View Gizmo

0. Start From Beginner Solution (Optional)
==========================================

If you wish to use the beginner solution of the last tutorial as a starting point:

::

    $ git clone https://github.com/tethysplatform/tethysapp-dam_inventory.git
    $ cd tethysapp-dam_inventory
    $ git checkout beginner-solution

1. Forms and User Input
=======================

HTML forms are the primary mechanism for obtaining input from users of your app. In the next few sections, you'll learn how to create forms in the template and process the data submitted through the form in the controller. For this example, we'll create a form for adding new dams to the inventory.

a. Add a form to the Add Dam page by modifying the ``/templates/dam_inventory/add_dam.html`` template as follows:

::

    {% extends "dam_inventory/base.html" %}
    {% load tethys_gizmos %}

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

Also note that the ``method`` attribute of the ``<form>`` element is set to ``post``. This means the form will use the POST HTTP method to submit and transmit the data to the server. For an introduction to HTTP methods, see `The Definitive Guide to GET vs POST <http://blog.teamtreehouse.com/the-definitive-guide-to-get-vs-post>`_.

b. Define the options for the form gizmos in the controller and change the ``add_button`` gizmo to be a submit button for the form in the ``add_dam`` controller:

::

    from tethys_sdk.gizmos import TextInput, DatePicker, SelectInput

    ...

    @login_required()
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
            icon='glyphicon glyphicon-plus',
            style='success',
            attributes={'form': 'add-dam-form'},
            submit=True
        )

        cancel_button = Button(
            display_text='Cancel',
            name='cancel-button',
            href=reverse('dam_inventory:home')
        )

        context = {
            'name_input': name_input,
            'owner_input': owner_input,
            'river_input': river_input,
            'date_built_input': date_built,
            'add_button': add_button,
            'cancel_button': cancel_button,
        }

        return render(request, 'dam_inventory/add_dam.html', context)

2. Handle Form Submission
=========================

At this point the form will be functional, but the app is not doing anything with the data when the user submits the form. In this section we'll implement a pattern for handling the form submission and validating the form.

a. Change the ``add_dam`` controller to handle the form data using the form validation pattern:

::

    from django.shortcuts import redirect
    from django.contrib import messages

    ...

    @login_required()
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
                return redirect(reverse('dam_inventory:home'))

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
        ...

.. tip::

    **Form Validation Pattern**: The example above implements a common pattern for handling and validating form input. Generally, the steps are:

    1. **define a "value" variable for each input in the form and assign it the initial value for the input**
    2. **define an "error" variable for each input to handle error messages and initially set them to the empty string**
    3. **check to see if the form is submitted and if the form has been submitted:**
        a. extract the value of each input from the GET or POST parameters and overwrite the appropriate value variable from step 1
        b. validate the value of each input, assigning an error message (if any) to the appropriate error variable from step 2 for each input with errors.
        c. if there are no errors, save or process the data, and then redirect to a different page
        d. if there are errors continue on and re-render from with error messages
    4. **define all gizmos and variables used to populate the form:**
        a. pass the value variable created in step 1 to the ``initial`` argument of the corresponding gizmo
        b. pass the error variable created in step 2 to the ``error`` argument of the corresponding gizmo
    5. **render the page, passing all gizmos to the template through the context**

3. Create the Model and File IO
===============================

Now that we are able to get information about new dams to add to the dam inventory from the user, we need to persist the data to some sort of database. It's time to create the Model for the app.

In this tutorial we will start with a file database model to illustrate how to work with files in Tethys apps. In the :doc:`./advanced` tutorial we will convert this file database model to an SQL database model. Here is an overview of the file-based model:

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

    For more information on file workspaces see the :doc:`../../tethys_sdk/workspaces`.

.. warning::

    File database models can be problematic for web applications, especially in a production environment. We recommend using and SQL or other database that can handle concurrent requests and heavy traffic.

a. Open ``model.py`` and add a new function called ``add_new_dam``:

::

    import os
    import uuid
    import json
    from .app import DamInventory as app


    def add_new_dam(name, owner, river, date_built):
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

        # Write to file in app_workspace/dams/{{uuid}}.json
        # Make dams dir if it doesn't exist
        app_workspace = app.get_app_workspace()
        dams_dir = os.path.join(app_workspace.path, 'dams')
        if not os.path.exists(dams_dir):
            os.mkdir(dams_dir)

        # Name of the file is its id
        file_name = str(new_dam_id) + '.json'
        file_path = os.path.join(dams_dir, file_name)

        # Write json
        with open(file_path, 'w') as f:
            f.write(dam_json)



b. Modify ``add_dam`` controller to use the new ``add_new_dam`` model function to persist the dam data:

::

    from .model import add_new_dam

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
                add_new_dam(name=name, owner=owner, river=river, date_built=date_built)
                return redirect(reverse('dam_inventory:home'))

            ...

c. Use the Add Dam page to add several dams for the Dam Inventory app.

d. Navigate to ``workspaces/app_workspace/dams`` to see the JSON files that are being written.

4. Develop Table View Page
==========================

Now that the data is being persisted in our make-shift inventory database, let's create useful views of the data in our inventory. First, we'll create a new page that lists all of the dams in our inventory database in a table, which will provide a good review of Model View Controller:

a. Open ``models.py`` and add a model method for listing the dams called ``get_all_dams``:

::

    def get_all_dams():
        """
        Get all persisted dams.
        """
        # Write to file in app_workspace/dams/{{uuid}}.json
        # Make dams dir if it doesn't exist
        app_workspace = app.get_app_workspace()
        dams_dir = os.path.join(app_workspace.path, 'dams')
        if not os.path.exists(dams_dir):
            os.mkdir(dams_dir)

        dams = []

        # Open each file and convert contents to python objects
        for dam_json in os.listdir(dams_dir):
            # Make sure we are only looking at json files
            if '.json' not in dam_json:
                continue

            dam_json_path = os.path.join(dams_dir, dam_json)
            with open(dam_json_path, 'r') as f:
                dam_dict = json.loads(f.readlines()[0])
                dams.append(dam_dict)

        return dams

b. Add a new template ``/templates/dam_inventory/list_dams.html`` with the following contents:

::

    {% extends "dam_inventory/base.html" %}
    {% load tethys_gizmos %}

    {% block app_content %}
      <h1>Dams</h1>
      {% gizmo dams_table %}
    {% endblock %}

c. Create a new controller function in ``controllers.py`` called ``list_dams``:

::

    from tethys_sdk.gizmos import DataTableView
    from .model import get_all_dams

    ...

    @login_required()
    def list_dams(request):
        """
        Show all dams in a table view.
        """
        dams = get_all_dams()
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

        return render(request, 'dam_inventory/list_dams.html', context)

d. Create a new URL Map in the ``app.py`` for the new ``list_dams`` controller:

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
                ...

                UrlMap(
                    name='dams',
                    url='dam-inventory/dams',
                    controller='dam_inventory.controllers.list_dams'
                ),
            )

            return url_maps

e. Open ``/templates/dam_inventory/base.html`` and add navigation links for the List View page:

::

    {% block app_navigation_items %}
      {% url 'dam_inventory:home' as home_url %}
      {% url 'dam_inventory:add_dam' as add_dam_url %}
      {% url 'dam_inventory:dams' as list_dam_url %}
      <li class="title">Navigation</li>
      <li class="{% if request.path == home_url %}active{% endif %}"><a href="{{ home_url }}">Home</a></li>
      <li class="{% if request.path == list_dam_url %}active{% endif %}"><a href="{{ list_dam_url }}">Dams</a></li>
      <li class="{% if request.path == add_dam_url %}active{% endif %}"><a href="{{ add_dam_url }}">Add Dam</a></li>
    {% endblock %}


5. Spatial Input with Forms
===========================

In this section, we'll add a Map View gizmo to the Add Dam form to allow users to provide the location of the dam as another attribute.

a. Open ``/templates/dam_inventory/add_dam.html`` and add the ``location_input`` gizmo to the form:

::

    {% extends "dam_inventory/base.html" %}
    {% load tethys_gizmos %}

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

::

    from tethys_sdk.gizmos import MVDraw, MVView

    ...

    @login_required()
    def add_dam(request):
        """
        Controller for the Add Dam page.
        """
        # Default Values
        location = ''
        ...

        # Errors
        location_error = ''
        ...

        # Handle form submission
        if request.POST and 'add-button' in request.POST:
            # Get values
            has_errors = False
            location = request.POST.get('geometry', None)
            ...

            # Validate
            if not location:
                has_errors = True
                location_error = 'Location is required.'

            ...

            if not has_errors:
                add_new_dam(location=location, name=name, owner=owner, river=river, date_built=date_built)
                return redirect(reverse('dam_inventory:home'))

            messages.error(request, "Please fix errors.")

        # Define form gizmos
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
            basemap='OpenStreetMap',
            draw=drawing_options,
            view=initial_view
        )

        ...

        context = {
            'location_input': location_input,
            'location_error': location_error,
            ...
        }

        return render(request, 'dam_inventory/add_dam.html', context)

c. Modify the ``add_new_dam`` Model Method to store spatial data:

::

    def add_new_dam(location, name, owner, river, date_built):
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

        # Write to file in app_workspace/dams/{{uuid}}.json
        # Make dams dir if it doesn't exist
        app_workspace = app.get_app_workspace()
        dams_dir = os.path.join(app_workspace.path, 'dams')
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

Finally, we'll add logic to the home controller to display all of the dams in our dam inventory on the map.

a. Modify the ``home`` controller in ``controllers.py`` to map the list of dams:

::

    from tethys_sdk.gizmos import MVLayer

    ...

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

        # Define GeoJSON Features
        for dam in dams:
            dam_location = dam.pop('location')
            lat_list.append(dam_location['coordinates'][1])
            lng_list.append(dam_location['coordinates'][0])

            dam_feature = {
                'type': 'Feature',
                'geometry': {
                    'type': dam_location['type'],
                    'coordinates': dam_location['coordinates'],
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

        style = {'ol.style.Style': {
            'image': {'ol.style.Circle': {
                'radius': 10,
                'fill': {'ol.style.Fill': {
                    'color':  '#d84e1f'
                }},
                'stroke': {'ol.style.Stroke': {
                    'color': '#ffffff',
                    'width': 1
                }}
            }}
        }}

        # Create a Map View Layer
        dams_layer = MVLayer(
            source='GeoJSON',
            options=dams_feature_collection,
            legend_title='Dams',
            layer_options={'style': style}
            }
        )

        # Define view centered on dam locations
        try:
            view_center = [sum(lng_list) / float(len(lng_list)), sum(lat_list) / float(len(lat_list))]
        except ZeroDivisionError:
            view_center = [-98.6, 39.8]

        view_options = MVView(
            projection='EPSG:4326',
            center=view_center,
            zoom=4.5,
            maxZoom=18,
            minZoom=2
        )

        dam_inventory_map = MapView(
            height='100%',
            width='100%',
            layers=[dams_layer],
            basemap='OpenStreetMap',
            view=view_options
        )

        add_dam_button = Button(
            display_text='Add Dam',
            name='add-dam-button',
            icon='glyphicon glyphicon-plus',
            style='success',
            href=reverse('dam_inventory:add_dam')
        )

        context = {
            'dam_inventory_map': dam_inventory_map,
            'add_dam_button': add_dam_button
        }

        return render(request, 'dam_inventory/home.html', context)

7. Solution
===========

This concludes the Intermediate Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-dam_inventory>`_ or clone it as follows:

::

    $ mkdir ~/tethysdev
    $ cd ~/tethysdev
    $ git clone https://github.com/tethysplatform/tethysapp-dam_inventory.git
    $ cd tethysapp-dam_inventory
    $ git checkout intermediate-solution