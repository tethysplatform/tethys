**********************
Working with Form Data
**********************

**Last Updated:** May 27, 2013

Most apps will use HTML forms to recieve input from the user. In this part of the tutorial, you'll learn how to create forms in your template and process the data submitted through the form in your controller.

Create Template with a Form
===========================

An HTML form in the simplest form consists of a set of ``input`` element wrapped in a ``form`` element. Each ``input`` element must have a unique name attribute to be submitted. Several complex input elements are available through :term:`snippets`, but this tutorial, we will use a very simple form.

1. Create a new template called :file:`form.html` in your templates directory (:file:`~tethysdev/ckanapp-my_first_app/ckanapp/my_first_app/templates/my_first_app/form.html`). Copy and paste the following lines into :file:`form.html`:

::

    {% extends "my_first_app/app_base.html" %}

    {% block breadcrumb_content %}
      <li><a href="{% url_for 'apps' %}">Apps</a></li>
      <li><a href="/apps/my-first-app">My First App</a></li>
      <li class="active"><a href="#">Username Form</a></li>
    {% endblock %}

    {% block primary_content %}
      <div class="module">
        <div class="module-content">
          <h5>Please enter your name:</h5>
          <form method="post" class="form-horizontal">
            <input type="text" name="username-input">
            <input type="submit" name="username-submit">
          </form>
          {% if c.username %}
          <h1>Hello, {{ c.username }}!</h1>
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
                <p>Welcome to my new page!</p>
        </div>
      </div>
    {% endblock %}

2. Open :file:`index.py` in your app ``controllers`` package (:file:`~tethysdev/ckanapp-my_first_app/ckanapp/my_first_app/controllers/index.py`) and add the following method to your ``MyFirstAppController`` class:

::

    def form(self):
        # Tools
        t = p.toolkit
        c = t.c

        # Set default value for username
        c.username = ''

        # Evaluate form if submitted
        if 'username-submit' in t.request.params:
            c.username = t.request.params['username-input']

        return t.render('my_first_app/form.html')

The form data is made available in the form of a dictionary in the ``t.request.params`` object. The values of the fields in your form can be accessed by using the names of the input fields as keys in this dictionary (e.g.: ``t.request.params['input-name']. The ``t.request.params`` object aggregates data submitted through all request types. Alternatively, the data submitted using a POST request can be accessed using ``t.request.POST`` and the data submitted through GET request can be accessed using ``t.request.GET``.

3. Add this controller mapping to the ``registerControllers`` method of your :term:`app class` in your :file:`app configuration file` (:file:`app.py`):

::

    controllers.addController(name='my_first_app_action',
                              url='my-first-app/{action}',
                              controller='my_first_app.controllers.index:MyFirstAppController')

4. Navigate to: http://localhost:5000/apps/my-first-app/form . Enter your name in the text field and submit it. Your name is submitted via a POST request to your controller. The controller passes the name back to the template in the ``c.username`` template variable, resulting in a warm greeting to yourself.




