****************
Dask Distributed
****************

**Last Updated:** August 2024

This section will illustrate how to use the ``dask.distributed`` API with ``DaskJob`` in Tethys. This example also illustrates how to use a custom process results function.

1. Add Job Function
===================

Add a new function to the :file:`job_functions.py` module that builds the same Dask job as before using the ``dask.distributed`` API approach:

    .. code-block:: python

        # Distributed Job
        def distributed_job(client):
            output = []
            for x in range(3):
                a = client.submit(inc, x, pure=False)
                b = client.submit(double, x, pure=False)
                c = client.submit(add, a, b, pure=False)
                output.append(c)
            return client.submit(sum_up, output)



2. Setup the Controller
=======================

Modify the ``home`` controller in the :file:`controller.py` module, adding a button to the context that will launch the Dask Distributed job. Afterwards the home function should look like this:

    .. code-block:: python
        :emphasize-lines: 17-26, 41

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

            dask_distributed_button = Button(
                display_text='Dask Distributed Job',
                name='dask_distributed_button',
                attributes={
                    'data-bs-toggle': 'tooltip',
                    'data-bs-placement': 'top',
                    'title': 'Dask Future Job'
                },
                href=App.reverse('run_job', kwargs={'job_type': 'distributed'})
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
                'dask_distributed_button': dask_distributed_button,
                'jobs_button': jobs_button,
            }

            return App.render(request, 'home.html', context)

Additionally update the ``run_job`` controller in :file:`controller.py` to look like:

    .. code-block:: python
        :emphasize-lines: 24-42

        @controller
        def run_job(request, job_type):
            """
            Controller for the app home page.
            """
            # Get scheduler from dask_primary setting.
            scheduler = app.get_scheduler(name='dask_primary')

            if job_type.lower() == 'delayed':
                from tethysapp.dask_tutorial.job_functions import delayed_job

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

            elif job_type.lower() == 'distributed':
                from tethysapp.dask_tutorial.job_functions import distributed_job, convert_to_dollar_sign

                # Get the client to create future
                try:
                    client = scheduler.client
                except DaskJobException:
                    return App.redirect(App.reverse('error_message'))

                # Create future job instance
                future = distributed_job(client)
                dask = job_manager.create_job(
                    job_type='DASK',
                    name='dask_distributed',
                    user=request.user,
                    scheduler=scheduler,
                )
                dask.process_results_function = convert_to_dollar_sign
                dask.execute(future)

            return HttpResponseRedirect(App.reverse('jobs_table'))

3. Setup HTML
=============

Modify the ``app_content`` block in the :file:`home.html` so that it looks like the following:

    .. code-block:: html+django

        {% block app_content %}
        <h2>Dask Delayed Job</h2>
        {% gizmo dask_delayed_button %}

        <h2>Dask Distributed Job</h2>
        {% gizmo dask_distributed_button %}
        {% endblock %}

4. Review Dask Distributed
==========================

If your tethys project does not restart on its own, you may need to do so manually by ending the server with ``ctrl+c``, and then entering the command ``tethys manage start`` again. Now when you navigate to your app page, you should see this:

.. figure:: ../../images/tutorial/dask/home_with_distributed_button.png
    :width: 900px
    :align: center

Click on the ``Dask Distributed Job`` button to launch the new job type. It will submit the job and redirect to the jobs table page:

.. figure:: ../../images/tutorial/dask/jobs_table_with_distributed.png
    :width: 900px
    :align: center

5. Solution
===========

View the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-dask_tutorial>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-dask_tutorial
    cd tethysapp-dask_tutorial
    git checkout -b dask-distributed-solution dask-distributed-solution-|version|
