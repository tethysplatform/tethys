***********
URL Mapping
***********

**Last Updated:** May 27, 2014

In this part of the tutorial, URL mapping will be introduced. It is likely that your app will have more than one controller. Everytime that you create a new controller you will need to map it to a URL. When this url is called, that controller will be executed. We'll illustrate the process of creating a new controller and mapping it to a URL for this first app.

Create a New Contoller
======================

1. Create a new file called :file:`new_controller.py` in your ``controllers`` package (:file:`~tethysdev/ckanapp-my_first_app/ckanapp/my_first_app/controllers/new_controller.py`).

2. Copy and paste the following code into `:file:`new_controller.py`:

::

    from ckan.lib.base import BaseController
    import ckan.plugins as p

    class NewController(BaseController):
        
        def index(self):
            # Tools
            t = p.toolkit
            c = t.c
                    
            return t.render('my_first_app/new_template.html')

First, we import the ``BaseController`` from the CKAN source. All new controller classes must inherit from ``BaseController``. We also import the ``plugins`` library from the CKAN source and alias it as ``p``. The ``plugins`` library contains the plugins toolkit that was discussed in the previous tutorial. We also define a method/action for our new contrller called ``index()``. All action does at this point is render the :file:`new_template.html`. template.

Create a New Template
=====================

The :file:`new_template.html` template doesn't exist yet, so we'll make it now:

1. Create a new file called :file:`new_template.html` in your :file:`templates` directory (:file:`~tethysdev/ckanapp-my_first_app/ckanapp/my_first_app/templates/my_first_app/new_template.html`).

2. Copy and paste the following lines into :file:`new_template.html`:

::

    {% extends "my_first_app/app_base.html" %}

    {% block breadcrumb_content %}
      <li><a href="{% url_for 'apps' %}">Apps</a></li>
      <li><a href="/apps/my-first-app">My First App</a></li>
      <li class="active"><a href="#">New Page</a></li>
    {% endblock %}

    {% block primary_content %}
      <div class="module">
        <div class="module-content">
          <h1>Hello World!</h1>
        </div>
      </div>
    {% endblock %}

    {% block secondary_content %}
      <div class="module module-narrow module-shallow">
        <h2 class="module-heading">
          <i class="icon-info-sign"></i>
          Welcome
        </h2>
        <div class="module-content">
        	<p>Welcome to my new page!</p> 
        </div>
      </div>
    {% endblock %}

Map Controller to URL
=====================

Now that we have a new controller that renders a new template, we need to map the controller to a URL. This is done in the :term:`app configuration file` (:file:`app.py`).

1. Open the :term:`app configuration file: for your app (:file:`~/tethysdev/ckanapp-my_first_app/ckanapp/my_first_app/app.py`) and locate the ``registerControllers()`` method of your :term:`app class`.

2. Add the following lines to the end of the ``registerControllers()`` method:

::

    controllers.addController(name='new_controller',
                              url='my-first-app/new-controller',
                              controller='my_first_app.controllers.new_controller:NewController',
                              action='index')

To register the new controller, we use the ``addController()`` method to:

1. give the new mapping a name ("new_controller"),
2. define the url pattern that will execute the controller ("my-first-app/new-controller"),
3. specify where the controller is located using dot notation path ("my_first_app.controllers.new_controller:NewController"),
4. and define the action (method) that will be called ("index")

That's all it takes to map the URL. Start/Restart the paster server and navigate to: http://localhost:5000/apps/my-first-app/new-controller .

.. note::

    The URLs that you use to map your controllers are relative to the "/apps" base URL. Also, all of your URL patterns should begin with your app's index (e.g.: 'my-first-app') to prevent conflicts with other apps.

URL Variables
=============

It is possible to embed variables in the URL. The next part of the tutorial will demonstrate how this is done.

1. Add the following lines to the end of the ``registerControllers()`` method in your :term:`app configuration file`:

::
    
    controllers.addController(name='new_controller_action',
                              url='my-first-app/new-controller/{action}',
                              controller='my_first_app.controllers.new_controller:NewController')

Compare this new controller mapping with the one we added in the previous section. This controller mapping points to the same controller class as the other one, but the URL contains a variable, ``action``, denoted by the curly braces. The ``action`` variable is a special variable, because it maps to the action/method that will be executed when the URL is requested. The new mapping definition omits the fourth argument (the ``action`` argument), because the action will be defined by the URL variable.

2. Copy and paste the following method definition to the end of the ``NewController`` class in the :file:`new_controller.py` file:

::

    def hello(self):
        # Tools
        t = p.toolkit
        c = t.c

        c.hello_name = 'Cosmo'

        return t.render('my_first_app/hello.html')

3. Create a new file in your templates directory called :file:`hello.html` and add the following contents:

::

    {% extends "my_first_app/app_base.html" %}

    {% block breadcrumb_content %}
      <li><a href="{% url_for 'apps' %}">Apps</a></li>
      <li><a href="/apps/my-first-app">My First App</a></li>
      <li class="active"><a href="#">Hello {{ c.hello_name }}</a></li>
    {% endblock %}

    {% block primary_content %}
      <div class="module">
        <div class="module-content">
          <h1>Hello, {{ c.hello_name }}!</h1>
        </div>
      </div>
    {% endblock %}

    {% block secondary_content %}
      <div class="module module-narrow module-shallow">
        <h2 class="module-heading">
          <i class="icon-info-sign"></i>
          Welcome
        </h2>
        <div class="module-content">
                <p>Welcome to my new page!</p>
        </div>
      </div>
    {% endblock %}

4. Navigate to the following URL in an internet browser: http://localhost:5000/apps/my-first-app/new-controller/hello

The last element of the URL, "hello", is mapped to the ``hello`` action and the :file:`hello.html` template is rendered. Similarly, http://localhost:5000/apps/my-first-app/new-controller/index will map to the original ``index`` action of the ``NewController``. You can add whatever variables you deem necessary, so long as the URL pattern is unique.

5. Add a new variable to the URL pattern by modifying the controller mapping in your :file:`app configuration file` from step 1 to look like this:

::

    controllers.addController(name='new_controller_action',
                              url='my-first-app/new-controller/{action}/{name}',
                              controller='my_first_app.controllers.new_controller:NewController')

6. The URL variables automatically passed to the template through the the template context object (``c``). In this case, the URL ``name`` variable will be accessible at ``c.name``. Modify the ``hello`` action in your ``NewController`` class to look like this:

::

    def hello(self):
        # Tools
        t = p.toolkit
        c = t.c

        c.hello_name = c.name

        return t.render('my_first_app/hello.html')

7. Now, name used in the URL ``name`` space will be passed to the template through the template context object (``c``). Navigate to http://localhost:5000/apps/my-first-app/new-controller/hello/Pete . The page should now render with a nice greeting for Pete: "Hello, Pete!" Replace Pete with your own name if you'd like.


.. hint::

    URL patterns need to be unique. For example, consider the following URL patterns:


    ::

        # Set 1
        url = 'my-first-app/{action}/{name}
        url = 'my-first-app/{id}/{property}

        # Set 2
        url = 'my-first-app/cats/{action}/{id}
        url = 'my-first-app/dogs/{action}/{id}

    The two URLs shown in Set 1, have variables with different names, but the URL pattern is the same. These URLs would not work because they are not unique. Pylons would not be able to accurately map the pattern to the appropriate controller. The URLs in Set 2, however, have unique patterns even though the varaibles are the same. Set 2 would be a valid set of URLs because the pattern is unique.
