.. _templating_api:

******************
App Templating API
******************

**Last Updated:** May 2017

The pages of a Tethys app are created using the Django template language. This provides an overview of important Django templating concepts and introduces the base templates that are provided to make templating easier.

Django Templating Concepts
==========================

The Django template language allows you to create dynamic HTML templates and minmizes the amount of HTML you need to write for your app pages. This section will provide a crash course in Django template language basics, but we highly recommend a review of the `Django Template Language <https://docs.djangoproject.com/en/2.2/topics/templates/>`_ documentation.

.. tip::

    Review the `Django Template Language <https://docs.djangoproject.com/en/2.2/topics/templates/>`_ to get a better grasp on templating in Tethys.

Variables
---------

In Django templates, variables are denoted by double curly brace syntax: ``{{ variable }}``. The variable expression will be replaced by the value of the variable. Dot notation can be used access attributes of a variable: ``{{ variable.attribute }}``.

Examples:

.. code-block:: html+django

  # Examples of Django template variable syntax
  {{ variable }}

  # Access items in a list or tuple using dot notation
  {{ list.0 }}

  # Access items in a dictionary using dot notation
  {{ dict.key }}

  # Access attributes of objects using dot notation
  {{ object.attribute }}

.. hint::

    See `Django template Variables <https://docs.djangoproject.com/en/2.2/topics/templates/#variables>`_ documentation for more information.

Filters
-------

Variables can be modified by filters which look like this: ``{{ variable|filter:argument }}``. Filters perform modifying functions on variable output such as formatting dates, formatting numbers, changing the letter case, and concatenating multiple variables.

Examples:

.. code-block:: html+django

    # The default filter can be used to print a default value when the variable is falsy
    {{ variable|default:"nothing" }}

    # The join filter can be used to join a list with a the separator given
    {{ list|join:", " }}

.. hint::

    Refer to the `Django Filter Reference <https://docs.djangoproject.com/en/2.2/ref/templates/builtins/#ref-templates-builtins-filters>`_ for a full list of the filters available.

Tags
----

Tags use curly brace percent sign syntax like this: ``{% tag %}``. Tags perform many different functions including creating text, controlling flow, or loading external information to be used in the app. Some commonly used tags include ``for``, ``if``, ``block``, and ``extends``.

Examples:

.. code-block:: html+django

    # The if tag only prints its contents when the condition evaluates to True
    {% if name %}
        <h1>Hello, {{ name }}!</h1>
    {% else %}
        <h1>Welcome!</h1>
    {% endif %}

    #  The for tag can be used to loop through iterables printing its contents on each iteration
    <ul>
      {% for item in item_list %}
        <li>{{ item }}</li>
      {% endfor %}
    </ul>

    # The block tag is used to override the contents of the block of a parent template
    {% block example %}
      <p>I just overrode the contents of the "example" block with this paragraph.</p>
    {% endblock %}

.. hint::

    See the `Django Tag Reference <https://docs.djangoproject.com/en/2.2/ref/templates/builtins/#ref-templates-builtins-tags>`_ for a complete list of tags that Django provides.

Tethys Filters
++++++++++++++

In addition to Django's library of template filters, Tethys also defines several additional template filters that can be used in your templates.

.. note::

    To load the Tethys template filters you will need to add a include ``tethys`` in the ``load`` tag:

    .. code-block:: html+django

        {% load tethys %}

.. automodule:: tethys_apps.templatetags.tags
   :members: url, public

.. automodule:: tethys_apps.templatetags.humanize
   :members: human_duration

.. automodule:: tethys_apps.templatetags.app_theme
   :members: lighten

Template Inheritance
--------------------

One of the advantages of using the Django template language is that it provides a method for child templates to extend parent templates, which can reduce the amount of HTML you need to write. Template inheritance is accomplished using two tags, ``extends`` and ``block``. Parent templates provide ``blocks`` of content that can be overridden by child templates. Child templates can extend parent templates by using the ``extends`` tag. Calling the ``block`` tag of a parent template in a child template will override any content in that ``block`` tag with the content in the child template.

.. hint::

    The `Django Template Inheritance <https://docs.djangoproject.com/en/5.1/ref/templates/language/#template-inheritance>`_ documentation provides an excellent example that illustrates how inheritance works.


Base Templates
==============

There are two layers of templates provided for Tethys app development. The :file:`app_base.html` or any of its derivatives (See :ref:`additional_base_templates`) from which all Tethys apps inherit, and the :file:`base.html` at the app level from which all pages in an app project can inherit.

The :file:`app_base.html` template provides the HTML skeleton for all Tethys app templates, which includes the base HTML structural elements (e.g.: ``<html>``, ``<head>``, and ``<body>`` elements), the base style sheets and JavaScript libraries, and many blocks for customization.

All Tethys app projects also include a :file:`base.html` template that inherits from the :file:`app_base.html` template.

App developers are encouraged to use the :file:`base.html` file as the base template for all of their templates within an app, rather than extending the :file:`app_base.html` file directly. The :file:`base.html` template is easier to work with, because it includes only the blocks that will be used most often from the :file:`app_base.html` template or its derivatives (See :ref:`additional_base_templates`). However, all of the blocks that are available from :file:`app_base.html` template or its selected derivative template will also be available for use in the :file:`base.html` template and any templates that extend it.

Many of the blocks in the template correspond with different portions of the app interface. Figure 1 provides a graphical explanation of these blocks. An explanation of all the blocks provided in the :file:`app_base.html` and :file:`base.html` templates can be found in the section that follows.

.. figure:: ../images/detailed_template_blocks.png
    :width: 700px

    **Figure 1.** Illustration of the blocks that correspond with app interface elements as follows:

    1. app_header_override
    2. app_navigation_toggle_override
    3. app_icon_override, app_icon
    4. app_title_override, app_title
    5. exit_button_override
    6. app_content_override
    7. app_navigation_override
    8. app_navigation, app_navigation_items
    9. flash
    10. app_content
    11. app_actions_override
    12. app_actions


Blocks
======

This section provides an explanation of the blocks are available for use in child templates of either the :file:`app_base.html` or the :file:`base.html` templates.

htmltag
-------

Override the ``<html>`` element open tag.

*Example:*

.. code-block:: html+django

    {% block htmltag %}<html lang="es">{% endblock %}

headtag
-------

Add attributes to the ``<head>`` element.

*Example:*

.. code-block:: html+django

    {% block headtag %}style="display: block;"{% endblock %}

meta
----

Override or append ``<meta>`` elements to the ``<head>`` element. To append to existing elements, use ``block.super``.

*Example:*

.. code-block:: html+django

    {% block meta %}
      {{ block.super }}
      <meta name="description" value="My website description" />
    {% endblock %}

title
-----

Change title for the page. The title is used as metadata for the site and shows up in the browser in tabs and bookmark names.

*Example:*

.. code-block:: html+django

    {% block title %}My Sub Title{% endblock %}

links
-----

Add content before the stylesheets such as rss feeds and favicons. Use ``block.super`` to preserve the default favicon or override completely to specify custom favicon.

*Example:*

.. code-block:: html+django

    {% block links %}
      <link rel="shortcut icon" href="/path/to/favicon.ico" />
    {% endblock %}

import_gizmos
-------------

The import_gizmos block allows you register gizmos to be added to your page so that the dependencies load properly.

*Example:*

.. code-block:: html+django

    {% block import_gizmos %}
      {% import_gizmo_dependency map_view %}
    {% endblock %}

styles
------

Add additional stylesheets to the page. Use ``block.super`` to preserve the existing styles for the app (recommended) or override completely to use your own custom stylesheets.

*Example:*

.. code-block:: html+django

    {% block styles %}
      {{ block.super }}
      <link href="/path/to/styles.css" rel="stylesheet" />
    {% endblock %}

global_scripts
--------------

Add JavaScript libraries that need to be loaded prior to the page being loaded. This is a good block to use for libraries that are referenced globally. The global libraries included as global scripts by default are JQuery and Bootstrap. Use ``block.super`` to preserve the default global libraries.

*Example:*

.. code-block:: html+django

    {% block global_scripts %}
      {{ block.super }}
      <script src="/path/to/script.js" type="text/javascript"></script>
    {% endblock %}

bodytag
-------

Add attributes to the ``body`` element.

*Example:*

.. code-block:: html+django

    {% block bodytag %}class="a-class" onload="run_this();"{% endblock %}

app_content_wrapper_override
----------------------------

Override the app content structure completely. The app content wrapper contains all content in the ``<body>`` element other than the scripts. Use this block to override all of the app template structure completely.

*Override Eliminates:*

app_header_override, app_navigation_toggle_override, app_icon_override, app_icon, app_title_override, app_title, exit_button_override, app_content_override, flash, app_navigation_override, app_navigation, app_navigation_items, app_content, app_actions_override, app_actions.

*Example:*

.. code-block:: html+django

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

.. code-block:: html+django

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

.. code-block:: html+django

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

.. code-block:: html+django

    {% block app_title %}My App Title{% endblock %}

header_buttons_override
-----------------------

Override all the header buttons on the right-hand side of the header (settings button, exit button, and header buttons).

header_buttons
--------------

Use this block to add custom buttons to the app header. Use an anchor/link tag for the button and wrap it in a ``div`` with the class ``header-button``. For buttons with the Bootstrap icons, add the ``glyphicon-button`` class to the wrapper element as well.

*Example:*

.. code-block:: html+django

    {% block header_buttons %}
      <div class="header-button glyphicon-button">
        <a href="{% url tethys_app|url:'another_page' %}"><i class="bi bi-boombox"></i></a>
      </div>
    {% endblock %}

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

Override or append to the app navigation list. These should be ``<li>`` elements according to the `Boostrap Vertical Nav <https://getbootstrap.com/docs/5.2/components/navs-tabs/#vertical>`_ structure. In addition, Tethys Platform provides the ``title`` and ``separator`` classes that can be used to split the navigation items into sections.

Example:

.. code-block:: html+django

    {% block app_navigation_items %}
      <li class="nav-item title">App Navigation</li>
      <li class="nav-item"><a class="nav-link active" href="">Home</a></li>
      <li class="nav-item"><a class="nav-link" href="">Jobs</a></li>
      <li class="nav-item separator"></li>
      <li class="nav-item"><a class="nav-link" href="">Get Started</a></li>
    {% endblock %}

app_content
-----------

Add content to the app content area. This should be the primary block used to add content to the app.

*Example:*

.. code-block:: html+django

    {% block app_content %}
      <p>Content for my app.</p>
    {% endblock %}

after_app_content
-----------------

Use this block for adding elements after the app content such as Bootstrap modals (Bootstrap modals will not work properly if they are placed in the main ``app_content`` block).

*Example:*

.. code-block:: html+django

    {% block after_app_content %}
      {% gizmo my_modal %}
    {% endblock %}

app_actions_override
--------------------

Override app content elements including any wrapping elements.

app_actions
-----------

Override or append actions to the action area. These are typically buttons or links. The actions are floated right, so they need to be listed in right to left order.

*Example:*

.. code-block:: html+django

    {% block app_actions %}
      <a href="" class="btn btn-secondary">Next</a>
      <a href="" class="btn btn-secondary">Back</a>
    {% endblock %}

scripts
-------

Add additional JavaScripts to the page. Use ``block.super`` to preserve the existing scripts for the app (recommended) or override completely to use your own custom scripts.

*Example:*

.. code-block:: html+django

    {% block scripts %}
      {{ block.super }}
      <script href="/path/to/script.js" type="text/javascript"></script>
    {% endblock %}

base.html
=========

The :file:`base.html` is the base template that is used directly by app templates. This file is generated in all new Tethys app projects that are created using the scaffold. The contents are provided here for reference.

All of the blocks provided by the :file:`base.html` template are inherited from the :file:`app_base.html` template. The :file:`base.html` template is intended to be a simplified version of the :file:`app_base.html` template, providing only the the blocks that should be used in a default app configuration. However, the blocks that are excluded from the :file:`base.html` template can be used by advanced Tethys app developers who wish customize parts or all of the app template structure.

See the `Blocks`_ section for an explanation of each block.

.. code-block:: html+django

    {% extends "tethys_apps/app_base.html" %}

    {% load static %}

    {% block title %}{{ tethys_app.name }}{% endblock %}

    {% block app_icon %}
      {# The path you provided in your app.py is accessible through the tethys_app.icon context variable #}
      <img src="{% if 'http' in tethys_app.icon %}{{ tethys_app.icon }}{% else %}{% static tethys_app.icon %}{% endif %}" />
    {% endblock %}

    {# The name you provided in your app.py is accessible through the tethys_app.name context variable #}
    {% block app_title %}{{ tethys_app.name }}{% endblock %}

    {% block app_navigation_items %}
      <li class="nav-item title">App Navigation</li>
      <li class="nav-item"><a class="nav-link active" href="">Home</a></li>
      <li class="nav-item"><a class="nav-link" href="">Jobs</a></li>
      <li class="nav-item"><a class="nav-link" href="">Results</a></li>
      <li class="nav-item title">Steps</li>
      <li class="nav-item"><a class="nav-link" href="">1. The First Step</a></li>
      <li class="nav-item"><a class="nav-link" href="">2. The Second Step</a></li>
      <li class="nav-item"><a class="nav-link" href="">3. The Third Step</a></li>
      <li class="nav-item separator"></li>
      <li class="nav-item"><a class="nav-link" href="">Get Started</a></li>
    {% endblock %}

    {% block app_content %}
    {% endblock %}

    {% block app_actions %}
    {% endblock %}

    {% block content_dependent_styles %}
      {{ block.super }}
      <link href="{% static 'my_first_app/css/main.css' %}" rel="stylesheet"/>
    {% endblock %}

    {% block scripts %}
      {{ block.super }}
      <script src="{% static 'my_first_app/js/main.js' %}" type="text/javascript"></script>
    {% endblock %}

app_base.html
=============

This section provides the complete contents of the :file:`app_base.html` template. It is meant to be used as a reference for app developers, so they can be aware of the HTML structure underlying their app templates.

.. literalinclude:: ../../tethys_apps/templates/tethys_apps/app_base.html
    :language: html+django

.. _additional_base_templates:

Additional Base Templates
=========================

Additional templates that inherit from the :file:`app_base.html` template have been added to Tethys to facilitate app customization. These templates include:

app_content_only.html
---------------------

This template contains only the app content. Code referencing displays block other than the ``app_content`` block will have no effect on this template. ``Override``, ``JavaScript``, and ``Style`` blocks retain their regular behavior.

.. figure:: ../images/app_content_only.png
    :width: 700px

    **Figure 2.** Layout of the app_content_only.html file.

app_header_content.html
-----------------------

This template contains only the header and app content. Code referencing any display block other than the ``app_content`` block or blocks contained in the app header (``app_icon``, ``app_title``, or ``header_buttons``) will have no effect on this template. ``Override``, ``JavaScript``, and ``Style`` blocks retain their regular behavior.

.. figure:: ../images/app_header_content.png
    :width: 700px

    **Figure 3.** Layout of the app_header_content.html file.

app_no_nav.html
---------------

This template is the same as normal :file:`app_base.html`, but with the navigation menu strip out. Code referencing the ``app_navigation`` block will have no effect on this template. Other blocks retain their regular behavior.

.. figure:: ../images/app_no_nav.png
    :width: 700px

    **Figure 4.** Layout of the app_no_nav.html file.

app_no_actions.html
-------------------

This template is the same as normal :file:`app_base.html`, but with no app actions section. Code referencing the ``app_actions`` block will have no effect on this template. Other blocks retain their regular behavior.

.. figure:: ../images/app_no_actions.png
    :width: 700px

    **Figure 5.** Layout of the app_no_actions.html file.

app_left_actions.html
---------------------

This template is the same as :file:`app_header_content.html` with the actions bar on left.

.. figure:: ../images/app_left_actions.png
    :width: 700px

    **Figure 6.** Layout of the app_left_actions.html file.

app_right_actions.html
----------------------

This template is the same as :file:`app_header_content.html` with the actions bar on right.

.. figure:: ../images/app_right_actions.png
    :width: 700px

    **Figure 7.** Layout of the app_right_actions.html file.

app_quad_split.html
-------------------

This template is the same as :file:`app_header_content.html` but with a 2 x 2 Bootstrap Grid in the content area.

.. figure:: ../images/app_quad_split.png
    :width: 700px

    **Figure 8.** Layout of the app_quad_split.html file.

Instead of an ``app_content`` block, this app uses the following four blocks:

- **app_content_tl:** The app content that will be displayed in the top left section of the 2 x 2 grid.
- **app_content_tr:** The app content that will be displayed in the top right section of the 2 x 2 grid.
- **app_content_bl:** The app content that will be displayed in the bottom left section of the 2 x 2 grid.
- **app_content_br:** The app content that will be displayed in the bottom right section of the 2 x 2 grid.

*Example:*

.. code-block:: html+django

    {% block app_content_tl %}
      <p>Top left content for my app.</p>
    {% endblock %}
    {% block app_content_tr %}
      <p>Top right content for my app.</p>
    {% endblock %}
    {% block app_content_bl %}
      <p>Bottom left content for my app.</p>
    {% endblock %}
    {% block app_content_br %}
      <p>Bottom right content for my app.</p>
    {% endblock %}

app_three_columns.html
----------------------

This template is the same as :file:`app_header_content.html` but with a three-column Bootstrap Grid in the content area.

.. figure:: ../images/app_three_columns.png
    :width: 700px

    **Figure 9.** Layout of the app_three_columns.html file.

Instead of an ``app_content`` block, this app uses the following three blocks:

- **app_content_lc:** The app content that will be displayed in the left column of the three-column grid.
- **app_content_mc:** The app content that will be displayed in the middle column of the three-column grid.
- **app_content_rc:** The app content that will be displayed in the right column of the three-column grid.

*Example:*

.. code-block:: html+django

    {% block app_content_lc %}
      <p>Left column content for my app.</p>
    {% endblock %}
    {% block app_content_tr %}
      <p>Middle column content for my app.</p>
    {% endblock %}
    {% block app_content_bl %}
      <p>Right column content for my app.</p>
    {% endblock %}

app_two_columns.html
--------------------

This template is the same as :file:`app_header_content.html` but with a two-column Bootstrap Grid in the content area.

.. figure:: ../images/app_two_columns.png
    :width: 700px

    **Figure 10.** Layout of the app_two_columns.html file.

Instead of an ``app_content`` block, this app uses the following two blocks:

- **app_content_lc:** The app content that will be displayed in the left column of the two-column grid.
- **app_content_rc:** The app content that will be displayed in the right column of the two-column grid.

*Example:*

.. code-block:: html+django

    {% block app_content_lc %}
      <p>Left column content for my app.</p>
    {% endblock %}
    {% block app_content_bl %}
      <p>Right column content for my app.</p>
    {% endblock %}
