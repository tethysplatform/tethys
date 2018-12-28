********
Jobs API
********

**Last Updated:** December 27, 2018

The Jobs API provides a way for your app to run asynchronous tasks (meaning that after starting a task you don't have to wait for it to finish before moving on). As an example, you may need to run a model that takes a long time (potentially hours or days) to complete. Using the Jobs API you can create a job that will run the model, and then leave it to run while your app moves on and does other stuff. You can check the job's status at any time, and when the job is done the Jobs API will help retrieve the results.


Key Concepts
============
To facilitate interacting with jobs asynchronously, the details of the jobs are stored in a database. The Jobs API provides a job manager to handle the details of working with the database, and provides a simple interface for creating and retrieving jobs. The Jobs API supports various types of jobs (see `Job Types`_).

.. deprecated::2.1
    Creating jobs used to be done via job templates. This method is now deprecated.

.. _job-manager-label:

Job Manager
===========
The Job Manager is used in your app to interact with the jobs database. It facilitates creating and querying jobs.

Using the Job Manager in your App
---------------------------------
To use the Job Manager in your app you first need to import the TethysAppBase subclass from the app.py module:

::

    from app import MyFirstApp as app

You can then get the job manager by calling the method ``get_job_manager`` on the app.

::

    job_manager = app.get_job_manager()

You can now use the job manager to create a new job, or retrieve an existing job or jobs.

Creating and Executing a Job
----------------------------
To create a new job call the ``create_job`` method on the job manager. The required arguments are:

    * ``name``: A unique string identifying the job
    * ``user``: A user object, usually from the request argument: `request.user`
    * ``job_type``: A string specifying on of the supported job types (see `Job Types`_)

Any other job attributes can also be passed in as `kwargs`.

::

    # get the path to the app workspace to reference job files
    app_workspace = app.get_app_workspace().path

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

Before a controller returns a response the job must be saved or else all of the changes made to the job will be lost (executing the job automatically saves it). If submitting the job takes a long time (e.g. if a large amount of data has to be uploaded to a remote scheduler) then it may be best to use AJAX to execute the job.

.. tip::
   The `Jobs Table Gizmo`_ has a built-in mechanism for submitting jobs with AJAX. If the `Jobs Table Gizmo`_ is used to submit the jobs then be sure to save the job after it is created.

Job Types
---------
The Jobs API is designed to support multiple job types. Each job type provides a different framework and environment for executing jobs. When creating a new job you must specify its type by passing in the `job_type` argument. Currently the supported job types are:

    * 'BASIC'
    * 'CONDOR' or 'CONDORJOB'
    * 'CONDORWORKFLOW'

Additional job attributes can be passed into the `create_job` method of the job manager or they can be specified after the job is instantiated. All jobs have a common set of attributes, and then each job type may add additional attributes.

The following attributes can be defined for all job types:

    * ``name`` (string, required): a unique identifier for the job. This should not be confused with the job template name. The template name identifies a template from which jobs can be created and is set when the template is created. The job ``name`` attribute is defined when the job is created (see `Creating and Executing a Job`_).
    * ``description`` (string): a short description of the job.
    * ``workspace`` (string): a path to a directory that will act as the workspace for the job. Each job type may interact with the workspace differently. By default the workspace is set to the user's workspace in the app that is creating the job.
    * ``extended_properties`` (dict): a dictionary of additional properties that can be used to create custom job attributes.


All job types also have the following read-only attributes:

    * ``user`` (User): the user who created the job.
    * ``label`` (string): the package name of the Tethys App used to created the job.
    * ``creation_time`` (datetime): the time the job was created.
    * ``execute_time`` (datetime): the time that job execution was started.
    * ``start_time`` (datetime):
    * ``completion_time`` (datetime): the time that the job status changed to 'Complete'.
    * ``status`` (string): a string representing the state of the job. Possible statuses are:

        - 'Pending'
        - 'Submitted'
        - 'Running'
        - 'Complete'
        - 'Error'
        - 'Aborted'
        - 'Various'\*
        - 'Various-Complete'\*

        \*used for job types with multiple sub-jobs (e.g. CondorWorkflow).

Specific job types may define additional attributes. The following job types are available.

.. toctree::
   :maxdepth: 1

   jobs/basic_job_type
   jobs/condor_job_type
   jobs/condor_workflow_type


Retrieving Jobs
---------------
Two methods are provided to retrieve jobs: ``list_jobs`` and ``get_job``. Jobs are automatically filtered by app. An optional ``user`` parameter can be passed in to these methods to further filter jobs by the user.

::

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
The Jobs Table Gizmo facilitates job management through the web interface and is designed to be used in conjunction with the Job Manager. It can be configured to list any of the properties of the jobs, and will automatically update the job status, and provides buttons to run, delete, or view job results. The following code sample shows how to use the job manager to populate the jobs table:

::

    job_manager = app.get_job_manager()

    jobs = job_manager.list_jobs(request.user)

    jobs_table_options = JobsTable(jobs=jobs,
                                   column_fields=('id', 'description', 'run_time'),
                                   hover=True,
                                   striped=False,
                                   bordered=False,
                                   condensed=False,
                                   results_url='my_first_app:results',
                                   )

.. seealso::
    :doc:`gizmos/jobs_table`

Job Status Callback
-------------------
Each job has a callback URL that will update the job's status. The URL is of the form:

::

    http://<host>/update-job-status/<job_id>/

For example, a URL may look something like this:

::

    http://example.com/update-job-status/27/

The output would look something like this:
::

    {"success": true}

This URL can be retrieved from the job manager with the ``get_job_status_callback_url`` method, which requires a `request` object and the id of the job.

::

    job_manager = app.get_job_manager()
    callback_url = job_manager.get_job_status_callback_url(request, job_id)

API Documentation
=================

.. autoclass:: tethys_compute.job_manager.JobManager
    :members: create_job, list_jobs, get_job, get_job_status_callback_url

.. autoclass:: tethys_compute.models.TethysJob

References
==========

.. toctree::
   :maxdepth: 1

   jobs/condor_job_description
