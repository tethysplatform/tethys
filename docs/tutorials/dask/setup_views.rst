***********
Setup Views
***********

**Last Updated:** August 2024

In this section, you will setup most of the views needed for this app. For a refresher on setting up url maps, controllers, and templates, see: :ref:`key_concepts_tutorial`.


1. Add Job Functions
====================

Create :file:`job_functions.py` and set its contents to the following:

    .. code-block:: python

        import time
        import dask


        def inc(x):
            time.sleep(3)
            return x + 1


        def double(x):
            time.sleep(3)
            return x + 2


        def add(x, y):
            time.sleep(10)
            return x + y


        def sum_up(x):
            time.sleep(5)
            return sum(x)


        def convert_to_dollar_sign(result):
            return '$' + str(result)

.. important::

    The :file:`job_functions.py` module contains all the functions that we will call using Dask. It is recommended that you follow the same pattern in your apps--splitting Dask functions into a separate file. Dask produces strange results when functions are defined in the same files as controllers or models.

.. note::

    The ``sleep`` calls in each function are to simulate functions that do real work and hence take time to run.


2. Setup Controllers
====================

Replacte the contents of :file:`controller.py` with the following:

    .. code-block:: python

        import random
        from tethys_sdk.routing import controller
        from django.http.response import HttpResponseRedirect
        from django.contrib import messages
        from tethys_sdk.gizmos import Button
        from tethys_sdk.gizmos import JobsTable
        from tethys_compute.models.dask.dask_job_exception import DaskJobException
        from .app import App

        # get job manager for the app
        job_manager = App.get_job_manager()


        @controller
        def home(request):
            """
            Controller for the app home page.
            """

            jobs_button = Button(
                display_text='Show All Jobs',
                name='dask_button',
                attributes={
                    'data-bs-toggle': 'tooltip',
                    'data-bs-placement': 'top',
                    'title': 'Show All Jobs'
                },
                href=App.reverse('jobs_table')
            )

            context = {
                'jobs_button': jobs_button
            }

            return App.render(request, 'home.html', context)


        @controller
        def jobs_table(request):
            # Use job manager to get all the jobs.
            jobs = job_manager.list_jobs(order_by='-id', filters=None)

            # Table View
            jobs_table_options = JobsTable(
                jobs=jobs,
                column_fields=('id', 'name', 'description', 'creation_time'),
                hover=True,
                striped=False,
                bordered=False,
                condensed=False,
                results_url=f'{App.package}:result',
                refresh_interval=1000,
                show_detailed_status=True,
            )

            home_button = Button(
                display_text='Home',
                name='home_button',
                attributes={
                    'data-bs-toggle': 'tooltip',
                    'data-bs-placement': 'top',
                    'title': 'Home'
                },
                href=App.reverse('home')
            )

            context = {'jobs_table': jobs_table_options, 'home_button': home_button}

            return App.render(request, 'jobs_table.html', context)


        @controller
        def result(request, job_id):
            # Use job manager to get the given job.
            job = job_manager.get_job(job_id=job_id)

            # Get result and name
            job_result = job.result
            name = job.name

            home_button = Button(
                display_text='Home',
                name='home_button',
                attributes={
                    'data-bs-toggle': 'tooltip',
                    'data-bs-placement': 'top',
                    'title': 'Home'
                },
                href=App.reverse('home')
            )

            jobs_button = Button(
                display_text='Show All Jobs',
                name='dask_button',
                attributes={
                    'data-bs-toggle': 'tooltip',
                    'data-bs-placement': 'top',
                    'title': 'Show All Jobs'
                },
                href=App.reverse('jobs_table')
            )

            context = {
                'result': job_result,
                'name': name,
                'home_button': home_button,
                'jobs_button': jobs_button
            }

            return App.render(request, 'results.html', context)


        @controller
        def error_message(request):
            messages.add_message(request, messages.ERROR, 'Invalid Scheduler!')
            return App.redirect(App.reverse('home'))



3. Set up HTML
==============

Remove the navigation menu from the app by using the ``app_no_nav.html`` base template. Replace the contents of :file:`templates/dask_tutorial/base.html` as follows:

    .. code-block:: html+django

        {% extends "tethys_apps/app_no_nav.html" %}

        {% load static tethys %}

        {% block title %}{{ tethys_app.name }}{% endblock %}

        {% block app_icon %}
        {# The path you provided in your app.py is accessible through the tethys_app.icon context variable #}
        <img src="{% if 'http' in tethys_app.icon %}{{ tethys_app.icon }}{% else %}{% static tethys_app.icon %}{% endif %}" />
        {% endblock %}

        {# The name you provided in your app.py is accessible through the tethys_app.name context variable #}
        {% block app_title %}{{ tethys_app.name }}{% endblock %}

        {% block app_content %}
        {% endblock %}

        {% block app_actions %}
        {% endblock %}

        {% block content_dependent_styles %}
        {{ block.super }}
        <link href="{% static tethys_app|public:'css/main.css' %}" rel="stylesheet"/>
        {% endblock %}

        {% block scripts %}
        {{ block.super }}
        <script src="{% static tethys_app|public:'js/main.js' %}" type="text/javascript"></script>
        {% endblock %}


Replace the contents of :file:`templates/dask_tutorial/home.html` with the following:

    .. code-block:: html+django

        {% extends tethys_app.package|add:"/base.html" %}
        {% load tethys %}

        {% block app_actions %}
        {% gizmo jobs_button %}
        {% endblock %}

Create :file:`templates/dask_tutorial/jobs_table.html` with the following contents:

    .. code-block:: html+django

        {% extends tethys_app.package|add:"/base.html" %}
        {% load static tethys %}

        {% block global_scripts %}
            {{ block.super }}
            {% gizmo_dependencies global_js %}
        {% endblock %}

        {% block styles %}
            {{ block.super }}
            {% gizmo_dependencies global_css %}
        <link rel="stylesheet" href="{% static 'tethys_gizmos/css/gizmo_showcase.css' %}" type="text/css" />
        <style>
            #content {
                padding-bottom: 50px;
            }
        </style>
        {% endblock %}

        {% block app_content %}
        <div class="gizmo-page-wrapper">
            <h2>Jobs Table</h2>
            {% gizmo jobs_table %}
        </div>
        {% endblock %}

        {% block app_actions %}
        {% gizmo home_button %}
        {% endblock %}

        {% block scripts %}
        {% gizmo_dependencies css %}
            {{ block.super }}
        {% gizmo_dependencies js %}
        {% endblock %}

Create :file:`templates/dask_tutorial/results.html` with the following contents:

    .. code-block:: html+django

        {% extends tethys_app.package|add:"/base.html" %}
        {% load static tethys %}

        {% block title %}- Gizmos - Map View{% endblock %}

        {% block global_scripts %}
            {{ block.super }}
            {% gizmo_dependencies global_js %}
        {% endblock %}

        {% block styles %}
            {{ block.super }}
            {% gizmo_dependencies global_css %}
        <link rel="stylesheet" href="{% static 'tethys_gizmos/css/gizmo_showcase.css' %}" type="text/css" />
        <style>
            #content {
                padding-bottom: 50px;
            }
        </style>
        {% endblock %}

        {% block app_content %}
        <li>The result of running <strong>{{ name }}</strong> job is : <strong>{{ result }}</strong></li>

        {% endblock %}

        {% block app_actions %}
        {% gizmo home_button %}
        {% gizmo jobs_button %}
        {% endblock %}

        {% block scripts %}
        {% gizmo_dependencies css %}
            {{ block.super }}
        {% gizmo_dependencies js %}
        {% endblock %}

Create :file:`templates/dask_tutorial/error.html` with the following contents:

    .. code-block:: html+django

        {% extends tethys_app.package|add:"/base.html" %}
        {% load tethys %}

        {% block app_content %}
        <div class="error-message">
            {{ error_message }}
        </div>
        {% endblock %}

        {% block app_actions %}
        {% gizmo jobs_button %}
        {% endblock %}

4. Change App icon
==================

Download :download:`Dask Logo <./resources/dask-logo.png>` and save it to :file:`public/images`.

Update the ``icon`` property of the :term:`app class` in :file:`app.py` to use the dask logo as the app icon:

    .. code-block:: python
        :emphasize-lines: 6

        class App(TethysAppBase):
            """
            Tethys app class for Dask Tutorial.
            """
            ... 
            icon = f'{package}/images/dask-logo.png'
            ...


5. Review Results
=================

If your tethys project does not restart on its own, you may need to do so manually by ending the server with ``ctrl+c``, and then entering the command ``tethys manage start`` again. Now when you navigate to your app page, you should see this:

.. figure:: ../../images/tutorial/dask/blank_home.png
    :width: 900px
    :align: center

In the lower right hand corner is the button to navigate to the jobs table. Click that to navigate to the just created jobs table which should looks like this:

.. figure:: ../../images/tutorial/dask/blank_jobs_table.png
    :width: 900px
    :align: center

6. Solution
===========

View the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-dask_tutorial>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-dask_tutorial
    cd tethysapp-dask_tutorial
    git checkout -b setup-views-solution setup-views-solution-|version|
