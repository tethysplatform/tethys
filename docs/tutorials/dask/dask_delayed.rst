************
Dask Delayed
************

**Last Updated:** August 2024

The ``DaskJob`` can be used with either the ``dask.delayed`` or ``dask.distributed`` APIs. The next three sections will illustrate how to use each Dask API with TethysJobs. This section will illustrate how to use the ``dask.delayed`` API with ``DaskJob`` in Tethys.

1. Add Job Function
===================

Add a new function to the :file:`job_functions.py` module that builds a Dask job using the ``dask.delayed`` API approach:

    .. code-block:: python

        # Delayed Job
        def delayed_job():
            output = []
            for x in range(3):
                a = dask.delayed(inc, pure=False)(x)
                b = dask.delayed(double, pure=False)(x)
                c = dask.delayed(add, pure=False)(a, b)
                output.append(c)
            return dask.delayed(sum_up, pure=False)(output)

2. Setup Controller
===================

Modify the ``home`` controller in the :file:`controller.py` module, adding a button to the context that will launch the Dask Delayed job. Afterwards the home function should look like this:

    .. code-block:: python
        :emphasize-lines: 6-15, 29


        @controller
        def home(request):
            """
            Controller for the app home page.
            """
            dask_delayed_button = Button(
                display_text='Dask Delayed Job',
                name='dask_delayed_button',
                attributes={
                    'data-bs-toggle': 'tooltip',
                    'data-bs-placement': 'top',
                    'title': 'Dask Delayed Job'
                },
                href=App.reverse('run_job', kwargs={'job_type': 'delayed'})
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
                'dask_delayed_button': dask_delayed_button,
                'jobs_button': jobs_button
            }

            return App.render(request, 'home.html', context)


Add the ``run_job`` controller to the :file:`controller.py` module as well:

    .. code-block:: python

        @controller
        def run_job(request, job_type):
            """
            Controller for the app home page.
            """
            # Get scheduler from dask_primary setting.
            scheduler = App.get_scheduler(name='dask_primary')

            if job_type.lower() == 'delayed':
                from .job_functions import delayed_job

                # Create dask delayed object
                delayed = delayed_job()
                dask = job_manager.create_job(
                    job_type='DASK',
                    name='dask_delayed',
                    user=request.user,
                    scheduler=scheduler,
                )

                # Execute future
                dask.execute(delayed)

            return HttpResponseRedirect(App.reverse('jobs_table'))

.. note::

    We'll expand the ``run_job`` controller in the following sections to handle different Dask APIs.

3. Setup HTML
=============

Add the ``app_content`` block to the :file:`home.html` so that it looks like the following:

    .. code-block:: html+django

        {% block app_content %}
        <h2>Dask Delayed Job</h2>
        {% gizmo dask_delayed_button %}
        {% endblock %}

4. Review Dask Delayed
======================

If your tethys project does not restart on its own, you may need to do so manually by ending the server with ``ctrl+c``, and then entering the command ``tethys manage start`` again. Now when you navigate to your app page, you should see this:

.. figure:: ../../images/tutorial/dask/home_with_delayed_button.png
    :width: 900px
    :align: center

Click on the ``Dask Delayed Job`` button to launch the new job type. It will submit the job and redirect to the jobs table page:

.. figure:: ../../images/tutorial/dask/jobs_table_with_delayed.png
    :width: 900px
    :align: center

5. Solution
===========

View the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-dask_tutorial>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-dask_tutorial
    cd tethysapp-dask_tutorial
    git checkout -b dask-delayed-solution dask-delayed-solution-|version|
