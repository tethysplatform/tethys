***************************
Working with the Controller
***************************

**Last Updated:** May 27, 2014

The Controller component of MVC will be discussed in this part of the tutorial. The job of the controller is to coordinate between the View and the Model. Often this means querying a database and transforming the data to a format that the view expects it to be in. The Controller also handles most of the application logic such as processing and validating form data or launching model runs. In Tethys Apps, controllers are created as Python classes using the Pylons web framework. In this tutorial we will retrive the data from our stream gage model and then pass it to the template for visualizing.

Query Persitent Store
=====================

If you recall, in the :doc:`./persistent_stores` tutorial we created an SQLAlchemy data model to store information about our stream gages. We also created an initialization script that loaded some dummy data into our database. We will now add some logic to our controller to retrive this data:

1. Open your :file:`index.py` controller (:file:`~/tethysdev/ckanapp-my_first_app/ckanapp/my_first_app/controllers/index.py`).

There should be a class called ``MyFirstAppController`` that has one method called ``index()``. Notice that ``MyFirstAppController`` inherits from the ``BaseController`` class. This is what makes this class a controller. The ``index()`` method is the controller that renders the :file:`index.html` template that we worked on in the :doc:`./view` tutorial.

2. To retrieve the data from our data model, we need to import the ``StreamGage`` class from the :file:`stream_gage_model.py` file that we created in the :doc:`./persistent_stores` tutorial. Add the following line at the end of your import statements, just before the class definition:

::
    
    from ckanapp.my_first_app.stream_gage_model import StreamGage, SessionMaker


3. Recall that in the :doc:`./view` tutorial, we added a map :term:`snippet` that required ``c.map_options`` as input. We'll define that variable now. Add the following lines to the ``index()`` method of the controller, just before the ``return`` statement:

::
    
    # Get data for Map
    geojson_gages = StreamGage.get_gages_as_geojson()
    
    # Define map options
    c.map_options = {'height': '500px',
                     'width': '100%',
                     'maps_api_key': <google_maps_api_key>,
                     'drawing_types_enabled': ['POLYGONS', 'POINTS', 'POLYLINES'],
                     'initial_drawing_mode': 'POLYGONS',
                     'input_overlays': geojson_gages}

First we use the ``StreamGage.get_gages_as_geojson()`` class method to retrieve our gage information in GeoJSON format and store it in the ``geojson_gages`` variable. Next we define ``c.map_options`` to be a dictionary with all the configuration options we wish to use on our map. The ``geojson_gages`` variable is given to the map using the *input_overlays* option.

4. Finally, replace the **<google_maps_api_key>** with a string of your own Google Maps API key (e.g.: 'tH1$is@fAK3KeY'). To get a Google Maps API key, follow `these <https://developers.google.com/maps/documentation/javascript/tutorial#api_key>`_ instructions. **Please, do not use our API key**.

5. Now we need to define the ``c.stream_gages`` variable for the table in our template. Add the following lines to the ``index()`` method of your controller, just before the ``return`` statement:

::

    # Create a session
    session = SessionMaker()
    
    # Get data for table
    c.stream_gages = session.query(StreamGage).all()

First, a ``session`` object is created using the ``SessionMaker`` from the :file:`stream_gage_model.py` file we created in the :doc:`./persistent_stores` tutorial. Next, we use the SQLAlchemy query language to query our table for all the records. They are returned as a list of ``StreamGage`` objects. Our template processes loops through each of the objects and populates the table values with properties of the objects.

Your :file:`index.py` controller should look like this when you are finished:

::

    from ckan.lib.base import BaseController, abort
    import ckan.plugins as p

    from ckanext.tethys_apps.lib import get_app_definition

    from ckanapp.my_first_app.stream_gage_model import StreamGage, SessionMaker

    class MyFirstAppController(BaseController):
        
        def index(self):
            # Tools
            t = p.toolkit
            c = t.c
            _ = t._
            
            context = {'user': c.user or c.author}
             
            # Check permissions
            try:
                t.check_access('apps_read', context)
            except t.NotAuthorized:
                abort(401, _('Not authorized to see this page'))
                
            # Get App Definition
            app_definition = get_app_definition('my_first_app')
            
            c.app_name = app_definition['name']
            c.app_index = app_definition['index']
            
            # Get data for Map
            geojson_gages = StreamGage.get_gages_as_geojson()
            
            # Define map options
            c.map_options = {'height': '500px',
                             'width': '100%',
                             'maps_api_key': 'AIzaSyB-0nvmHhbOaaiYx6UN36145lWjUq5c2tg',
                             'drawing_types_enabled': ['POLYGONS', 'POINTS', 'POLYLINES'],
                             'initial_drawing_mode': 'POLYGONS',
                             'input_overlays': geojson_gages}
            
            # Create a session
            session = SessionMaker()
            
            # Get data for table
            c.stream_gages = session.query(StreamGage).all()
                    
            return t.render('my_first_app/index.html')

6. Activate the CKAN Python virtual environment and start the paster server:

::

    $ . /usr/lib/ckan/default/bin/activate
    $ paster serve --reload /etc/ckan/default/development.ini

7. Navigate to http://localhost:5000/apps Login/create a user if necessary to view the apps library. 

Your app should appear in the Apps library complete with a default image. Click on the app icon to start up the app. Your app has only one page, but you should have a map and a table of values. You can pan and zoom the map and even draw different shapes.

Controller Tools Reference
==========================

There are many tools available to work with in controllers. Some of the most commonly used tools will be summarized here as a reference.

Plugins Toolkit
---------------

CKAN provides a toolkit for developers who are building extensions for CKAN. This toolkit is also needed to build apps. The toolkit provides safe access to controller utilities like the Pylons ``request`` object, the ``template context`` object (c), the ``render()`` method, the ``redirect_to()`` method, and the ``get_action()`` method. The most commonly used tools will be discussed as part of this tutorial. Visit the `Plugins Toolkit <http://docs.ckan.org/en/ckan-2.2/extensions/plugins-toolkit.html>`_ docs in the CKAN documentation for more information.

Template Context
----------------

The `template context <http://ckan.readthedocs.org/en/ckan-2.2/extensions/plugins-toolkit.html#ckan.plugins.toolkit.c>`_ often called ``c`` is used to pass variables from the controller to the template. All templates are automatically given access to the ``c`` object. Any data that your template needs to render will need to be passed through the template context object. New variables can be assigned to the template context object using dot notation. The template context can be accessed through the toolkit. The following example illustrates how simple variables can be passed to the template:

::

    import ckan.plugins.toolkit as t
    c = t.c

    c.name = 'Bill'
    c.age = 25
    c.email_addresses = ['bill@example.com', 'b25@email.org']

Request
-------

The Pylons `request <http://ckan.readthedocs.org/en/ckan-2.2/extensions/plugins-toolkit.html#ckan.plugins.toolkit.request>`_ object contains all of the information that is submitted as part of the request including the HTML headers and GET and POST parameters. You will most often use this object to access the information submitted with a form. To access only parameters from a POST request use the ``request.POST`` property or for only GET request parameters use the ``request.GET``. If you want all parameters use the ``request.params`` property. The parameters are stored in a dictionary, where the keys will match the names of the input elements. Here is a simple example of how that can be done:

::

    import ckan.plugins.toolkit as t

    params = t.request.params

    name = params['name-input']
    age = params['age-input']
    email = params['email-input']

The ``request`` object also has a property called ``matchdict``. As the name suggests, ``matchdict`` is a dictionary and it contains all of the variables derived from the URL. A better explanation of this will be provided in the URL Mapping section.

Render
------

The `render <http://ckan.readthedocs.org/en/ckan-2.2/extensions/plugins-toolkit.html#ckan.plugins.toolkit.render>`_ method of the toolkit is used to render the Jinja2 templates. This is most often used as the return value of a controller action. Consider the following example:

::

    from ckan.lib.base import BaseController
    import ckan.plugins.toolkit as t

    class ExampleController(BaseController):
        '''
        Example controller
        '''

        def index(self):
            # Template Context
            c = t.c

            # Template variables
            c.name = 'Bill'
            c.age = 25
            c.email_addresses = ['bill@example.com', 'b25@email.org']

            return t.render('my_first_app/index.html')

This is the class for a controller called "ExampleController" with one method called "index". What makes this class a controller is that it inherits from the ``BaseController`` class provided by CKAN. The methods of controllers are called actions. Most actions will result in some template being rendered. This is done by using the ``render()`` method of the toolkit. The method accepts the path to the template that is to be rendered (relative to your app's templates directory).

Redirect
--------

In some cases, you will need to redirect an action to another controller or action. This can be done by using the ``redirect_to()`` method as the return value of the action. Pass the name of the controller and any URL variables to the `redirect_to <http://ckan.readthedocs.org/en/ckan-2.2/extensions/plugins-toolkit.html#ckan.plugins.toolkit.redirect_to>`_ method. For example:

::

    from ckan.lib.base import BaseController
    import ckan.plugins.toolkit as t

    class ExampleController(BaseController):
        '''
        Example controller
        '''

        def index(self):
            # Template Context
            c = t.c

            # Template variables
            c.name = 'Bill'
            c.age = 25
            c.email_addresses = ['bill@example.com', 'b25@email.org']

            return t.redirect_to(controller='other_controller', action='view')

Get Action
----------

CKAN provides programming API that can be used to interact with datasets and resources called the Actions API. It is divided into four categories based on the type of operation being performed including get, create, update, and delete. For a complete reference refer to the CKAN `Actions API reference <http://ckan.readthedocs.org/en/ckan-2.2/api.html#action-api-reference>`_. Use the `get_action <http://ckan.readthedocs.org/en/ckan-2.2/extensions/plugins-toolkit.html#ckan.plugins.toolkit.get_action>`_ method of the toolkit to access these actions like so:

::

    import ckan.plugins.toolkit as t

    t.get_action('package_create')(context, data_dict)

Most Action API methods accept two parameters: ``context`` and ``data_dict``. The ``context`` accepts the template context object (``c``). The ``data_dict`` argument accepts a dictionary containing the key-value arguments for the action as specified in the Action API documentation.
