***********************
The View and Templating
***********************

**Last Updated:** May 23, 2014

In this section we'll discuss the View aspect of MVC. The View represents the visualizations of your app's data and the user interface. Views for Tethys Apps are constructed using the standard web programming tools: HTML, JavaScript, and CSS. Additionally, the Jinja2 Python templating language allows you to insert Python code into your HTML, similar to how PHP is used. The result is dynamic, reusable templates. In this tutorial we will continue with our stream gages example. We'll add a view that will display our stream gages for the user on a Google Map.

Templating
==========

Jinja2 is a simple, but powerful templating language. This section will provide a crash course in the templating language, but we highly recommend a review of the `Jinja2 documentation <http://jinja.pocoo.org/docs/>`_ for a better understanding.

Browse to the your templates directory (:file:`~/tethysdev/ckanapp-my_first_app/ckanapp/my_first_app/templates/my_first_app`). By convention, all the templates for your app should be stored in a directory with the same name of your :term:`app package` inside the templates directory (e.g.: :file:`templates/my_first_app`). This convention is followed to prevent conflicts with other apps. You will find two templates in this directory: :file:`app_base.html` and :file:`index.html`. Refer to these templates as different Jinja2 concepts are introduced.

Variables and Expressions
-------------------------

All Jinja2 statements are denoted using two forms of tags: double curly braces ``{{ variable }}`` or curly brace percent sign ``{% function argument1, argument2 %}``. The double curly brace syntax is used to print the values of variables into your templates. The curly brace percent sign syntax is used to execute expressions.

Extends
-------

One of the advantages of using Jinja2 is that it provides a way for one template to extend another. If you open the :file:`index.html` template, you'll see that the first line uses the Jinja2 ``extends()`` method:

::

    {% extends "my_first_app/app_base.html" %}

The :file:`index.html` template is extending the :file:`app_base.html` template, meaning it inherits from the :file:`app_base.html` file. If you open the :file:`app_base.html` file, you will see that it extends :file:`page.html`, which in turn extends :file:`base.html`. :file:`page.html` and :file:`base.html` are templates provided by the CKAN system. The ``extends()`` method allows you to create templates that are reusable and it will prevent unneccesary duplicate code.

For example, if you are familiar with HTML, you know all HTML documents have two main parts: the *head* and the *body*. :file:`index.html` has no *head* or *body* tags. This skeleton structure (head and body) for all pages in CKAN is provided in the :file:`base.html`. All templates inherit from this page eventually. But what if you want to modify something in the *head* tag like add a style sheet reference specific to your current template? That is where blocks come in.

Blocks
------

Parent templates inherit content from child templates through blocks. For example, open :file:`app_base.html`. This file defines 5 blocks using the ``block()`` method: *styles*, *breadcrumb_content*, *primary_content*, *secondary_content*, and *scripts*. Templates that extend :file:`app_base.html`, or child templates, are allowed to replace content in any of the blocks that :file:`app_base.html` defines by calling the same blocks.

Now open :file:`index.html`. This file extends :file:`app_base.html` and it defines content for the *breadcrumb_content*, *primary_content*, and *secondary_content* blocks. If a block is not implemented by a child template, it will retain whatever content was in the block on the parent template.

If you would like to keep the content of the parent page and add to it, use the ``super()`` method within the block.  For example, the :file:`app_base.html` template inherits all of the CSS scripts from the :file:`page.html` that it extends and adds one additional scripts specific to the app:

::

    {% block styles %}
        {{ super() }}
        {% resource 'ckanapp_my_first_app/css/my_first_app.css' %}
    {% endblock%}

We recommend that all of your app templates inherit from the :file:`app_base.html` template. If you need to import any CSS or javascript libraries that need to be accessible to all templates, add them to the :file:`app_base.html` template and they will be made to all pages that extend it.

.. hint::

    The templates that inherit from :file:`app_base.html` also inherit all of the blocks from :file:`page.html` and :file:`base.html`. This is because :file:`app_base.html` extends :file:`page.html` and :file:`page.html` extends :file:`base.html`. If you would like to see what blocks are available to implement in :file:`page.html` or :file:`base.html`, they can be found in the CKAN source in this directory: :file:`/usr/lib/ckan/default/src/ckan/ckan/public/templates`.

Add Map to Template
===================

Now that you know the basics with templating in Jinja2, let's add a map to our :file:`index.html` template for viewing the stream gages in our database. We'll also add a table under the map that will list the values in our database in a tabular format.

1. Open your :file:`index.html` template (:file:`~/tethysdev/ckanapp-my_first_app/ckanapp/my_first_app/templates/my_first_app/index.html`).

2. Locate the *primary_content* block and add the following link just under the *Heading 1* tag (``<h1>``):

::

    {% snippet "snippets/editable_google_map.html", options=c.map_options %}

This line will add our map. It uses the ``snippet()`` method and takes two arguments: a path to a snippet template and an options dictionary. Snippets are bits of HTML, CSS, and JavaScript that can be inserted in any template using the ``snippet()`` method (see :ref:`snippets-blurb`). The editable Google Map template inserts a Google Map with some editing capabilites.

Notice for the second argument, we pass a variable called ``c.map_options``. The ``c`` object is a special variable also called the template context. The template context contains any variables that we have passed to a template from its controller. The options for the map snippet are defined in our controller and passed to :file:`index.html` via the template context object. We'll discuss this more in the next tutorial.

Add Table to Template
=====================

Next let's add the table. First, we will only want to show the table if we have values to show. So we will use a conditional statement. We'll also use a for loop statement to create the rows of our table.

3. Insert the following lines after the snippet statement from the previous step:

::

          {% if c.stream_gages %}
            <table class="table">
              <tr>
                <th>Latitude</th>
                <th>Longitude</th>
                <th>Value</th>
              </tr>
              {% for stream_gage in c.stream_gages %}
              <tr>
                <th>{{ stream_gage.latitude }}</th>
                <th>{{ stream_gage.longitude }}</th>
                <th>{{ stream_gage.value }}</th>
              </tr>
              {% endfor %}
            </table>
          {% endif %}

We plan on the data being sent as a list to the template in a variable called ``c.stream_gages``. Two new Jinja2 expressions are introduced with this code. The conditional statement ``{% if <condition> %}{% endif %}`` is used to check whether the ``c.stream_gages`` variable is defined. If it is not defined, none of the contents of the conditional statement will be inserted into the HTML template (i.e.: there will be no table if there is no stream gage data). The loop statement ``{% for <item> in <iterable> %}{% endfor %}`` repeats it's contents for every iteration of the loop. In this case, the loop will create a row in the table for every stream gage in our ``c.stream_gages`` list.

When you are done, your :file:`index.html` template should look like this:

::

    {% extends "my_first_app/app_base.html" %}

    {% block breadcrumb_content %}
      <li><a href="{% url_for 'apps' %}">Apps</a></li>
      <li class="active"><a href="{% url_for(c.app_index) %}">{{ c.app_name }}</a></li>
    {% endblock %}

    {% block primary_content %}
      <div class="module">
        <div class="module-content">
          <h1>My First App</h1>
	      {% snippet "snippets/editable_google_map.html", options=c.map_options %}

          {% if c.stream_gages %}
            <table class="table table-bordered">
              <tr>
                <th>Latitude</th>
                <th>Longitude</th>
                <th>Value</th>
              </tr>
              {% for stream_gage in c.stream_gages %}
              <tr>
                <th>{{ stream_gage.latitude }}</th>
                <th>{{ stream_gage.longitude }}</th>
                <th>{{ stream_gage.value }}</th>
              </tr>
              {% endfor %}
            </table>
          {% endif %}
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
        	<p>This is a basic app generated from the scaffold provided by Tethys SDK. Use this as a 
        	   starting point for all new apps.</p> 
        </div>
      </div>
    {% endblock %}

.. _snippets-blurb:

Snippets
========

The other important templating construct that will save you time are :term:`snippets`. Snippets are pre-packaged chunks of HTML and JavaScript that can be used to insert commonly used user interface elements with minimal code. One of the major features of the Tethys Apps plugin is that it provides some specialized :term:`snippets` that can be used to build scientific apps including: buttons, date pickers, auto completes, toggle switches, text inputs, plots, and maps.

The ``snippet()`` method takes a one or more arguments. The first argument is always the path to the snippet template. The other arguments depend on the snippet. All of the Tethys Apps snippets accept a Python dictionary for the second argument called options. The dictionary containes all of the configuration options for the snippet.

Detailed documentation for all snippets provided by Tethys Apps is provided at a hidden url. You must have the Tethys Apps plugin installed to view the documentation. This page provides live demos, explanations, and example code for each :term:`snippet`. An example :term:`snippet` showcase url would be:

::

    http://www.example.org/apps/snippet-showcase

.. hint::

    If you are viewing these docs on the machine where you have CKAN and Tethys Apps running, you can access the snippet showcase here: http://localhost:5000/apps/snippet-showcase

Public Files and Resources
==========================

Most apps will use files and resources that are static--meaning they do not need to be preprocessed before being served like templates do. Examples of these files include images, CSS files, and JavaScript files. If you generate your app using the scaffold, it will be preconfigured to look for these types of files in a directory named :file:`public`. For most apps, this will be the only diretory you will need to store static files. If you use this directory to store your static files, you will not need to alter any configuration settings.

By default, the public directory is also configured as a resource library. JavaScript and CSS files in a resource directory can be included in an HTML template using the Jinja2 ``resource()`` method. For example, using the default resources configuration you can use the following line to import JavaScript and CSS files:

::

    {% resource 'ckanapp_my_first_app/css/my_first_app.css' %}

or 

::

    {% resource 'ckanapp_my_first_app/js/my_first_app.js' %}

Each resource directory is given an name. In this case our resource directory is called "ckanapp_my_first_app" and it points at the :file:`public` directory in our :term:`app package`. Therefore, all CSS and JavaScript files inside the :file:`public` directory are available to import as resources.

Resources are served using `Fanstatic <http://www.fanstatic.org/en/latest/>`_. For more details on resources, see `this <http://ckan.readthedocs.org/en/ckan-2.2/resources.html?highlight=resources>`_ article from the CKAN documentation. To add more resources to an app, use the ``registerResources()`` method in the :term:`app configuration file` (:file:`app.py`).

.. caution::

    Any file stored in the public directory will be accesible to anyone. Be careful not to expose sensitive information.


View Configuration
==================

There are several configuration options for views that can be set in the :term:`app configuration file` (:file:`app.py`). The applicable methods are: ``registerTemplateDirectories()``, ``registerPublicDirectories()``, and ``registerResources()``. Use ``registerTemplateDirectories()`` to specify where the templates for you app can be found. The ``registerPublicDirectories()`` should be used to define the location of your static resouces and the ``registerResources()`` method can be used to register directories where resouces are located. See :doc:`./configuration` for details about each configuration method. 
