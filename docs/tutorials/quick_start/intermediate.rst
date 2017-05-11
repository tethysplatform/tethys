*****************************
App Development: Intermediate
*****************************

**Last Updated:** May 2017

.. warning::

   UNDER CONSTRUCTION

Concepts
========

* Advanced Gizmos API (Plotting and Mapping) - Hard code data / empty
* Custom App Settings API (control default color of points on map?)
* HTML Forms and Getting Input from users - use map in form for input
* Navigation Links
* Workspaces API (Write data submitted to file temporarily?)

Start From Beginner Solution
============================

If you wish to use the solution as a starting point:

::

    $ mkdir ~/tethysdev
    $ cd ~/tethysdev
    $ git clone https://github.com/tethysplatform/tethysapp-dam_inventory.git
    $ cd tethysapp-dam_inventory
    $ git checkout beginner-solution
    $ t
    (tethys)$ python setup.py develop

Start the Development Server
============================

If you have not already started the development server, start it now:

::

    (tethys) $ tethys manage start

    OR

    (tethys) $ tms

Add Dam Form
============

Intro to user input and HTML forms...

1. Add a form to the Add Dam page by modifying the ``templates/dam_inventory/add_dam.html`` template as follows:

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
      {% gizmo add_button %}
      {% gizmo cancel_button %}
    {% endblock %}

2. Define the form gizmos and change the Add button to a submit button for the Add Dam form in the ``add_dam`` controller:

::

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
            initial=['reclamation']
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

Handle Form Submission
======================

Intro to form validation method...
Intro to django.contrib.messages...
Intro to initial and error attributes in gizmos

Change to the ``add_dam`` controller to handle the form data (write to file for now):

::

    from django.shortcuts import render, redirect
    from django.contrib import messages

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

            if not river:
                has_errors = True
                river_error = 'Required.'

            if not date_built:
                has_errors = True
                date_error = 'Required.'

            if not has_errors:
                # Do stuff here
                return redirect(reverse('dam_inventory:home'))

            messages.error(request, "Please fix errors.")

        # Define form gizmos'
        ...

Write Data To File
==================

Intro to model concept...
Intro to workspaces API... :doc:`../../tethys_sdk/workspaces`

1. Open ``model.py`` and add this function:

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
        user_workspace = app.get_app_workspace()
        dams_dir = os.path.join(user_workspace.path, 'dams')
        if not os.path.exists(dams_dir):
            os.mkdir(dams_dir)

        # Name of the file is its id
        file_name = str(new_dam_id) + '.json'
        file_path = os.path.join(dams_dir, file_name)

        # Write json
        with open(file_path, 'w') as f:
            f.write(dam_json)

2. Modify controller to use the new ``add_new_dam`` model function:

::

    from .model import add_new_dam

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

Create list_dams Model Method
=============================

Open ``models.py`` and add a model method for listing the dams called ``list_dams``:

::

    def get_all_dams():
        """
        Get all persisted dams.
        """
        # Write to file in app_workspace/dams/{{uuid}}.json
        # Make dams dir if it doesn't exist
        user_workspace = app.get_app_workspace()
        dams_dir = os.path.join(user_workspace.path, 'dams')
        if not os.path.exists(dams_dir):
            os.mkdir(dams_dir)

        dams = []

        # Open each file and convert contents to python objects
        for dam_json in os.listdir(dams_dir):
            dam_json_path = os.path.join(dams_dir, dam_json)
            with open(dam_json_path, 'r') as f:
                dam_dict = json.loads(f.readlines()[0])
                dams.append(dam_dict)

        return dams

Create List View Page
=====================

1. Add a new template ``templates/dam_inventory/list_dams.html`` with the following contents:

::

    {% extends "dam_inventory/base.html" %}

    {% block app_content %}
      <h1>Dams</h1>
      <table class="table table-hover">
        <thead>
          <tr>
            <th>Name</th>
            <th>Owner</th>
            <th>River</th>
            <th>Date Built</th>
          </tr>
        </thead>
        <tbody>
          {% for dam in dams %}
            <tr>
              <td>{{ dam.name }}</td>
              <td>{{ dam.owner }}</td>
              <td>{{ dam.river }}</td>
              <td>{{ dam.date_built }}</td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    {% endblock %}

2. Create a new controller function in ``controllers.py`` called ``list_dams``:

::

    from .model import add_new_dam, get_all_dams

    ...

    @login_required()
    def list_dams(request):
        """
        Show all dams in a table view.
        """
        dams = get_all_dams()
        context = {'dams': dams}
        return render(request, 'dam_inventory/list_dams.html', context)




3. Create a new URL Map in the ``app.py`` for the new ``list_dams`` controller:

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
                )
            )

            return url_maps

4. Open ``templates/dam_inventory/base.html`` and add navigation links for the List View page:

::

    {% block app_navigation_items %}
      <li class="title">App Navigation</li>
      {% url 'dam_inventory:home' as home_url %}
      {% url 'dam_inventory:add_dam' as add_dam_url %}
      {% url 'dam_inventory:dams' as list_dam_url %}
      <li class="{% if request.path == home_url %}active{% endif %}"><a href="{{ home_url }}">Home</a></li>
      <li class="{% if request.path == list_dam_url %}active{% endif %}"><a href="{{ list_dam_url }}">Dams</a></li>
      <li class="{% if request.path == add_dam_url %}active{% endif %}"><a href="{{ add_dam_url }}">Add Dam</a></li>
    {% endblock %}


Add Map Input to Add Dam Form
=============================

1. Use a Map View Gizmo to capture spatial input. Open ``templates/dam_inventory/add_dam.html`` and add the ``location_input`` gizmo to the form:

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

2. Add the definition of the ``location_input`` gizmo and validation code to the ``add_dam`` controller in ``controllers.py``:

::

    from tethys_sdk.gizmos import MapView, Button, TextInput, DatePicker, SelectInput, MVDraw, MVView

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

3. Modify the ``add_new_dam`` Model Method to store spatial data:

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
        user_workspace = app.get_app_workspace()
        dams_dir = os.path.join(user_workspace.path, 'dams')
        if not os.path.exists(dams_dir):
            os.mkdir(dams_dir)

        # Name of the file is its id
        file_name = str(new_dam_id) + '.json'
        file_path = os.path.join(dams_dir, file_name)

        # Write json
        with open(file_path, 'w') as f:
            f.write(dam_json)

Show Dams on the Map on the Home Page
=====================================

**IMPORTANT**: Delete all ``json`` files in the ``workspace/app_workspace/dams`` directory and create new entries using the Add Dam page.

Modify the ``home`` controller in ``controllers.py`` to map the list of dams:

::

    from tethys_sdk.gizmos import MapView, Button, TextInput, DatePicker, SelectInput, MVDraw, MVView, MVLayer

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

        dams_layer = MVLayer(
            source='GeoJSON',
            options=dams_feature_collection,
            legend_title='Dams'
        )

        # Define view centered on dam locations
        try:
            view_center = [sum(lng_list) / float(len(lng_list)), sum(lat_list) / float(len(lat_list))]
        except ZeroDivisionError:
            view_center = [-98.6, 39.8]

        view_options = MVView(
            projection='EPSG:4326',
            center=view_center,
            zoom=6,
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

