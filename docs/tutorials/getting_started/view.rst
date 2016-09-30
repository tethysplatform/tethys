***********************
The View and Templating
***********************

**Last Updated:** September 29, 2016

In this section the View aspect of MVC will be introduced. The View consists of the representation or visualizations of your app's data and the user interface. Views for Tethys apps are constructed using the standard web programming tools: HTML, JavaScript, and CSS. Additionally, Tethys Platform provides the Django Python templating language allowing you to insert Python code into your HTML documents, similar to how PHP is used. The result is dynamic, reusable templates for the web pages of your app.

In this tutorial you will add a view to your app for displaying the stream gages that are in your database on a Google Map.

Templating
==========

The Django template language is a simple, but powerful templating language. This section will provide a crash course in Django template language basics, but we highly recommend a review of the `Django Template Language <https://docs.djangoproject.com/en/1.7/topics/templates/>`_ documentation.

Browse to the your templates directory located at :file:`my_first_app/templates/`. By convention, all the templates for your app are stored in a directory with the same name of your :term:`app package` inside the templates directory (e.g.: :file:`templates/my_first_app`). This will prevent potential conflicts with the templates of other apps. You will find two templates in this directory: :file:`base.html` and :file:`home.html`. Refer to these templates as the Django template concepts are introduced.

Variables, Filters, and Tags
----------------------------

Django templates can contain variables, filters, and tags. Variables are denoted by double curly brace syntax like this: ``{{ variable }}``. Template variables are replaced by the value of the variable. Dot notation can be used access attributes of a variable: ``{{ variable.attribute }}``.

Variables can be modified by filters which look like this: ``{{ variable|filter:argument }}``. Filters perform modifying functions on variable output such as formatting dates, formatting numbers, changing the letter case, and concatenating multiple variables.

Tags use curly-brace-percent-sign syntax like this: ``{% tag %}``. Tags perform many different functions including creating text, controlling flow, or loading external information to be used in the app. Some commonly used tags include ``for``, ``if``, ``block``, and ``extends``.

.. tip::

    For a better explanation of variables, filters and tags, see the :doc:`../../tethys_sdk/templating`.

Template Inheritance
--------------------

One of the advantages of using the Django template language is that it provides a way for child templates to extend parent templates, which reduces the amount of HTML you need to write. Template inheritance is accomplished using two tags: ``extends`` and ``block``. Parent templates provide ``blocks`` of content that can be overridden by child templates. Child templates can extend parent templates by using the ``extends`` tag and specifying the template they which to inherit from. Calling the ``block`` tag of a parent template in a child template will override any content in that ``block`` tag with the content in the child template.

.. tip::

    If you are unfamiliar with Django template inheritance, please review the `Django Template Inheritance <https://docs.djangoproject.com/en/1.7/topics/templates/#template-inheritance>`_ documentation before proceeding.

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
      <script src="{% static 'my_first_app/js/main.js' %}" type="text/javascript"></script>
    {% endblock %}

The :file:`base.html` template is intended to be used as the parent template for all your app templates via the ``extends`` tag. It contains several ``block`` tags that your app templates can override or extend. The ``block`` tags you will use most often are ``app_navigation_items``, ``app_content``, and, ``app_actions``. These blocks correspond with different parts of the app interface (shown in the figure below). As a rule, content that you would like to be present in all your templates should be included in the :file:`base.html` template and content that is specific to a certain template should be included in that template.

.. figure:: ../../images/template_blocks.png
    :width: 650px

The ``block`` tags of the :file:`base.html` template correspond with different parts of the interface: (1) ``app_navigation_items``, (2) ``app_content``, and (3) ``app_actions``.

.. tip::

    For an explanation of the blocks in the :file:`base.html` template see the :doc:`../../tethys_sdk/templating`.

Public Files and Resources
==========================

Most apps will use files and resources that are static--meaning they do not need to be preprocessed before being served like templates do. Examples of these files include images, CSS files, and JavaScript files. Tethys Platform will automatically register static files that are located in the :file:`public` directory of your app project. Use the ``static`` tag in templates to load the resource URLs. The :file:`base.html` template provides examples of how to use the ``static`` tag. See the Django documentation for the `static <https://docs.djangoproject.com/en/1.7/ref/contrib/staticfiles/#static>`_ tag for more details.

.. caution::

    Any file stored in the public directory will be accesible to anyone. Be careful not to expose sensitive information.

Make a New Template
===================

Now that you know the basics of templating, you will learn how to create new templates that extend the base template and use the ``block`` tags. Create a new template in your templates directory (:file:`my_first_app/templates/my_first_app/`) and name it :file:`map.html`. Open this file in a text editor and copy and paste the following code into it:

::

    {% extends "my_first_app/base.html" %}

    {% load tethys_gizmos %}

    {% block app_content %}
      <h1>Stream Gages</h1>
      {% gizmo map_view map_options %}
    {% endblock %}

    {% block app_actions %}
      <a href="{% url 'my_first_app:home' %}" class="btn btn-default">Back</a>
    {% endblock %}

The :file:`map.html` template that you created extends the :file:`base.html` template. It also overrides the ``app_content``, `app_actions``, and ``scripts`` blocks. An action called "Back" is added to the ``app_actions`` block. It uses a new tag, the ``url`` tag, to provide a link back to the home page of the app. The ``url`` tag will be discussed in more detail in the :doc:`url_mapping` tutorial.

The map is inserted into the ``app_content`` block using one of the Tethys Gizmos called ``map_view``. Gizmos are an easy way to insert common user interface elements in to your templates with minimal code. The map is configured via a dictionary called ``map_options``, which is defined in the controller. This will be discussed in the next tutorial. For more information on Gizmos, refer to the :doc:`../../tethys_sdk/gizmos` documentation.