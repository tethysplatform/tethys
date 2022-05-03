*******************************
Static Resources (Experimental)
*******************************

**Last Updated:** May 2022

The Tethys SDK includes many static resources (CSS and JavaScript) that can be used in apps to apply common styling effects or functionality. This document provides a short description of each of these resources.

CSS
===

Use the CSS resources to apply different styles to your app or provide additional functionality.

Usage
-----

Include any of the CSS files using a ``<link>`` tag in your HTML template like so:

.. code-block:: html+django

    {% load static %}

    {% block styles %}
       {{ block.super }}
        <link href="{% static 'tethys_sdk/css/flat_nav.css' %}" rel="stylesheet">
    {% endblock %}




JavaScript
==========

Usage
-----

Include any of the JavaScript files using a ``<script>`` tag in your HTML template like so:

.. code-block:: html+django

    {% load static %}

    {% block global_scripts %}
       {{ block.super }}
        <script src="{% static 'tethys_sdk/js/csrf.js' %}" type="text/javascript"></script>
    {% endblock %}

.. note::

    The ``global_scripts`` tag is ideal for libraries containing functions that are needed by other JavaScript modules. For JavaScript that executes on page load or manipulates page content it is recommended to place the ``<script>`` tag in the ``scripts`` block.

