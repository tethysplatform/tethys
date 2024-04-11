*****************************
Experimental Static Resources
*****************************

**Last Updated:** May 2022

Starting in Tethys 4, the Tethys SDK includes experimental static resources (CSS and JavaScript) that can be used in apps. This document provides a short description of each of these resources.

.. caution::

     Some of these resources may be repurposed as Gizmos in the future or may go away entirely. Use at your own risk.

CSS
===

Use the CSS resources to apply different styles to your app or provide additional functionality.

flat_nav.css
------------

Use this stylesheet to apply a flat style to the navigation pane in Tethys Apps.

To use this stylesheet add the following to :file:`base.html` in the ``styles`` block:

.. code-block:: html+django

    {% load static %}

    {% block styles %}
       {{ block.super }}
        <link href="{% static 'tethys_sdk/css/flat_nav.css' %}" rel="stylesheet">
    {% endblock %}

Also, add these lines to your :file:`main.css` but replace ``<app_color>`` with the theme color of your app:

**main.css**

.. code-block:: css

    #app-content-wrapper #app-content #app-navigation .nav li.active a {
        color: <app_color>!important;
        box-shadow: inset 4px 0 0 <app_color>!important;
    }


flat_slider.css
---------------

Use this stylesheet to apply a flat style to range slider elements.

To use, add the following stylesheet to your HTML template in the ``styles`` block:

.. code-block:: html+django

    {% load static %}

    {% block styles %}
       {{ block.super }}
        <link href="{% static 'tethys_sdk/css/flat_slider.css' %}" rel="stylesheet">
    {% endblock %}

Then add the ``flat-slider`` slider class to any range inputs:

.. code-block:: html

    <input type="range" class="flat-slider" id="volume" name="volume" min="0" max="100" step="1">

flatmark.css
------------

Use this stylesheet to style checkboxes and radio controls with a flat style.

To use, add the following stylesheet to your HTML template in the ``styles`` block:

.. code-block:: html+django

    {% load static %}

    {% block styles %}
       {{ block.super }}
        <link href="{% static 'tethys_sdk/css/flatmark.css' %}" rel="stylesheet">
    {% endblock %}

To use, apply the ``flatmark``, ``checkmark``, and ``checkbox`` classes and the following HTML structure:

.. code-block:: html

    <label class="flatmark"><span>Item 1</span>
        <input type="checkbox" checked>
        <span class="checkmark checkbox"></span>
    </label>
    <label class="flatmark"><span>Item 2</span>
        <input type="checkbox">
        <span class="checkmark checkbox"></span>
    </label>

Radio controls can be built as follows:

.. code-block:: html

    <label class="flatmark"><span>Option 1</span>
        <input type="radio" checked name="radio-group-1">
        <span class="checkmark radio"></span>
    </label>
    <label class="radio"><span>Option 2</span>
        <input type="radio" name="radio-group-1">
        <span class="checkmark radio"></span>
    </label>

nav_header.css
--------------

Use this stylesheet to build out a header with title, subtitle, and back button in the navigation pane of Tethys apps.

To use, add the following stylesheet to your HTML template in the ``styles`` block:

.. code-block:: html+django

    {% load static %}

    {% block styles %}
       {{ block.super }}
        <link href="{% static 'tethys_sdk/css/nav_header.css' %}" rel="stylesheet">
    {% endblock %}

Then include the ``nav_header.html`` template in the ``app_navigation`` block as follows:

.. code-block:: html+django

    {% block app_navigation %}
        {% include 'tethys_layouts/components/nav_header.html' %}
        {{ block.super }}
    {% endblock %}

Finally, include the following context variables in the controller for the page:

.. code-block:: python

    from tethys_sdk.routing import controller
    from .app import App

    @controller
    def some_controller(request):
        context = {
            'nav_title': 'My Title',
            'nav_subtitle': 'My Subtitle',
            'back_url': App.reverse('some_url')
        }
        return App.render(request, 'some_template.html', context)

nav_tabs.css
------------

Use this stylesheet to style Bootstrap tabs that are placed in the navigation pane of Tethys apps properly.

To use, add the following stylesheet to your HTML template in the ``styles`` block:

.. code-block:: html+django

    {% load static %}

    {% block styles %}
       {{ block.super }}
        <link href="{% static 'tethys_sdk/css/nav_tabs.css' %}" rel="stylesheet">
    {% endblock %}

Then add Bootstrap tabs to the template in the ``app_navigation`` block as usual (see `Navs and tabs | Bootstrap <https://getbootstrap.com/docs/5.2/components/navs-tabs/#using-data-attributes>`_):

.. code-block:: html+django

    {% block app_navigation %}
        <!-- Nav tabs -->
        <ul class="nav nav-tabs" id="myTab" role="tablist">
          <li class="nav-item" role="presentation">
            <button class="nav-link active" id="home-tab" data-bs-toggle="tab" data-bs-target="#home" type="button" role="tab" aria-controls="home" aria-selected="true">Home</button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" id="profile-tab" data-bs-toggle="tab" data-bs-target="#profile" type="button" role="tab" aria-controls="profile" aria-selected="false">Profile</button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" id="messages-tab" data-bs-toggle="tab" data-bs-target="#messages" type="button" role="tab" aria-controls="messages" aria-selected="false">Messages</button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" id="settings-tab" data-bs-toggle="tab" data-bs-target="#settings" type="button" role="tab" aria-controls="settings" aria-selected="false">Settings</button>
          </li>
        </ul>

        <!-- Tab panes -->
        <div class="tab-content">
          <div class="tab-pane active" id="home" role="tabpanel" aria-labelledby="home-tab">...</div>
          <div class="tab-pane" id="profile" role="tabpanel" aria-labelledby="profile-tab">...</div>
          <div class="tab-pane" id="messages" role="tabpanel" aria-labelledby="messages-tab">...</div>
          <div class="tab-pane" id="settings" role="tabpanel" aria-labelledby="settings-tab">...</div>
        </div>
    {% endblock %}

wide_nav.css
------------

Use this stylesheet to make the app navigation wider than the default (400px to be exact).

To use this stylesheet add the following to :file:`base.html` in the ``styles`` block:

.. code-block:: html+django

    {% load static %}

    {% block styles %}
       {{ block.super }}
        <link href="{% static 'tethys_sdk/css/wide_nav.css' %}" rel="stylesheet">
    {% endblock %}

.. tip::

    Alternatively, you may use the :file:`wide_nav.css` as a guide for creating your own stylesheet with a custom width. Copy the file into your app and then replace all of the ``400px`` values with the desired width and the ``415px`` value with ``<your_width> + 15px``.

JavaScript
==========

check_ie.js
-----------

Use this script to check if the web browser is Internet Explorer and display a warning message in an alert box that indicates the app does not support Internet Explorer. The exact message displayed is: "This app does not support Internet Explorer. Please switch to another browser."

To use this script add the following to :file:`base.html` in the ``scripts`` block:

.. code-block:: html+django

    {% load static %}

    {% block scripts %}
       {{ block.super }}
       <script src="{% static 'tethys_sdk/js/check_ie.js' %}" type="text/javascript"></script>
    {% endblock %}

collapse.js
-----------

This script provides ``collapse_section()`` and ``expand_section()`` methods that can be used to collapse and expand aribtrary elements with smooth animation.

To use this script add the following to :file:`base.html` in the ``global_scripts`` block:

.. code-block:: html+django

    {% load static %}

    {% block global_scripts %}
       {{ block.super }}
       <script src="{% static 'tethys_sdk/js/collapse.js' %}" type="text/javascript"></script>
    {% endblock %}

Then call the functions in your JavaScript:

.. code-block:: javascript

    let element = $('#some-element-id');
    collapse_section(element);
    expand_section(element);

csrf.js
-------

This script provides a ``get_csrf_token()`` function that retrieves the value of the CSRF token generated by Django from the cookie that it is stored in.

To use this script add the following to :file:`base.html` in the ``global_scripts`` block:

.. code-block:: html+django

    {% load static %}

    {% block global_scripts %}
       {{ block.super }}
       <script src="{% static 'tethys_sdk/js/csrf.js' %}" type="text/javascript"></script>
    {% endblock %}

Then use the ``get_csrf_token()`` function in your JavaScript AJAX requests:

.. code-block:: javascript

    $.ajax({
        type: 'POST',
        url: '/apps/my-first-app/some-url',
        data: {some: 'data'},
        beforeSend: xhr => {
            xhr.setRequestHeader('X-CSRFToken',  get_csrf_token());
        }
    }).done(function(data) {
        // Do stuff with the result
    })

utilities.js
------------

This script provides several utility functions that can be used to simplify your JavaScript. The utility functions included are:

* ``contains(str, sub)``: Test if a substring (``sub``) is contained in a string (``str``). Returns a boolean.
* ``in_array(item, array)``: Test if given ``item`` is in the given ``array``. Returns a boolean.
* ``is_defined(variable)``: Safely test if given ``variable`` is defined. Retruns a boolean.
* ``to_title_case(str)``: Change case of given string to title case. Returns title case string.
* ``var_to_title_case(str)``: Replace underscores with spaces, then convert to title case (e.g.: ``"some_var_name"`` -> ``"Some Var Name"``. Returns title case string.
* ``compute_center(features)``: Compute the center of the given array of OpenLayers ``ol.Features`` or ``ol.geom.Geometry``. Suported geometries include ``Point``, ``LineString``, ``Polygon``, and ``MultiPolygon``. Returns an ``ol.geom.Point``. Requires OpenLayers to be loaded.
* ``copy_text_to_clipboard(text)``: Add given ``text`` to the clipboard.
* ``convert_utc_to_local(identifier)``: Convert UTC date times to local time. Specify CSS selector for ``identifier`` of the elements that have the datetimes as their ``innerText``. The ``innerText`` will be replaced with local time. If multiple elements selected, they will all be updated.
* ``format_output_time(date)``: Format the given ``Date`` object to ``MMM DD YYYY HH:MM AM/PM``.

To use this script add the following to :file:`base.html` in the ``global_scripts`` block:

.. code-block:: html+django

    {% load static %}

    {% block global_scripts %}
       {{ block.super }}
       <script src="{% static 'tethys_sdk/js/utilities.js' %}" type="text/javascript"></script>
    {% endblock %}

.. note::

    The ``global_scripts`` tag is ideal for libraries containing functions that are needed by other JavaScript modules. Place JavaScript that executes on page load or manipulates page content in the ``scripts`` block.

