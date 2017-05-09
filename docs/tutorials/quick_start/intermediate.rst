************************
App Basics: Intermediate
************************

**Last Updated:** May 2017

* Advanced Gizmos API (Plotting and Mapping) - Hard code data / empty
* Custom App Settings API (control default color of points on map?)
* HTML Forms and Getting Input from users - use map in form for input
* Navigation Links
* Workspaces API (Write data submitted to file temporarily?)

Narrative
* Create HTML Form on "Add Dam" page using gizmos w/out map initially
* Illustrate how to submit form and extract data on server
* Save data to a json file for now in the User Workspace
* Add Map to new dam form with only point input enabled and show how spatial data is serialized
* Add spatial data to json that is written
* Create a new page that lists all data in table form
* Add navigation links to get back to home and to table form
* Add dams in files to the map
* Plot something? Hydrograph creator?

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

Add a form to the Add Dam page by modifying the ``templates/dam_inventory/add_dam.html`` template as follows:

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

Define Form Gizmos
==================

Define the form gizmos and change the Add button to a submit button for the Add Dam form in the ``add_dam`` controller:

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
            options=[('Reclamation', 'reclamation'), ('Army Corp', 'armycorp'), ('Other', 'other')],
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
        owner = 'reclamation'
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

Intro to model...
Intro to workspaces API...

Open ``model.py`` and add this function:

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
        dam_dict = {
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
        new_dam_id = uuid.uuid4()
        file_name = str(new_dam_id) + '.json'
        file_path = os.path.join(dams_dir, file_name)

        # Write json
        with open(file_path, 'w') as f:
            f.write(dam_json)

Modify controller to use the new ``add_new_dam`` model function:

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

Create Table View Page
======================

Add Navigation Links for Table View Page
========================================

Add Map Input to Add Dam Form
=============================

Modify add_new_dam Model Method to Store Spatial Data
=====================================================

Modify list_dams Model Method to Return Spatial Data
====================================================

Show Dams on the Map on the Home Page
=====================================

