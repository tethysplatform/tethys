*****************
Multiple Leaf Job
*****************

**Last Updated:** August 2024

This section will illustrate how to use the ``dask.distributed`` API with a dask job that ends in multiple leafs. The recommended approach is to create a new ``DaskJob`` for each leaf and track them as though they were separate jobs. A similar approach can be followed using the ``dask.delayed`` API.

1. Add Job Function
===================

Add a new function to the :file:`job_functions.py` module:

    .. code-block:: python

        # Multiple Leaf Distributed Job
        def multiple_leaf_job(client):
            output = []
            for x in range(3):
                a = client.submit(inc, x, pure=False)
                b = client.submit(double, x, pure=False)
                c = client.submit(add, a, b, pure=False)
                output.append(c)
            return output

    .. note::

        This job is the same as the ``dask_distributed_job`` with the final ``sum`` call removed. Since the call to ``sum`` aggregated our results in the previous job, we are now left with multiple Dask jobs to track, which the function returns as a list.

2. Setup the Controller
=======================

Modify the ``home`` controller in the :file:`controller.py` module, adding a button to the context that will launch the Multi Leaf job.


    .. code-block:: python
        :emphasize-lines: 28-37, 53

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

            dask_multiple_leaf_button = Button(
                display_text='Dask Multiple Leaf Jobs',
                name='dask_multiple_leaf_button',
                attributes={
                    'data-bs-toggle': 'tooltip',
                    'data-bs-placement': 'top',
                    'title': 'Dask Multiple Leaf Jobs'
                },
                href=App.reverse('run_job', kwargs={'job_type': 'multiple-leaf'})
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
                'dask_multiple_leaf_button': dask_multiple_leaf_button,
                'jobs_button': jobs_button,
            }

            return App.render(request, 'home.html', context)

Update the ``run_job`` controller to call the Multi Leaf Job:

    .. code-block:: python
        :emphasize-lines: 44-68

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

            elif job_type.lower() == 'multiple-leaf':
                from tethysapp.dask_tutorial.job_functions import multiple_leaf_job

                # Get the client to create future
                try:
                    client = scheduler.client
                except DaskJobException:
                    return App.redirect(App.reverse('error_message'))

                # Create future job instance
                futures = multiple_leaf_job(client)

                # Execute multiple future
                i = random.randint(1, 10000)

                for future in futures:
                    i += 1
                    name = 'dask_leaf' + str(i)
                    dask = job_manager.create_job(
                        job_type='DASK',
                        name=name,
                        user=request.user,
                        scheduler=scheduler,
                    )
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

        <h2>Multi Leaf Distributed Job</h2>
        {% gizmo dask_multiple_leaf_button %}
        {% endblock %}
    
4. Review Multiple Leaf Job
===========================

If your tethys project does not restart on its own, you may need to do so manually by ending the server with ``ctrl+c``, and then entering the command ``tethys manage start`` again. Now when you navigate to your app page, you should see this:

.. figure:: ../../images/tutorial/dask/home_with_multiple_button.png
    :width: 900px
    :align: center

Click on the ``Dask Multiple Leaf Jobs`` button to launch the new job type. You will see multiple jobs being tracked by the jobs table, one for each leaf:

.. figure:: ../../images/tutorial/dask/jobs_table_with_multiple.png
    :width: 900px
    :align: center

.. tip::

    If you get stuck, compare with the solution here: `<https://github.com/tethysplatform/tethysapp-dask_tutorial>`_

5. Solution
===========

View the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-dask_tutorial>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-dask_tutorial
    cd tethysapp-dask_tutorial
    git checkout -b multiple-leaf-solution multiple-leaf-solution-|version|
