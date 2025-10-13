.. _file_upload_recipe :


*************
Upload a File
*************

**Last Updated:** September 2025

Prerequisite: :ref:`Get User Input Recipe<get_user_input_recipe>`

This recipe will show you how to enable users to upload files to use in your app.

Add a File Input to Your Form
#############################

Begin by adding a file input line to your form:

.. code-block:: html+django
    :emphasize-lines: 7

    <form id="add-gauge-form" method="post">
        ...
        <input type="file" name='measurements'>
        ...
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
            ...

            if request.FILES and 'measurements' in request.FILES:
                measurements_file = request.FILES.getlist('measurements')
                for line in measurements_file:
                    line = line.decode('utf-8')
                    sline = line.split(',')
                    date = sline[0]
                    value = sline[1]
                    print(f"{date}, {value}")

                ...
            

These new lines enter the file and print out each line of the file to the console. This example assumes a CSV file has been uploaded. 
You can download an example CSV file for testing :download:`here <../_static/example_files/recipes/stream_height_measurements.csv>`

That's it! That's all you need to do to begin accepting file uploads from users in your very own Tethys App. 

A good next step for an app like this would be to save these measurements to a database. If you need help setting up a database to store this information you can find instructions :ref:`here<create_database_models_recipe>`