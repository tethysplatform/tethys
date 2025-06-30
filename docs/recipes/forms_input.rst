.. _forms_input:

:orphan:

********************
Forms and Data Input
********************

HTML forms are the primary mechanism for obtaining input from users of your app.  You can add a form to an HTML page with 


.. code block:: HTML

    {% block app_content %}
    <h1>Add Dam</h1>
    <form id="add-dam-form" method="post">
        {% csrf_token %}
        {% gizmo name_input %}
        {% gizmo owner_input %}
        {% gizmo river_input %}
        {% gizmo date_built_input %}
    </form>
    {% endblock %}

.. note:: In this code block the form is being added to the main content area of the page.  Forms can be added anywhere you need them in your app by changing the template.
.. check with Nathan on this note.  Also add link to extending templates

