***************
Setup Scheduler
***************

**Last Updated:** November 2018

1. Start Scheduler
==================

Open up a new terminal and make sure the tethys environment is activated (start it we the command ``t`` if not). Run ``tethys-dask-scheduler --tethys-host <tethys-host>`` to start the scheduler. ``<tethys-host>`` is the host of the Tethys server you'd like to link this scheduler with (i.e.: ``http://localhost:8000``).


.. figure:: ../../images/tutorial/Setup_scheduler--run_tethys_dask.png
    :align: center

.. note::

    Do not leave out the protocol when specifying ''tethys_host'' address.

2. Start Worker
===============

Open up a new terminal and make sure the tethys environment is activated. Run ``dask-worker <scheduler-host>`` to start the worker. ``<scheduler-host>`` should be the same as the ``scheduler-at`` field from the previous command.

.. figure:: ../../images/tutorial/Setup_scheduler--run_worker.png
    :align: center

3. Log in to Tethys
===================

Log in to tethys. For this tutorial use the username ``admin`` and the password ``pass``.

4. Go to Site Admin
===================

Use the drop down menu in the top right corner near your username to navigate to the ``Site Admin`` page.

.. note::

    If you are in an app, you will need to exit to the App Library page to access the drop down.

5. Dask Schedulers
==================

Scroll down to the Tethys Computing sub group and select Dask Scheduler to navigate to the Dask Scheduler page.

.. figure:: ../../images/tutorial/NewTethysCompute.png
    :align: center

6. Add a New Dask Scheduler
===========================
Select the add Dask Scheduler button. Fill out the following form to create a new scheduler. Use the name ``test_scheduler`` for this tutorial. For host and port see the scheduler terminal. Use the ``scheduler at`` field for the host field. Use the ``bokeh at`` port for dashboard field, using the same host as the scheduler. Select ``Save`` once done.

.. figure:: ../../images/tutorial/SchedulerCommand.png
    :align: center

.. figure:: ../../images/tutorial/NewCreateDaskScheduler.png
    :align: center

7. View Embedded Dashboard
==========================
Select the ``Launch Dashboard`` button to the right of your newly created dashboard to visit your embedded Dashboard. It should look like this.

.. figure:: ../../images/tutorial/NewDaskSchedulerPage.png
    :align: center