.. _jobs_api:

********
Jobs API
********

**Last Updated:** September 2024

The Jobs API provides a way for your app to run asynchronous tasks (meaning that after starting a task you don't have to wait for it to finish before moving on). As an example, you may need to run a simulation that takes a long time (potentially hours or days) to complete. Using the Jobs API you can create a job that will submit the simulation run, and then leave it to run while your app moves on and does other stuff. You can check the job's status at any time, and when the job is done the Jobs API will help retrieve the results.

Job Management Software
=======================

The Jobs API leverages third-party job management systems to perform the actual execution of the jobs, including HTCondor and Dask. HTCondor is well suited for executing long-running executable-like jobs, such as running a simulation. Dask is ideal for converting existing Python logic into efficient, parallel running code, especially logic that uses the SciPy stack to perform the analysis.

To learn more about HTCondor and Dask, review the following resources:

* `Overview of HTCondor <https://condorpy.readthedocs.io/en/latest/htcondor.html>`_
* `HTCondor User Manual <https://research.cs.wisc.edu/htcondor/manual/>`_
* `Dask Overview <https://docs.dask.org/en/latest/>`_
* `Dask Distributed <https://distributed.dask.org/en/stable/>`_


.. _jobs_api_schedulers:

Schedulers
==========

A scheduler is the part of a job managment system that is responsible for accepting job requests and assigning them to the appropriate computing resources to be executed. The Jobs API needs to know how to connect to the scheduler to be able to submit jobs. This is done by adding Scheduler entries in the Tethys Portal admin pages (see: :ref:`Tethys Compute Admin Pages: Schedulers <schedulers-label>`).

.. note::

    Schedulers can also be created and accessed programmatically using the lower-level compute API. However, this approach is only recommended for experienced developers (see: :ref:`lower_level_scheduler_api`).

.. _jobs_api_scheduler_app_settings:

Scheduler App Settings
----------------------

Apps that use either HTCondor or Dask should define one or more app Scheduler Settings in their :term:`app class`. Tethys Portal administrators use this setting to assign an appropriate Scheduler to the app when it is being configured. To access Schedulers assigned to app Scheduler Settings, use the ``get_scheduler()`` method of the :term:`app class`. See :ref:`Scheduler Settings <app_settings_scheduler_settings>` for more details.

.. _job-manager-label:

Job Manager
===========

To facilitate interacting with jobs asynchronously, the metadata of the jobs are stored in a database. The Jobs API provides a Job Manager to handle the details of working with the database, and provides a simple interface for creating and retrieving jobs. The Jobs API supports various types of jobs (see `Job Types`_).

.. .. seealso::

..     The Condor Job and the Condor Workflow job types use the CondorPy library to submit jobs to HTCondor compute pools. For more information on CondorPy and HTCondor see the `CondorPy documentation <https://condorpy.readthedocs.io/en/latest/>`_ and specifically the `Overview of HTCondor <https://condorpy.readthedocs.io/en/latest/htcondor.html>`_.

..     The Dask Job uses the Dask Distributed python library to automatically parallelize your Python code and run them on a distributed cluster of workers. For more information on Dask, see: `Dask <https://docs.dask.org/en/latest/>`_ and `Dask Distributed <https://distributed.dask.org/en/latest/>`_ documentation.

Using the Job Manager in your App
---------------------------------
To use the Job Manager in your app you first need to import the TethysAppBase subclass from the app.py module:

.. code-block:: python

    from .app import App

You can then get the job manager by calling the method ``get_job_manager`` on the app.

.. code-block:: python

    job_manager = App.get_job_manager()

You can now use the job manager to create a new job, or retrieve an existing job or jobs.

Creating and Executing a Job
----------------------------
To create a new job call the ``create_job`` method on the job manager. The required arguments are:
    * ``name``: A unique string identifying the job
    * ``user``: A user object, usually from the request argument: `request.user`
    * ``job_type``: A string specifying on of the supported job types (see `Job Types`_)

Any other job attributes can also be passed in as `kwargs`.

.. code-block:: python

    # create a new job from the job manager
    job = job_manager.create_job(
        name='myjob_{id}',  # required
        user=request.user,  # required
        job_type='CONDOR',  # required

        # any other properties can be passed in as kwargs
        attributes=dict(attribute1='attr1'),
        condorpy_template_name='vanilla_transfer_files',
        remote_input_files=(
            os.path.join(app_workspace, 'my_script.py'),
            os.path.join(app_workspace, 'input_1'),
            os.path.join(app_workspace, 'input_2')
        )
    )

    # properties can also be added after the job is created
    job.extended_properties = {'one': 1, 'two': 2}

    # each job type may provided methods to further specify the job
    job.set_attribute('executable', 'my_script.py')

    # save or execute the job
    job.save()
    # or
    job.execute()

Before a controller returns a response the job must be saved or else all of the changes made to the job will be lost (executing the job automatically saves it). If submitting the job takes a long time (e.g. if a large amount of data has to be uploaded to a remote scheduler) then it may be best to use AJAX to call the controller that executes the job in the background.

.. tip::

   The `Jobs Table Gizmo`_ has a built-in mechanism for submitting jobs with AJAX. If the `Jobs Table Gizmo`_ is used to submit the jobs then be sure to save the job after it is created.

Common Attributes
-----------------

Job attributes can be passed into the `create_job` method of the job manager or they can be specified after the job is instantiated. All jobs have a common set of attributes. Each job type may have additional attributes specific that are to that job type.

The following attributes can be defined for *all* job types:
    * ``name`` (string, required): a unique identifier for the job. This should not be confused with the job template name. The template name identifies a template from which jobs can be created and is set when the template is created. The job ``name`` attribute is defined when the job is created (see `Creating and Executing a Job`_).
    * ``description`` (string): a short description of the job.
    * ``workspace`` (string): a path to a directory that will act as the workspace for the job. Each job type may interact with the workspace differently. By default the workspace is set to the user's workspace in the app that is creating the job.
    * ``extended_properties`` (dict): a dictionary of additional properties that can be used to create custom job attributes.
    * ``status`` (string): a string representing the state of the job. When accessed the status will be updated if necessary. Possible statuses are:
        - Pending
        - Submitted
        - Running
        - Paused
        - Results-Ready
        - Complete
        - Error
        - Aborted
        - Various\*
        - Various-Complete\*
        - Other\**

        \*used for job types with multiple sub-jobs (e.g. CondorWorkflow).

        \**When  a custom job status is set the official status is 'Other', but the custom status is stored as an extended property of the job. See `Custom Statuses`_

    * ``cached_status`` (string): Same as the ``status`` attribute, except that the status is not actively updated. Rather the last known status is returned.

All job types also have the following **read-only** attributes:
    * ``user`` (User): the user who created the job.
    * ``label`` (string): the package name of the Tethys App used to created the job.
    * ``creation_time`` (datetime): the time the job was created.
    * ``execute_time`` (datetime): the time that job execution was started.
    * ``start_time`` (datetime):
    * ``completion_time`` (datetime): the time that the job status changed to 'Complete'.

Job Types
---------

The Jobs API is designed to support multiple job types. Each job type provides a different framework and environment for executing jobs. When creating a new job you must specify its type by passing in the ``job_type`` argument. Supported values for ``job_type`` are:
    * "BASIC"
    * "CONDOR" or "CONDORJOB"
    * "CONDORWORKFLOW"
    * "DASK"

For detailed documentation on each of the job types see:

.. toctree::
   :maxdepth: 1

   jobs/basic_job_type
   jobs/condor_job_type
   jobs/condor_workflow_type
   jobs/dask_job_type


Retrieving Jobs
---------------
Two methods are provided to retrieve jobs: ``list_jobs`` and ``get_job``. Jobs are automatically filtered by app. An optional ``user`` parameter can be passed in to these methods to further filter jobs by the user.

.. code-block:: python

    # get list of all jobs created in your app
    job_manager.list_jobs()

    # get list of all jobs created by current user in your app
    job_manager.list_jobs(user=request.user)

    # get job with id of 27
    job_manager.get_job(job_id=27)

    # get job with id of 27 only if it was created by current user
    job_manager.get_job(job_id=27, user=request.user)

.. caution::
    Be thoughtful about how you retrieve jobs. The user filter is provided to prevent unauthorized users from accessing jobs that don't belong to them.

Jobs Table Gizmo
----------------
The Jobs Table Gizmo facilitates job management through the web interface and is designed to be used in conjunction with the Job Manager. It can be configured to list any of the properties of the jobs, and will automatically update the job status. It also can provide a list of actions that can be done on the a job. In addition to several build-in actions (including run, delete, viewing job results, etc.), developers can also create custom actions to include in the actions dropdown list. Note that while none of the built-in actions are asynchronous on any of the built-in `Job Types`_, the Jobs Table supports both synchronous and asynchronous actions. Custom actions or the built-in actions of custom job types may be asynchronous. The following code sample shows how to use the job manager to populate the jobs table:

.. code-block:: python

    job_manager = App.get_job_manager()

    jobs = job_manager.list_jobs(request.user)

    jobs_table_options = JobsTable(
        jobs=jobs,
        column_fields=('id', 'name', 'description', 'creation_time', 'execute_time'),
        actions=['run', 'resubmit', '|', 'logs', '|', 'terminate', 'delete'],
        hover=True,
        striped=False,
        bordered=False,
        condensed=False,
        results_url=f'{App.package}:results_controller',
    )

.. seealso::
    :doc:`gizmos/jobs_table`

Job Status Callback
-------------------
Each job has a callback URL that will update the job's status. The URL is of the form:

.. code-block::

    http://<host>/update-job-status/<job_id>/

For example, a URL may look something like this:

.. code-block::

    http://example.com/update-job-status/27/

The response would look something like this:

.. code-block:: javascript

    {"success": true}

This URL can be retrieved from the job manager with the ``get_job_status_callback_url`` method, which requires a `request` object and the id of the job.

.. code-block:: python

    job_manager = App.get_job_manager()
    callback_url = job_manager.get_job_status_callback_url(request, job_id)

The callback URL can be used to update the jobs status after a specified delay by passing the ``delay`` query parameter:

.. code-block::

    http://<host>/update-job-status/<job_id>/?delay=<delay_in_seconds>

For example, to schedule a job update in 30 seconds:

.. code-block::

    http://<host>/update-job-status/27/?delay=30

In this case the response would look like this:

.. code-block:: javascript

    {"success": "scheduled"}

This delay can be useful so the job itself can hit the endpoint just before completing to trigger the Tethys Portal to check its status after it has time to complete and exit. This will allow the portal to register that the job has completed and start any data transfer that is triggered upon job completion.

Custom Statuses
---------------
Custom statuses can be given to jobs simply by assigning the ``status`` attribute:

.. code-block:: python

    my_job.status = "Custom Status"

However, note that the ``TethysJob.update_status`` method will only check for updated statuses of jobs where the current status is one of the ``TethysJob.NON_TERMINAL_STATUSES``. The default ``TethysJob.NON_TERMINAL_STATUSES`` are:
    - Pending
    - Submitted
    - Running
    - Various
    - Paused

Also note that the `Jobs Table Gizmo`_ will only actively poll the status of jobs that have one of the ``TethysJob.ACTIVE_STATUSES``. The default ``TethysJob.ACTIVE_STATUSES`` are:
    - Submitted
    - Running
    - Various

If you would like to classify a custom status to take advantage of these features then there are several methods on the ``TethysJob`` class to add custom statuses to various categories. For example:

.. code-block:: python

    TethysJob.add_custom_active_status("Custom Status")

This will ensure that the jobs table will continue to poll the server to update the status and that the ``TethysJob.update_status`` method will check if the status has changed. See the details of these methods below in the API documentation for `Tethys Job`_:
    - ``add_custom_pre_running_status``
    - ``add_custom_running_status``
    - ``add_custom_active_status``
    - ``add_custom_terminal_status``

.. note::

    When adding a custom status to the ``TethysJob.NON_TERMINAL_STATUSES`` the status will be updated when the ``TethysJob.update_status`` method is called. This is the intended behavior, however, it may be necessary to modify the ``TethysJob.update_status`` method to add additional logic that preserves the desired custom status. This is most easily done by subclassing the ``TethysJob`` class (or one of it's subclasses).

API Documentation
=================

.. job_manager_api:

Job Manager
-----------

.. autoclass:: tethys_compute.job_manager.JobManager
    :members: create_job, list_jobs, get_job, get_job_status_callback_url

.. tethys_job_api:

Tethys Job
----------

.. autoclass:: tethys_compute.models.TethysJob
    :members:

.. _lower_level_scheduler_api:

Low-Level Scheduler API
-----------------------

.. autofunction:: tethys_sdk.compute.list_schedulers

.. autofunction:: tethys_sdk.compute.get_scheduler

.. autofunction:: tethys_sdk.compute.create_scheduler

.. autofunction:: tethys_sdk.compute.create_condor_scheduler

.. autofunction:: tethys_sdk.compute.create_dask_scheduler