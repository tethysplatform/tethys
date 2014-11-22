******************
App Templating API
******************

**Last Updated:** November 21, 2014

.. warning::

    **UNDER CONSTRUCTION**

The templates for apps developed in Tethys Platform are created using the Django template language. This article discusses pertinent Django templating concepts and the base templates that are provided by Tethys Platform..

Django Templating Concepts
==========================

The Django template language allows you to create dynamic HTML templates and will minimize the amount of HTML you need to write. This section will provide a crash course in Django template language basics, but we highly recommend a review of the `Django Template Language <https://docs.djangoproject.com/en/1.7/topics/templates/>`_ documentation.

Variables
---------

In Django templates, variables are denoted by double curly brace syntax: ``{{ variable }}``. The variable expression will be replaced by the value of the variable. Dot notation can be used access attributes of a variable: ``{{ variable.attribute }}``.

See `Django template Variables <https://docs.djangoproject.com/en/1.7/topics/templates/#variables>`_ documentation.

::

  # Examples of Django template variable syntax
  {{ variable }}

  # Access items in a list or tuple using dot notation
  {{ list.0 }}

  # Access items in a dictionary using dot notation
  {{ dict.key }}

  # Access attributes of objects using dot notation
  {{ object.attribute }}

Filters
-------

Variables can be modified by filters which look like this: ``{{ variable|filter:argument }}``. Filters perform modifying functions on variable output such as formatting dates, formatting numbers, changing the letter case, and concatenating multiple variables.

Refer to the `Django Filter Reference <https://docs.djangoproject.com/en/1.7/ref/templates/builtins/#ref-templates-builtins-filters>`_ for a full list of the filters available.

Tags
----

Tags use curly brace percent sign syntax like this: ``{% tag %}``. Tags perform many different functions including creating text, controlling flow, or loading external information to be used in the app. Some commonly used tags include ``for``, ``if``, ``block``, and ``extends``.

See the `Django Tag Reference <https://docs.djangoproject.com/en/1.7/ref/templates/builtins/#ref-templates-builtins-tags>`_ for a complete list of tags that Django provides.

Template Inheritance
--------------------

One of the advantages of using the Django template language is that it provides a way for child templates to extend parent templates, which can reduce the amount of HTML you need to write. Template inheritance is accomplished using two tags, ``extends`` and ``block``. Parent templates provide ``blocks`` of content that can be overridden by child templates. Child templates can extend parent templates by using the ``extends`` tag. Calling the ``block`` tag of a parent template in a child template will override any content in that ``block`` tag with the content in the child template.

If you are unfamiliar with Django template inheritance, please review the `Django Template Inheritance <https://docs.djangoproject.com/en/1.7/topics/templates/#template-inheritance>`_ documentation.


Base Templates
==============

There are two layers of templates provided for Tethys app development. The :file:`app_base.html` template provides the HTML skeleton for all Tethys app templates. All Tethys app projects also include a :file:`base.html` template that inherits from the :file:`app_base.html` template.

App developers are encouraged to use the :file:`base.html` file as the base template for all of their templates, rather than extending the :file:`app_base.html` file directly. The :file:`base.html` template is easier to work with, because it includes only the blocks that will be used most often from the :file:`app_base.html` template. However, all of the blocks that are available from :file:`app_base.html` template will also be available for use in the :file:`base.html` template and any templates that extend from it.

Many of the blocks in these template correspond with different portions of the app interface. Figure 1 provides a graphical representation of these blocks.

.. figure:: ../images/detailed_template_blocks.png
    :width: 650px

    **Figure 1.** Blocks that correspond with app interface elements.

This section provides an explanation of the blocks that can be used in child templates of either :file:`app_base.html` template or the :file:`base.html` template.

Blocks
======

htmltag
-------

Override the ``<html>`` element open tag.

*Example:*

::

    {% block htmltag %}<html lang="es">{% endblock %}

headtag
-------

Add attributes to the ``<head>`` element.

*Example:*

::

    {% block headtag %}style="display: block;"{% endblock %}

meta
----

Override or append ``<meta>`` elements to the ``<head>`` element. To append to existing elements, use ``block.super``.

*Example:*

::

    {% block meta %}
      {{ block.super }}
      <meta name="description" value="My website description" />
    {% endblock %}

title
-----

Change title for the page. The title is used as metadata for the site and shows up in the browser in tabs and bookmark names.

*Example:*

::

    {% block title %}{{ block.super }} - My Sub Title{% endblock %}

links
-----

Add content before the stylesheets such as rss feeds and favicons. Use ``block.super`` to preserve the default favicon or override completely to specify custom favicon.

*Example:*

::

    {% block links %}
      <link rel="shortcut icon" href="/path/to/favicon.ico" />
    {% endblock %}

styles
------

Add additional stylesheets to the page. Use ``block.super`` to preserve the existing styles for the app (recommended) or override completely to use your own custom stylesheets.

*Example:*

::

    {% block styles %}
      {{ block.super }}
      <link href="/path/to/styles.css" rel="stylesheet" />
    {% endblock %}

global_scripts
--------------

Add JavaScript libraries that need to be loaded prior to the page being loaded. This is a good block to use for libraries that are referenced globally. The global libraries included as global scripts by default are JQuery and Bootstrap. Use ``block.super`` to preserve the default global libraries.

*Example:*

::

    {% block global_scripts %}
      {{ block.super }}
      <script src="/path/to/script.js" type="text/javascript"></script>
    {% endblock %}

bodytag
-------

Add attributes to the ``body`` element.

*Example:*

::

    {% block bodytag %}class="a-class" onload="run_this();"{% endblock %}

app_content_wrapper_override
----------------------------

Override the app content structure completely. The app content wrapper contains all content in the ``<body>`` element other than the scripts. Use this block to override all of the app template structure completely.

*Override Eliminates:*

app_header_override, app_navigation_toggle_override, app_icon_override, app_icon, app_title_override, app_title, exit_button_override, app_content_override, flash, app_navigation_override, app_navigation, app_navigation_items, app_content, app_actions_override, app_actions.

*Example:*

::

    {% block app_content_wrapper_override %}
      <div>
        <p>My custom content</p>
      </div>
    {% endblock %}

app_header_override
-------------------

Override the app header completely including any wrapping elements. Useful for creating a custom header for your app.

*Override Eliminates:*

app_navigation_toggle_override, app_icon_override, app_icon, app_title_override, app_title, exit_button_override

app_navigation_toggle_override
------------------------------

Override the app navigation toggle button. This is useful if you want to create an app that does not include the navigation pane. Use this to remove the navigation toggle button as well.

*Example:*

::

    {% block app_navigation_toggle_override %}{% endblock %}

app_icon_override
-----------------

Override the app icon in the header completely including any wrapping elements.

*Override Eliminates:*

app_icon


app_icon
--------

Override the app icon ``<img>`` element in the header.

*Example:*

::

    {% block app_icon %}<img src="/path/to/icon.png">{% endblock %}

app_title_override
------------------

Override the app title in the header completely including any wrapping elements.

*Override Eliminates:*

app_title

app_title
---------

Override the app title element in the header.

*Example:*

::

    {% block app_title %}My App Title{% endblock %}

exit_button_override
--------------------

Override the exit button completely including any wrapping elements.

app_content_override
--------------------

Override only the app content area while preserving the header. The navigation and actions areas will also be overridden.

*Override Eliminates:*

flash, app_navigation_override, app_navigation, app_navigation_items, app_content, app_actions_override, app_actions

flash
-----

Override the flash messaging capabilities. Flash messages are used to display dismissible messages to the user using the Django messaging capabilities. Override if you would like to implement your own messaging system or eliminate functionality all together.

app_navigation_override
-----------------------

Override the app navigation elements including any wrapping elements.

*Override Eliminates:*

app_navigation, app_navigation_items

app_navigation
--------------

Override the app navigation container. The default container for navigation is an unordered list. Use this block to override the unordered list for custom navigation.

*Override Eliminates:*

app_navigation_items

app_navigation_items
--------------------

Override or append to the app navigation list. These should be ``<li>`` elements.

app_content
-----------

Add content to the app content area. This should be the primary block used to add content to the app.

*Example:*

::

    {% block app_content %}
      <p>Content for my app.</p>
    {% endblock %}

app_actions_override
--------------------

Override app content elements including any wrapping elements.

app_actions
-----------

Override or append actions to the action area. These are typically buttons or links. The actions are floated right, so they need to be listed in right to left order.

*Example:*

::

    {% block app_actions %}
      <a href="" class="btn btn-default">Next</a>
      <a href="" class="btn btn-default">Back</a>
    {% endblock %}

scripts
-------

Add additional JavaScripts to the page. Use ``block.super`` to preserve the existing scripts for the app (recommended) or override completely to use your own custom scripts.

*Example:*

::

    {% block scripts %}
      {{ block.super }}
      <script href="/path/to/script.js" type="text/javascript"></script>
    {% endblock %}

app_base.html
=============

This section provides the complete contents of the :file:`app_base.html` template, so app developers can be aware of the template structure underlying their app templates.

::

    {% load staticfiles tethys_gizmos %}
    <!DOCTYPE html>

    {% block htmltag %}
    <!--[if IE 7]> <html lang="en" class="ie ie7"> <![endif]-->
    <!--[if IE 8]> <html lang="en"  class="ie ie8"> <![endif]-->
    <!--[if IE 9]> <html lang="en"  class="ie9"> <![endif]-->
    <!--[if gt IE 8]><!--> <html lang="en" > <!--<![endif]-->
    {% endblock %}

      <head {% block headtag %}{% endblock %}>

        {% block meta %}
          <meta charset="utf-8" />
          <meta http-equiv="X-UA-Compatible" content="IE=edge">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <meta name="generator" content="Django" />
        {% endblock %}

        <title>
          {% if site_globals.site_title %}
             {{ site_globals.site_title }}
          {% elif site_globals.brand_text %}
            {{ site_globals.brand_text }}
          {% else %}
            Tethys
          {% endif %}
          {% block title %}{% endblock %}
        </title>

        {% block links %}
          {% if site_globals.favicon %}
            <link rel="shortcut icon" href="{{ site_globals.favicon }}" />
          {% endif %}
        {% endblock %}

        {% block styles %}
          <link href="//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css" rel="stylesheet" />
          <link href="{% static 'tethys_apps/css/app_base.css' %}" rel="stylesheet" />
        {% endblock %}

        {% block global_scripts %}
          <script src="//code.jquery.com/jquery-2.1.1.min.js" type="text/javascript"></script>
          <script src="//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js" type="text/javascript"></script>
        {% endblock %}

      </head>

      <body {% block bodytag %}{% endblock %}>

        {% block app_content_wrapper_override %}
          <div id="app-content-wrapper" class="show-nav">

            {% block app_header_override %}
              <div id="app-header" class="clearfix">
                <div class="tethys-app-header" style="background: {{ tethys_app.color|default:'#1b95dc' }};">

                  {% block app-navigation-toggle-override %}
                    <a href="javascript:void(0);" class="toggle-nav">
                      <div></div>
                      <div></div>
                      <div></div>
                    </a>
                  {% endblock %}

                  {% block app_icon_override %}
                    <div class="icon-wrapper">
                      {% block app_icon %}<img src="{% static tethys_app.icon %}">{% endblock %}
                    </div>
                  {% endblock %}

                  {% block app_title_override %}
                    <div class="app-title-wrapper">
                      <span class="app-title">{% block app_title %}{{ tethys_app.name }}{% endblock %}</span>
                    </div>
                  {% endblock %}

                  {% block exit_button_override %}
                    <div class="exit-button">
                      <a href="javascript:void(0);" onclick="TETHYS_APP_BASE.exit_app('{% url 'app_library' %}');">Exit</a>
                    </div>
                  {% endblock %}
                </div>
              </div>
            {% endblock %}

            {% block app_content_override %}
              <div id="app-content">

                {% block flash %}
                  {% if messages %}
                    <div class="flash-messages">

                      {% for message in messages %}
                        <div class="alert {% if message.tags %}{{ message.tags }}{% endif %} alert-dismissible" role="alert">
                          <button type="button" class="close" data-dismiss="alert">
                            <span aria-hidden="true">&times;</span>
                            <span class="sr-only">Close</span>
                          </button>
                          {{ message }}
                        </div>
                      {% endfor %}
                    </div>
                  {% endif %}
                {% endblock %}

                {% block app_navigation_override %}
                  <div id="app-navigation">
                    {% block app_navigation %}
                      <ul class="nav nav-pills nav-stacked">
                        {% block app_navigation_items %}{% endblock %}
                      </ul>
                    {% endblock %}
                  </div>
                {% endblock %}

                <div id="inner-app-content">
                  {% block app_content %}{% endblock %}

                  {# App actions are fixed to the bottom #}
                  {% block app_actions_override %}
                    <div id="app-actions">
                      {% block app_actions %}{% endblock %}
                    </div>
                  {% endblock %}
                </div>
              </div>
            {% endblock %}
          </div>
        {% endblock %}

        {% block scripts %}
          <script src="{% static 'tethys_apps/vendor/cookies.js' %}" type="text/javascript"></script>
          <script src="{% static 'tethys_apps/js/app_base.js' %}" type="text/javascript"></script>
          {% gizmo_dependencies %}
        {% endblock %}
      </body>
    </html>

base.html
=========

The :file:`base.html` is the base template that is used directly by app templates. This file is generated in all new Tethys app projects that are created using the scaffold.

::

    {% extends "tethys_apps/app_base.html" %}

    {% load staticfiles %}

    {% block title %}- {{ tethys_app.name }}{% endblock %}

    {% block styles %}
      {{ block.super }}
      <link href="{% static 'new_template_app/css/main.css' %}" rel="stylesheet"/>
    {% endblock %}

    {% block app_icon %}
      {# The path you provided in your app.py is accessible through the tethys_app.icon context variable #}
      <img src="{% static tethys_app.icon %}">
    {% endblock %}

    {# The name you provided in your app.py is accessible through the tethys_app.name context variable #}
    {% block app_title %}{{ tethys_app.name }}{% endblock %}

    {% block app_navigation_items %}
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
    {% endblock %}

    {% block app_content %}
    {% endblock %}

    {% block app_actions %}
    {% endblock %}

    {% block scripts %}
      {{ block.super }}
      <script src="{% static 'new_template_app/js/main.js' %}" type="text/javascript"></script>
    {% endblock %}