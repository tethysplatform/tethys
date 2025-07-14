.. _get_user_input:


**************
Get User Input
**************

HTML forms are the primary mechanism for obtaining input from users of your app.  

First, you will need to configure your inputs using Tethys Gizmos by adding them to your controller like so:

1. Define the options for the form gizmos in the controller in :file:`controllers.py`.

.. code-block:: python

    from tethys_sdk.gizmos import TextInput, DatePicker, SelectInput, Button
    from .app import App
    
    @controller(url='users/add')
    def add_user(request):
        """
        Controller for the Add User page.
        """
        # Define form gizmos
        name_input = TextInput(
            display_text='Name',
            name='name'
        )

        title_input = SelectInput(
            display_text='Title',
            name='title',
            multiple=False,
            options=[('Mr.', 'Mr.'), ('Mrs.', 'Mrs.'), ('Ms.', 'Ms.')],
            initial=['Mr.']
        )

        birthday_input = DatePicker(
            name='birthday',
            display_text='Birthday',
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
            attributes={'form': 'add-user-form'},
            submit=True
        )

        context = {
            'name_input': name_input,
            'title_input': title_input,
            'birthday_input': birthday_input,
            'submit_button': submit_button,
        }

        return App.render(request, 'add_user.html', context)


2. Add a form to `add_user.html` file with the following: 

.. code-block:: HTML+django

    {% block app_content %}
    <h1>Add New User</h1>
    <form id="add-user-form" method="post">
        {% csrf_token %}
        {% gizmo name_input %}
        {% gizmo title_input %}
        {% gizmo birthday_input %}
        {% gizmo submit_button %}
    </form>
    {% endblock %}


The form is composed of the the HTML ``<form>`` tag and various input gizmos inside it. We'll use the ``submit_button`` gizmo to submit the form. Also note the use of the ``csrf_token`` tag in the form. This is a security precaution that is required to be included in all the forms of your app (see the `Cross Site Forgery protection <https://docs.djangoproject.com/en/2.2/ref/csrf/>`_ article in the Django documentation for more details).
Also note that the ``method`` attribute of the ``<form>`` element is set to ``post``. This means the form will use the POST HTTP method to submit and transmit the data to the server. For an introduction to HTTP methods, see `The Definitive Guide to GET vs POST <https://blog.teamtreehouse.com/the-definitive-guide-to-get-vs-post>`_.

.. note:: In this code block the form is being added to the main content area of the page.  Forms can be added anywhere you need them in your app by changing the template.
.. check with Nathan on this note.  Also add link to extending templates

3. update your controller to handle form submissions by adding the highlighted dependency and updating the `add_user` controller.

.. code-block:: python
    :emphasize-lines: 1

    from django.contrib import messages
    ...
    
    @controller(url='users/add')
    def add_user(request):
        """
        Controller for the Add User page.
        """

        name_error = ''
        title_error = ''
        birthday_error = ''

        # Handle form submission
        if request.POST and 'submit-button' in request.POST:
            # Get values
            has_errors = False
            name = request.POST.get('name', None)
            title = request.POST.get('title', None)
            birthday = request.POST.get('birthday', None)

            if not name:   
                has_errors = True
                name_error = 'Name is required'

            if not title:
                has_errors = True
                title_error = 'Title is required'

            if not birthday:
                has_errors = True
                birthday_error = 'Birthday is required'

            if not has_errors:
                messages.success(request, f"Welcome, {title} {name}!")
        
        name_input = TextInput(
            display_text='Name',
            name='name',
            error=name_error
        )

        title_input = SelectInput(
            display_text='Title',
            name='title',
            multiple=False,
            options=[('Mr.', 'Mr.'), ('Mrs.', 'Mrs.'), ('Ms.', 'Ms.')],
            initial=['Mr.'],
            error=title_error
        )

        birthday_input = DatePicker(
            name='birthday',
            display_text='Birthday',
            autoclose=True,
            format='MM d, yyyy',
            start_view='decade',
            today_button=False,
            error=birthday_error
        )

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

        
.. tip:: For more details on form Gizmos see the :ref:`gizmos_api`.