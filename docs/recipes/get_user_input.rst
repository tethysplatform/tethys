.. _get_user_input_recipe :


**************
Get User Input
**************

**Last Updated:** September 2025

HTML forms are the primary mechanism for obtaining input from users of your app.  

First, you will need to configure your inputs using Tethys Gizmos by adding them to your controller like so:

1. Define the options for the form gizmos in the controller in :file:`controllers.py`.

.. code-block:: python

    from tethys_sdk.routing import controller
    from tethys_sdk.gizmos import TextInput, DatePicker, SelectInput, Button
    from .app import App
    
    @controller
    def home(request):
        """
        Controller for the app home page.
        """
        # Define form gizmos
        name_input = TextInput(
            display_text='Name',
            name='name'
        )

        owner_name_input = TextInput(
            display_text='Owner Name',
            name='owner_name'
        )        

        measurement_type_input = SelectInput(
            display_text = 'Measurement Type',
            name='measurement_type',
            options=[('Streamflow', 'streamflow'), 
                    ('Temperature', 'temperature'), 
                    ('Water Level', 'water_level')]
            select2_options={'placeholder': 'Select a measurement type'}
        )

        date_added_input = DatePicker(
            name='date_added',
            display_text='Date Added',
            autoclose=True,
            format='MM d, yyyy',
            start_view='decade',
            today_button=False,
        )

        submit_button = Button(
            display_text='Submit',
            name='submit-button',
            icon='plus-square',
            style='success',
            attributes={'form': 'add-gauge-form'},
            submit=True
        )

        context = {
            'name_input': name_input,
            'owner_name_input': owner_name_input,
            'measurement_type_input', measurement_type,
            'date_added_input': date_added_input,
            'submit_button': submit_button,
        }

        return App.render(request, 'home.html', context)


2. Add a form to `home.html` file by replacing the contents of the app_content block with the following: 

.. code-block:: HTML+django
    :emphasize-lines: 2-10
    
    {% block app_content %}
        <h1>Add New Gauge</h1>
        <form id="add-gauge-form" method="post">
            {% csrf_token %}
            {% gizmo name_input %}
            {% gizmo owner_name_input %}
            {% gizmo measurement_type_input %}
            {% gizmo date_added_input %}
            {% gizmo submit_button %}
        </form>
    {% endblock %}


The form is composed of the the HTML ``<form>`` tag and various input gizmos inside it. We'll use the ``submit_button`` gizmo to submit the form. Also note the use of the ``csrf_token`` tag in the form. This is a security precaution that is required to be included in all the forms of your app (see the `Cross Site Forgery protection <https://docs.djangoproject.com/en/2.2/ref/csrf/>`_ article in the Django documentation for more details).
Also note that the ``method`` attribute of the ``<form>`` element is set to ``post``. This means the form will use the POST HTTP method to submit and transmit the data to the server. For an introduction to HTTP methods, see `The Definitive Guide to GET vs POST <https://blog.teamtreehouse.com/the-definitive-guide-to-get-vs-post>`_.

.. note:: In this code block the form is being added to the main content area of the page.  Forms can be added anywhere you need them in your app by changing the template.
.. TODO check with Nathan on this note.  Also add link to extending templates

3. update your controller to handle form submissions by adding the highlighted dependency and updating the `home` controller.

.. code-block:: python
    :emphasize-lines: 1, 10-13, 16-41

    from django.contrib import messages
    ...
    
    @controller
    def home(request):
        """
        Controller for the Add Gauge page.
        """

        name_error = ''
        owner_name_error = ''
        measurement_type_error = ''
        date_added_error = ''

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

            if not has_errors:
                messages.success(request, f"Added gauge {name}!")
        
        name_input = TextInput(
            display_text='Name',
            name='name'
        )

        owner_name_input = TextInput(
            display_text='Owner Name',
            name='owner_name'
        )        

        measurement_type_input = SelectInput(
            display_text = 'Measurement Type',
            name='measurement_type',
            options=[('Streamflow', 'streamflow'), 
                    ('Temperature', 'temperature'), 
                    ('Water Level', 'water_level')]
            select2_options={'placeholder': 'Select a measurement type'}
        )

        date_added_input = DatePicker(
            name='date_added',
            display_text='Date Added',
            autoclose=True,
            format='MM d, yyyy',
            start_view='decade',
            today_button=False,
        )

        submit_button = Button(
            display_text='Submit',
            name='submit-button',
            icon='plus-square',
            style='success',
            attributes={'form': 'add-gauge-form'},
            submit=True
        )

        context = {
            "name_input": name_input,
            "owner_name_input": owner_name_input,
            "measurement_type_input": measurement_type_input,
            "date_added_input": date_added_input,
            "submit_button": submit_button
        }

        return App.render(request, "home.html", context)

The final product should look something like this:

.. figure:: ../../docs/images/recipes/user_input.png
    :width: 800px
    :align: center

.. tip::

    **Form Validation Pattern**: The example above implements a common pattern for handling and validating form input. Generally, the steps are:

    1. **Define a "value" variable for each input in the form and assign it the initial value for the input**
    2. **Define an "error" variable for each input to handle error messages and initially set them to the empty string**
    3. **Check to see if the form is submitted and if the form has been submitted:**
        a. Extract the value of each input from the GET or POST parameters and overwrite the appropriate value variable from step 1
        b. Validate the value of each input, assigning an error message (if any) to the appropriate error variable from step 2 for each input with errors.
        c. If there are no errors, save or process the data. 
        d. If there are errors continue on and re-render the form with error messages
    4. **Define all gizmos and variables used to populate the form:**
        a. Pass the value variable created in step 1 to the ``initial`` argument of the corresponding gizmo
        b. Pass the error variable created in step 2 to the ``error`` argument of the corresponding gizmo
    5. **Render the page, passing all gizmos to the template through the context**

        
.. tip:: For more details on form Gizmos see the :ref:`Gizmos Documentation<gizmos_api>`.
