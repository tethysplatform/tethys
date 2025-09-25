.. _file_upload_recipe :


*************
Upload a File
*************

**Last Updated:** September 2025

Prerequisite: :ref:`Get User Input Recipe<_recipe>`

This recipe will show you how to enable users to upload files to use in your app.

Add a File Input to Your Form
#############################

Begin by adding an `input` line to your form:

.. code-block:: html+django
    :emphasize-lines: 7

    <form id="add-gauge-form" method="post">
        {% csrf_token %}
        {% gizmo name_input %}
        {% gizmo owner_name_input %}
        {% gizmo measurement_type_input %}
        {% gizmo date_added_input %}
        <input type="file" name='measurements'>
        {% gizmo submit_button %}
    </form>
    {% endblock %}

This input will allow users to add files to this form to upload along with the rest of their data.

Update Controller Logic
#######################

Next, update your controller that handles the add-guage-form's input:

.. code-block:: python
    :emphasize-lines: 38-48
    
    @controller(url='gauges/add')
    def add_gauges(request):
        """
        Controller for the Add Gauge page.
        """

        name_error = ''
        owner_name_error = ''
        measurement_type_error = ''
        date_added_error = ''
        measurements_error = ''

        # Handle form submission
        if request.POST and 'submit-button' in request.POST:
            # Get values
            has_errors = False
            name = request.POST.get('name', None)
            owner_name = request.POST.get('owner_name', None)
            measurement_type = request.POST.get('measurement_type', None)
            date_added = request.POST.get('date_added', None)

            if not name:   
                has_errors = True
                name_error = 'Name is required'

            if not owner_name:
                has_errors = True
                owner_name_error = 'Owner name is required'

            if not measurement_type:
                has_errors = True
                measurement_type_error = 'Measurement type is required'

            if not date_added:
                has_errors = True
                date_added_error = 'Date added is required'

            if request.FILES and 'measurements' in request.FILES:
                measurements_file = request.FILES.getlist('measurements')
                for line in measurements_file:
                    line = line.decode('utf-8')
                    sline = line.split(',')
                    date = sline[0]
                    value = sline[1]
                    print(f"{date}, {value}")
            else:
                has_errors = True
                measurements_error = 'Measurements are required'

            if not has_errors:
                messages.success(request, f"Added gauge {name}!")

These new lines enter the file and print out each line of the file to the console. This example assumes a CSV file has been uploaded. 
You can download an example CSV file for testing :download:`here <../_static/example_files/recipes/stream_height_measurements.csv>`

That's it! That's all you need to do to begin accepting file uploads from users in your very own Tethys App. 

A good next step for an app like this would be to save these measurements to a database. If you need help setting up a database to store this information you can find instructions :ref:`here<create_database_models>`