***********************
The View and Templating
***********************

**Last Updated:** November 12, 2014

In this section we'll discuss the View aspect of MVC. The View represents the visualizations of your app's data and the user interface. Views for Tethys apps are constructed using the standard web programming tools: HTML, JavaScript, and CSS. Additionally, the Django Python templating language allows you to insert Python code into your HTML, similar to how PHP is used. The result is dynamic, reusable templates for the web pages of your app. In this tutorial you will add a view to your app for displaying the stream gages on a Google Map.

Templating
==========

The Django template language is a simple, but powerful templating language. This section will provide a crash course in Django template language basics, but we highly recommend a review of the `Django Template Language <https://docs.djangoproject.com/en/1.7/topics/templates/>`_ documentation.

Browse to the your templates directory located at :file:`my_first_app/templates/my_first_app/`. By convention, all the templates for your app should be stored in a directory with the same name of your :term:`app package` inside the templates directory (e.g.: :file:`templates/my_first_app`). This will prevent potential conflicts with the templates of other apps. You will find two templates in this directory: :file:`base.html` and :file:`home.html`. Refer to these templates as different the Django template concepts are introduced.

Variables
---------

In Django templates, variables are denoted by double curly brace syntax: ``{{ variable }}``. The variable expression will be replaced by the value of the variable. Dot notation can be used access attributes of a variable: ``{{ variable.attribute }}``. For a more detailed explanation of variables, see `Django template Variables <https://docs.djangoproject.com/en/1.7/topics/templates/#variables>`_ documentation.

::

  # Examples of Django template variable syntax
  {{ variable }}

  # Access items in a list using dot notation
  {{ list.0 }}

  # Access items in a dictionary using dot notation
  {{ dict.key }}

  # Access attributes of objects using dot notation
  {{ object.attribute }}

Filters
-------

Variables can be modified by filters which look like this: ``{{ variable|filter:argument }}``. Refer to the `Django Filter Reference <https://docs.djangoproject.com/en/1.7/ref/templates/builtins/#ref-templates-builtins-filters>`_ for a full list of the filters available.

Tags
----
Tags use curly brace percent sign syntax like this: ``{% tag %}``. Tags perform many different functions including creating text, controlling flow, or loading external information to be used in the app. Some commonly used tags include ``for``, ``if``, ``block``, and ``extends``. See the `Django Tag Reference <https://docs.djangoproject.com/en/1.7/ref/templates/builtins/#ref-templates-builtins-tags>`_ for a complete list of tags that Django provides.

Template Inheritance
--------------------

One of the advantages of using the Django template language is that it provides a way for child templates to extend parent templates, which reduces the amount of HTML you need to write. Template inheritance is accomplished using two tags, ``extends`` and ``block``. Parent templates provide ``blocks`` of content that can be overridden by child templates. Child templates can extend parent templates by using the ``extends`` block and specifying the template they which to inherit from. Calling the block of a parent template in a child template will override any content in that block with the content in the child template. If you are unfamiliar with Django template inheritance, please review the `Django Template Inheritance <https://docs.djangoproject.com/en/1.7/topics/templates/#template-inheritance>`_ documentation before proceeding.

Base Template
-------------

Tethys apps generated from the scaffold come with a :file:`base.html` template which has the following contents:

::

    {% extends "tethys_apps/app_base.html" %}

    {% load staticfiles %}

    {% block title %}- {{ tethys_app.name }}{% endblock %}

    {% block styles %}
      {{ block.super }}
      <link href="{% static 'my_first_app/css/main.css' %}" rel="stylesheet"/>
    {% endblock %}

    {% block app_icon %}
      {# The path you provided in your app.py is accessible through the tethys_app.icon context variable #}
      <img src="{% static tethys_app.icon %}">
    {% endblock %}

    {# The name you provided in your app.py is accessible through the tethys_app.name context variable #}
    {% block app_title %}{{ tethys_app.name }}{% endblock %}

    {% block app_navigation_items %}
    {% endblock %}

    {% block app_content %}
    {% endblock %}

    {% block app_actions %}
    {% endblock %}

    {% block scripts %}
      {{ block.super }}
      <script src="{% static 'my_first_app/js/main.js' %}" type="text/javascript"></script>
    {% endblock %}

The :file:`base.html` contains several blocks that your app templates can override or extend. The Blocks you will use most often are``app_navigation_items``, ``app_content``, and, ``app_actions``. These blocks correspond with different parts of the app interface (shown in Figure 1). All of your app templates should extend the :file:`base.html` file. As a rule, content that you would like to be present in all your templates should be included in the :file:`base.html` and content that is specific to a certain template should be included in that template. A brief explanation of each block is provided.

.. figure:: ../images/template_blocks.png
    :width: 650px

    **Figure 1.** The blocks of the :file:`base.html` template correspond with different parts of the interface: (1) app_navigation_items, (2) app_content, and (3) app_actions.

title
-----

The ``title`` block is used to override the title of the current page (not to be confused with the ``app_title``). This usually shows up as the title of the tab in the web browser or as the default name of a bookmark. By default, this is set to the name of your app.

styles and scripts
------------------

The ``styles`` and ``scripts`` blocks should be used to import new CSS and JavaScript files, respectively. All apps include an empty CSS and JavaScript file located in the :file:`public` directory of your app. Invoking the ``block.super`` variable within a block will retain the content of the block from the parent template. You should always use the ``block.super`` construct when overriding the ``styles`` and ``scripts`` blocks.

app_icon
--------

The ``app_icon`` block is used to load the app icon into your app. If you would like to change the app icon image, do so via the ``icon`` property of your :term:`app class`.

app_title
---------

The ``app_title`` block can be used to change the title that is located in the header of your app.

app_navigation_items
--------------------

Use the ``app_navigation_items`` block to define the navigation section for your app. Add new items as list elements. Use the "title" class to style a navigation item as a Title item. Use the "active" class to highlight the item and the "separator" class to insert a dividing space. Here is an example of appropriate content for the ``app_navigation_items`` block:

::

    <li class="title">App Navigation</li>
    <li class="active"><a href="">Home</a></li>
    <li><a href="">Jobs</a></li>
    <li><a href="">Results</a></li>
    <li class="title">Steps</li>
    <li><a href="">1. The First Step</a></li>
    <li><a href="">2. The Second Step</a></li>
    <li><a href="">3. The Third Step</a></li>
    <li class="separator"></li>
    <li><a href="">Get Started</a></li>

app_actions
-----------

Use the ``app_actions`` block to add actions to your template. The app actions are the buttons that appear in the strip at the bottom of your app. One quirk of the ``app_actions`` block is that the actions need to be provided in reverse order of how they are to appear in the template. For example:

::

    <a href="" class="btn btn-default">Next</a>
    <a href="" class="btn btn-default">Back</a>

app_content
-----------

Use the ``app_content`` block to add content to your template.

Make a New Template
===================

Now that you know the basics of Django templating, create a new template in your templates directory (:file:`my_first_app/templates/my_first_app/`) and name it :file:`map.html`. Open this file and copy and paste the following code into it:

::

    {% extends "my_first_app/base.html" %}

    {% load tethys_gizmos %}

    {% block app_content %}
      <h1>Stream Gages</h1>
      {% gizmo editable_google_map map_options %}
    {% endblock %}

    {% block app_actions %}
      <a href="{% url 'my_first_app:home' %}" class="btn btn-default">Back</a>
    {% endblock %}

    {% block scripts %}
      {{ block.super }}
      {% gizmo_dependencies %}
    {% endblock %}

The :file:`map.html` template inherits from the :file:`base.html` in your templates directory. It also overrides the ``app_content``, `app_actions``, and ``scripts`` blocks. The ``url`` tag is used to provide a link back to the home page of the app in the ``app_actions`` block.

The map is inserted into the ``app_content`` block using one of the Tethys Gizmos called ``editable_google_map``. Gizmos are an easy way to insert common user interface elements in to your templates with minimal code. The map is configured via a dictionary called ``map_options``, which is defined in the controller. This will be discussed in the next tutorial. For more information on Gizmos, refer to the :doc:`../tethys_api/gizmos` documentation.

Public Files and Resources
==========================

Most apps will use files and resources that are static--meaning they do not need to be preprocessed before being served like templates do. Examples of these files include images, CSS files, and JavaScript files. Tethys Platform will automatically register static files that are located in the :file:`public` directory of your app project. Use the ``static`` tag in templates to load the resource URLs. See the `static tag <https://docs.djangoproject.com/en/1.7/ref/contrib/staticfiles/#static>`_ documentation for more details.

.. caution::

    Any file stored in the public directory will be accesible to anyone. Be careful not to expose sensitive information.
