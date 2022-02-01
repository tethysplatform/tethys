*****************
Multiple Leaf Job
*****************

**Last Updated:** January 2022

This section will illustrate how to use the ``dask.distributed`` API with a dask job that ends in multiple leafs. The recommended approach is to create a new ``DaskJob`` for each leaf and track them as though they were separate jobs. A similar approach can be followed using the ``dask.delayed`` API.

1. Add Job Function
===================

Add a new function to the :file:`job_functions.py` module:

::

    ...
    # Multiple Leaf Distributed Job
    def multiple_leaf_job(client):
        output = []
        for x in range(3):
            a = client.submit(inc, x, pure=False)
            b = client.submit(double, x, pure=False)
            c = client.submit(add, a, b, pure=False)
            output.append(c)
        return output
    ...

.. note::

    This job is the same as the ``dask_distributed_job`` with the final ``sum`` call removed. Since the call to ``sum`` aggregated our results in the previous job, we are now left with multiple Dask jobs to track, which the function returns as a list.

2. Setup the Controller
=======================

Modify the ``home`` controller in the :file:`controller.py` module, adding a button to the context that will launch the Multi Leaf job and update the ``run_job`` function. The entire file should look like the following:

::

    import random
    from django.shortcuts import render, reverse, redirect
    from tethys_sdk.permissions import login_required
    from django.http.response import HttpResponseRedirect
    from django.contrib import messages
    from tethys_sdk.gizmos import Button
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
        dask_delayed_button = Button(
            display_text='Dask Delayed Job',
            name='dask_delayed_button',
            attributes={
                'data-toggle': 'tooltip',
                'data-placement': 'top',
                'title': 'Dask Delayed Job'
            },
            href=reverse('dask_tutorial:run-dask', kwargs={'job_type': 'delayed'})
        )

        dask_distributed_button = Button(
            display_text='Dask Distributed Job',
            name='dask_distributed_button',
            attributes={
                'data-toggle': 'tooltip',
                'data-placement': 'top',
                'title': 'Dask Future Job'
            },
            href=reverse('dask_tutorial:run-dask', kwargs={'job_type': 'distributed'})
        )

        dask_multiple_leaf_button = Button(
            display_text='Dask Multiple Leaf Jobs',
            name='dask_multiple_leaf_button',
            attributes={
                'data-toggle': 'tooltip',
                'data-placement': 'top',
                'title': 'Dask Multiple Leaf Jobs'
            },
            href=reverse('dask_tutorial:run-dask', kwargs={'job_type': 'multiple-leaf'})
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

        context = {
            'dask_delayed_button': dask_delayed_button,
            'dask_distributed_button': dask_distributed_button,
            'dask_multiple_leaf_button': dask_multiple_leaf_button,
            'jobs_button': jobs_button,
        }

        return render(request, 'dask_tutorial/home.html', context)


    @login_required()
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
                return redirect(reverse('dask_tutorial:error_message'))

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
                return redirect(reverse('dask_tutorial:error_message'))

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

        return HttpResponseRedirect(reverse('dask_tutorial:jobs-table'))


    @login_required()
    def jobs_table(request):
        # Using job manager to get all jobs in the database.
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
        # Using job manager to get the specified job.
        job = job_manager.get_job(job_id=job_id)

        # Get result and Key
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

3. Setup HTML
=============

Modify the ``app_content`` block in the :file:`home.html` so that it looks like the following:

::

    ...
    {% block app_content %}
    <h2>Dask Delayed Job</h2>
    {% gizmo dask_delayed_button %}

    <h2>Dask Distributed Job</h2>
    {% gizmo dask_distributed_button %}

    <h2>Multi Leaf Distributed Job</h2>
    {% gizmo dask_multiple_leaf_button %}
    {% endblock %}
    ...

4. Review Multiple Leaf Job
===========================

If your tethys project does not restart on its own, you may need to do so manually by ending the server with ``ctrl+c``, and then entering the command ``tethys manage start`` again. Now when you navigate to your app page, you should see this:

.. figure:: ../../images/tutorial/NewPostMultipleLeafHome.png
    :width: 900px
    :align: center

Click on the ``Dask Multiple Leaf Jobs`` button to launch the new job type. You will see multiple jobs being tracked by the jobs table, one for each leaf:

.. figure:: ../../images/tutorial/NewPostMultipleLeafJobsTable.png
    :width: 900px
    :align: center

.. tip::

    If you get stuck, compare with the solution here: `<https://github.com/tethysplatform/tethysapp-dask_tutorial>`_

5. Solution
===========

This concludes the Dask Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-dask_tutorial>`_ or clone it as follows:

.. parsed-literal::

    git clone git@github.com:tethysplatform/tethysapp-dask_tutorial.git
    cd tethysapp-dask_tutorial
    git checkout -b solution solution-|version|
