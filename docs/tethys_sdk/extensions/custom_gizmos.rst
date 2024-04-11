*************
Custom Gizmos
*************

**Last Updated:** February 22, 2018

Tethys Extensions can be used to create custom gizmos, which can then be used by any app in portals where the extension is installed. This document will provide a brief overview of how to create a gizmo.

Anatomy of a Gizmo
------------------

Gizmos are essentially mini-templates that can be embedded in other templates using the ``gizmo`` tag. They are composed of three primary components:

    #. Gizmo Options Class
    #. Gizmo Template
    #. JavaScript and CSS Dependencies

Each component will be briefly introduced. To illustrate, we will show how a simplified version of the ``SelectInput`` gizmo could be implemented as a custom Gizmo in an extension.

Gizmo Organization
------------------

The files used to define custom gizmos must be organized in a specific way in your app extension. Each gizmo options class must be located in its own python module and the file should be located in the ``gizmos`` package of your extension. The template for the gizmo must an HTML file located within the ``templates/gizmos/`` folder of your extension.

Gizmo files must follow a specific naming convention: the python module containing the gizmo options class and the name of the gizmo template must have the same name as the gizmo. For example, if the name of the gizmo you are creating is ``custom_select_input`` then the name of the gizmo template would be ``custom_select_input.html`` and the name of the gizmo options module would be ``custom_select_input.py``.

JavaScript and CSS dependencies should be stored in the ``public`` directory of your extension as usual or be publicly available from a CDN or similar. Dependencies stored locally can be organized however you prefer within the ``public`` directory.

Finally, you must import the gizmo options class in the ``gizmos/__init__.py`` module. Only Gizmos imported here will be accessible. For the custom select input example, the file structure would look something like this:

::

    tethysext-my_first_extension/
    |-- tethysext/
    |   |-- my_first_extension/
    |   |   |-- gizmos/
    |   |   |   |-- custom_select_input.py
    |   |   |-- public/
    |   |   |   |-- gizmos/
    |   |   |   |   |-- custom_select_input/
    |   |   |   |   |   |-- custom_select_input.css
    |   |   |   |   |   |-- custom_select_input.js
    |   |   |-- templates/
    |   |   |   |-- gizmos/
    |   |   |   |   |-- custom_select_input.html

.. important::

    Gizmo names must be globally unique within a portal. If a portal has two extensions that implement gizmos with the same name, they will conflict and likely not work properly.


Gizmo Options Class
-------------------

A gizmo options class is a class that inherits from the ``TethysGizmoOptions`` base class. It can be thought of as the context for the gizmo template. Any property or attribute of the gizmo options class will be available as a variable in the Gizmo Template.

For the custom select input gizmo, create a new python module in the ``gizmos`` package called ``custom_select_input.py`` and add the following contents:

::

    from tethys_sdk.gizmos import TethysGizmoOptions


    class CustomSelectInput(TethysGizmoOptions):
        """
        Custom select input gizmo.
        """
        gizmo_name = 'custom_select_input'

        def __init__(self, name, display_text='', options=(), initial=(), multiselect=False,
                     disabled=False, error='', **kwargs):
            """
            constructor
            """
            # Initialize parent
            super().__init__(**kwargs)

            # Initialize Attributes
            self.name = name
            self.display_text = display_text
            self.options = options
            self.initial = initial
            self.multiselect = multiselect
            self.disabled = disabled
            self.error = error

It is important that ``gizmo_name`` property is the same as the name of the python module and template for the gizmo. Also, it is important to include ``**kwargs`` as an argument to your contstructor and use it to initialize the parent ``TethysGizmoOptions`` object. This will catch any of the parameters that are common to all gizmos like ``attributes`` and ``classes``.

After defining the gizmo options class, import it in the ``gizmos/__init__.py`` module:

::

    from custom_select_input import CustomSelectInput


Gizmo Template
--------------

Gizmo templates are similar to the templates used for Tethys apps, but much simpler.

For the custom select input gizmo, create a new template in the ``templates/gizmos/`` directory with the same name as your gizmo, ``custom_select_input.html``, with the following contents:

.. code-block:: django

    {% load static %}

    <div class="form-group {% if error %} has-error {% endif %}">
      {% if display_text %}
        <label class="control-label" for="{{ name }}">{{ display_text }}</label>
      {% endif %}
      <select id="{{ name }}"
              name="{{ name }}"
              class="select2{% if classes %} {{ classes }}{% endif %}"
              {% if attributes %}
                {% for key, value in attributes.items %}
                  {{ key }}="{{ value }}"
                {% endfor %}
              {% endif %}
              {% if multiselect %}multiple{% endif %}
              {% if disabled %}disabled{% endif %}>
        {% for option, value in options %}
          {% if option in initial or value in initial %}
            <option value="{{value}}" selected="selected">{{ option }}</option>
          {% else %}
            <option value="{{value}}">{{ option }}</option>
          {% endif %}
        {% endfor %}
      </select>
      {% if error %}
      <p class="help-block">{{ error }}</p>
      {% endif %}
    </div>

The variables in this template are defined by the attributes of the gizmo options object. Notice how the ``classes`` and ``attributes`` variables are handled. It is a good idea to handle these variables for each of your gizmos, because most gizmos support them and developers will expect them.


JavaScript and CSS Dependencies
-------------------------------

Some gizmos have JavaScript and/or CSS dependencies. The ``TethysGizmoOptions`` base class provides methods for specifying different types of dependencies:

* ``get_vendor_js``: For vendor/3rd party javascript.
* ``get_vendor_css``: For vendor/3rd party css.
* ``get_gizmo_js``: For your custom javascript.
* ``get_gizmo_css``: For your custom css.
* ``get_tethys_gizmos_js``: For global gizmo javascript. Changing this could cause other gizmos to stop working. Best not to mess with it unless you know what you are doing.
* ``get_tethys_gizmos_css``: For global gizmo css. Changing this could cause other gizmos to stop working. Best not to mess with it unless you know what you are doing.

.. note::
    Tethys provides ``Twitter Bootstrap`` and ``jQuery``, so you don't need to include these as gizmo dependencies.

The custom select input depends on the select2 libraries and some custom javascript and css. Create ``custom_select_input.js`` and ``custom_select_input.css`` in the ``public/gizmos/custom_select_input/`` directory, creating the directory as well. Add the following contents to each file:

Add this content to the ``custom_select_input.css`` file:

.. code-block:: css

    .select2 {
        width: 100%;
    }

Add this content to the ``custom_select_input.js`` file:

.. code-block:: javascript

    $(document).ready(function() {
        $('.select2').select2();
    });


Modify the gizmo options class to include these dependencies:

::

    from tethys_sdk.gizmos import TethysGizmoOptions


    class CustomSelectInput(TethysGizmoOptions):
        """
        Custom select input gizmo.
        """
        gizmo_name = 'custom_select_input'

        def __init__(self, name, display_text='', options=(), initial=(), multiselect=False,
                     disabled=False, error='', **kwargs):
            """
            constructor
            """
            # Initialize parent
            super().__init__(**kwargs)

            # Initialize Attributes
            self.name = name
            self.display_text = display_text
            self.options = options
            self.initial = initial
            self.multiselect = multiselect
            self.disabled = disabled
            self.error = error

        @staticmethod
        def get_vendor_js():
            """
            JavaScript vendor libraries.
            """
            return ('https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.6-rc.0/js/select2.min.js',)

        @staticmethod
        def get_vendor_css():
            """
            CSS vendor libraries.
            """
            return ('https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.6-rc.0/css/select2.min.css',)

        @staticmethod
        def get_gizmo_js():
            """
            JavaScript specific to gizmo.
            """
            return ('my_first_extension/gizmos/custom_select_input/custom_select_input.js',)

        @staticmethod
        def get_gizmo_css():
            """
            CSS specific to gizmo .
            """
            return ('my_first_extension/gizmos/custom_select_input/custom_select_input.css',)

Using a Custom Gizmo
--------------------

To use a custom gizmo in an app, import the gizmo options object from the extension and create a new instance fo the gizmo in the app controller. Then use it with the ``gizmo`` template tag as normal.


Import and create a new instance of the gizmo in your controller:

::

    from tethysext.my_first_extension.gizmos import CustomSelectInput
    from .app import App


    def my_app_controller(request):
        """
        Example controller using extension gizmo
        """
        my_select = CustomSelectInput(
            name = 'my_select',
            display_text = 'Select One:',
            options = (('Option 1', '1'), ('Option 2', '2'), ('Option 3', '3')),
            initial = ('2')
        )

        context = {
            'my_select': my_select,
        }
        return App.render(request, 'a_template.html', context)

Then use the gizmo as usual in ``a_template.html``:

.. code-block::django

    {% load tethys %}

    {% gizmo my_select %}

