***********
Setup Views
***********

**Last Updated:** November 2018

In this section, you will setup most of the views needed for this app. For a refresher on setting up url maps, controllers, and templates, see: :doc:`../getting_started`.

1. Link URL
===========

Add `UrlMaps` for each view to :file:`app.py` in the url_maps function so that it looks like the following:

::

    from tethys_sdk.base import TethysAppBase, url_map_maker

    class DaskTutorial(TethysAppBase):
        """
        Tethys app class for Dask Tutorial.
        """

        name = 'Dask Tutorial'
        index = 'dask_tutorial:home'
        icon = 'dask_tutorial/images/icon.gif'
        package = 'dask_tutorial'
        root_url = 'dask-tutorial'
        color = '#f39c12'
        description = 'Place a brief description of your app here.'
        tags = ''
        enable_feedback = False
        feedback_emails = []

        def url_maps(self):
            """
            Add controllers
            """
            UrlMap = url_map_maker(self.root_url)

            url_maps = (
                UrlMap(
                    name='home',
                    url='dask-tutorial',
                    controller='dask_tutorial.controllers.home'
                ),
                UrlMap(
                    name='jobs-table',
                    url='dask-tutorial/dask/jobs_table',
                    controller='dask_tutorial.controllers.jobs_table'
                ),
                UrlMap(
                    name='result',
                    url='dask-tutorial/dask/result/{job_id}',
                    controller='dask_tutorial.controllers.result'
                ),
                UrlMap(
                    name='error_message',
                    url='dask-tutorial/dask/error',
                    controller='dask_tutorial.controllers.error_message'
                ),
            )

            return url_maps


2. Add Job Functions
====================

Create :file:`job_functions.py` and set its contents to the following:

::

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


3. Setup Controller
===================

Add the jobs button to the ``home`` controller in :file:`controller.py` module such that it looks like this:

::

    import random
    from django.shortcuts import render, reverse, redirect
    from django.contrib.auth.decorators import login_required
    from django.http.response import HttpResponseRedirect
    from django.contrib import messages
    from tethys_sdk.gizmos import Button
    from tethys_sdk.compute import get_scheduler
    from tethys_sdk.gizmos import JobsTable
    from tethys_compute.models.dask.dask_job_exception import DaskJobException
    from tethysapp.dask_tutorial.app import DaskTutorial as app

    # get job manager for the app
    job_manager = app.get_job_manager()

    @login_required()
    def home(request):
        """
        Controller for the app home page.
        """

        jobs_button = Button(
            display_text='Show All Jobs',
            name='dask_button',
            attributes={
                'data-toggle': 'tooltip',
                'data-placement': 'top',
                'title': 'Show All Jobs'
            },
            href=reverse('dask_tutorial:jobs-table')
        )

        context = {
            'jobs_button': jobs_button
        }

        return render(request, 'dask_tutorial/home.html', context)

Add two new controllers, ``jobs_table`` and ``result``, and the error handler, ``error_message``, to the :file:`controller.py` module:

::

    ...
    @login_required()
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
            results_url='dask_tutorial:result',
            refresh_interval=1000,
            delete_btn=True,
            show_detailed_status=True,
        )

        home_button = Button(
            display_text='Home',
            name='home_button',
            attributes={
                'data-toggle': 'tooltip',
                'data-placement': 'top',
                'title': 'Home'
            },
            href=reverse('dask_tutorial:home')
        )

        context = {'jobs_table': jobs_table_options, 'home_button': home_button}

        return render(request, 'dask_tutorial/jobs_table.html', context)


    @login_required()
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
                'data-toggle': 'tooltip',
                'data-placement': 'top',
                'title': 'Home'
            },
            href=reverse('dask_tutorial:home')
        )

        jobs_button = Button(
            display_text='Show All Jobs',
            name='dask_button',
            attributes={
                'data-toggle': 'tooltip',
                'data-placement': 'top',
                'title': 'Show All Jobs'
            },
            href=reverse('dask_tutorial:jobs-table')
        )

        context = {'result': job_result, 'name': name, 'home_button': home_button, 'jobs_button': jobs_button}

        return render(request, 'dask_tutorial/results.html', context)


    @login_required()
    def error_message(request):
        messages.add_message(request, messages.ERROR, 'Invalid Scheduler!')
        return redirect(reverse('dask_tutorial:home'))



3. Set up HTML
==============

Create :file:`jobs_table.html`. Change it so that the contents are as follows:

::

    {% extends "dask_tutorial/base.html" %}
    {% load staticfiles tethys_gizmos %}

    {% load tethys_gizmos %}

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

Create file :file:`error.html` and set its contents to the following:

::

    {% extends "dask_tutorial/base.html" %}
    {% load tethys_gizmos %}

    {% block header_buttons %}
      <div class="header-button glyphicon-button" data-toggle="tooltip" data-placement="bottom" title="Help">
        <a data-toggle="modal" data-target="#help-modal"><span class="glyphicon glyphicon-question-sign"></span></a>
      </div>
    {% endblock %}

    {% block app_content %}
      <div class="error-message">
        {{ error_message }}
      </div>
    {% endblock %}

    {% block app_actions %}
      {% gizmo jobs_button %}
    {% endblock %}

Edit :file:`home.html` and and set it to the following:

::

    {% extends "dask_tutorial/base.html" %}
    {% load tethys_gizmos %}

    {% block header_buttons %}
      <div class="header-button glyphicon-button" data-toggle="tooltip" data-placement="bottom" title="Help">
        <a data-toggle="modal" data-target="#help-modal"><span class="glyphicon glyphicon-question-sign"></span></a>
      </div>
    {% endblock %}

    {% block app_actions %}
      {% gizmo jobs_button %}
    {% endblock %}

Define :file:`results.html` to be the following:

::

    {% extends "dask_tutorial/base.html" %}
    {% load staticfiles tethys_gizmos %}

    {% load tethys_gizmos %}

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

Edit :file:`base.html` to be the following:

::

    {% extends "tethys_apps/app_base.html" %}

    {% load staticfiles %}

    {% block title %}{{ tethys_app.name }}{% endblock %}

    {% block app_icon %}
      {# The path you provided in your app.py is accessible through the tethys_app.icon context variable #}
      <img src="{% static tethys_app.icon %}">
    {% endblock %}

    {# The name you provided in your app.py is accessible through the tethys_app.name context variable #}
    {% block app_title %}{{ tethys_app.name }}{% endblock %}

    {% block app_navigation_toggle_override %}
    {% endblock %}

    {% block app_navigation_override %}
    {% endblock %}

    {% block app_content %}
    {% endblock %}

    {% block app_actions %}
    {% endblock %}

    {% block content_dependent_styles %}
      {{ block.super }}
      <link href="{% static 'dask_tutorial/css/main.css' %}" rel="stylesheet"/>
    {% endblock %}

    {% block scripts %}
      {{ block.super }}
      <script src="{% static 'dask_tutorial/js/main.js' %}" type="text/javascript"></script>
    {% endblock %}

4. Edit Styles
==============

Edit :file:`main.css` to be the following:

::

    #app-header .tethys-app-header #nav-title-wrapper {
        margin-left: 20px;
    }

5. Review Results
=================

If your tethys project does not restart on its own, you may need to do so manually by ending the server with ``ctrl+c``, and then entering the command ``tethys manage start`` again. Now when you navigate to your app page, you should see this:

.. figure:: ../../images/tutorial/NewPostCreateViewsHome.png
    :align: center

In the lower right hand corner is the button to navigate to the jobs table. Click that to navigate to the just created jobs table which should looks like this:

.. figure:: ../../images/tutorial/NewPostCreateViewsJobTable.png
    :align: center

.. tip::

    If you get stuck, compare with the solution here: `<https://github.com/tethysplatform/tethysapp-dask_tutorial>`_