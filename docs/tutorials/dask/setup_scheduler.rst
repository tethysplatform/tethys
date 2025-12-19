.. _dask_tutorial_setup_scheduler:

***************
Setup Scheduler
***************

**Last Updated:** August 2024

1. Start Scheduler
==================

Open up a new terminal and make sure the tethys environment is activated. To start a Dask scheduler with the Tethys Dask Scheduler plugin active run:


.. code-block:: bash

    dask-scheduler --preload tethys_dask_scheduler.plugin --tethys-host <tethys-host>

``<tethys-host>`` is the host of the Tethys server you'd like to link this scheduler with (i.e.: ``http://localhost:8000``).


.. figure:: ../../images/tutorial/Setup_scheduler--run_tethys_dask.png
    :width: 1000px
    :align: center

.. tip::

    Do not leave out the protocol (http/https) when specifying ''tethys_host'' address.

2. Start Worker
===============

Open up a new terminal and make sure the tethys environment is activated. To start the worker run:

.. code-block:: bash

    dask-worker <scheduler-host>

``<scheduler-host>`` should be the same as the ``scheduler-at`` field from the previous command (e.g.: ``tcp://192.168.1.17:8786``).

.. figure:: ../../images/tutorial/Setup_scheduler--run_worker.png
    :width: 1000px
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

Scroll down to the **TETHYS COMPUTE** section and select **Dask Schedulers** to navigate to the **Dask Schedulers** page.

.. figure:: ../../images/tethys_compute/tethys_compute_admin.png
    :width: 900px
    :align: center

6. Add a New Dask Scheduler
===========================

Select the **Add Dask Scheduler** button. Fill out the following form to create a new scheduler. Use the name ``dask_localhost`` for this tutorial. 
For host and port see the scheduler terminal. Use the ``scheduler at`` value (e.g.: 192.168.1.17:8786) for the **Host** field. Set **Timeout** to 60. Use the ``dashboard at``
port with the scheduler at host (e.g.: 192.168.1.17:8787) for the **Dashboard** field, using the same host as the scheduler. Select ``Save`` once done.

.. figure:: ../../images/tethys_compute/tethys_compute_dask_scheduler.png
    :width: 900px
    :align: center

.. tip::

    Don't include the protocol (i.e.: tcp://) or suffix (i.e.: **/status**) when specifying the **Host** and **Dashboard** fields.

7. View Embedded Dashboard
==========================
Select the **Launch Dashboard** link to the right of your newly created dashboard to visit your embedded Dashboard. It should look like this.

.. figure:: ../../images/tethys_compute/tethys_compute_dashboard.png
    :width: 900px
    :align: center

8. Create Scheduler Setting
===========================

Add the ``scheduler_settings()`` method to the app class. Return a single ``SchedulerSetting`` object in a tuple as shown below. Set the name to ``dask_primary`` and engine to ``DASK``:

.. code-block::

    from tethys_sdk.base import TethysAppBase
    from tethys_sdk.app_settings import SchedulerSetting


    class App(TethysAppBase):
        """
        Tethys app class for Dask Tutorial.
        """

        ...

        def scheduler_settings(self):
            scheduler_settings = (
                SchedulerSetting(
                    name='dask_primary',
                    description='Scheduler for a Dask distributed cluster.',
                    engine=SchedulerSetting.DASK,
                    required=True
                ),
            )

            return scheduler_settings

.. tip::

    You may need to uninstall the app and reinstall it for the new scheduler setting to be loaded properly:

    .. code-block::

        tethys uninstall dask_tutorial
        tethys install -d

9. Assign Scheduler to App Setting
==================================

a. After reloading the app, login to the Tethys Portal as an admin user.

b. Navigate to the Site Admin page as described in Step 4.

c. Locate the **TETHYS APPS** section and click on the **Installed Apps** link.

d. Select the **Dask Tutorial** link from the list of installed apps.

e. Scroll down to the **SCHEDULER SETTINGS** section and locate the row with the setting named ``dask_primary``.

f. Use the dropdown in the **SCHEDULER SERVICE** column to select the ``dask_localhost`` scheduler that you configured in step 6.

g. Press the ``SAVE`` button to save the changes.

.. figure:: ../../images/tutorial/DaskAppSettings.png
    :width: 900px
    :align: center

10. Solution
============

View the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-dask_tutorial>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-dask_tutorial
    cd tethysapp-dask_tutorial
    git checkout -b setup-scheduler-solution setup-scheduler-solution-|version|
