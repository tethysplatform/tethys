********
Jobs API
********

**Last Updated:** September 12, 2016

The Jobs API provides a way for your app to run asynchronous tasks (meaning that after starting a task you don't have to wait for it to finish before moving on). As an example, you may need to run a model that takes a long time (potentially hours or days) to complete. Using the Jobs API you can create a job that will run the model, and then leave it to run while your app moves on and does other stuff. You can check the job's status at any time, and when the job is done the Jobs API will help retrieve the results.


Key Concepts
============
To facilitate interacting with jobs asynchronously, they are stored in a database. The Jobs API provides a job manager to handle the details of working with the database, and provides a simple interface for creating and retrieving jobs. The first step to creating a job is to define a job template. A job template is like a blue print that describes certain key characteristics about the job, such as the job type and where the job will be run. The job manager uses a job template to create a new job that has all of the attributes that were defined in the template. Once a job has been created from a template it can then be customized with any additional attributes that are needed for that specific job.


The Jobs API supports various types of jobs (see `Job Types`_).

.. note::
    The real power of the jobs API comes when it is combined with the :doc:`compute`. This make it possible for jobs to be offloaded from the main web server to a scalable computing cluster, which in turn enables very large scale jobs to be processed. This is done through the :doc:`jobs/condor_job_type` or the :doc:`jobs/condor_workflow_type`.

.. seealso::
    The Condor Job and the Condor Workflow job types use the CondorPy library to submit jobs to HTCondor compute pools. For more information on CondorPy and HTCondor see the `CondorPy documentation <http://condorpy.readthedocs.org/en/latest/>`_ and specifically the `Overview of HTCondor <http://condorpy.readthedocs.org/en/latest/htcondor.html>`_.

Defining Job Templates
======================
To create jobs in an app you first need to define job templates. A job template specifies the type of job, and also defines all of the static attributes of the job that will be the same for all instances of that template. These attributes often include the names of the executable, input files, and output files. Job templates are defined in a method on the ``TethysAppBase`` subclass in ``app.py`` module. The following code sample shows how this is done:

::

  from tethys_sdk.jobs import CondorJobTemplate, CondorJobDescription
  from tethys_sdk.compute import list_schedulers

  def job_templates(cls):
      """
      Example job_templates method.
      """
      my_scheduler = list_schedulers()[0]

      my_job_description = CondorJobDescription(condorpy_template_name='vanilla_transfer_files',
                                                remote_input_files=('$(APP_WORKSPACE)/my_script.py', '$(APP_WORKSPACE)/input_1', '$(USER_WORKSPACE)/input_2'),
                                                executable='my_script.py',
                                                transfer_input_files=('../input_1', '../input_2'),
                                                transfer_output_files=('example_output1', 'example_output2'),
                                                )

      job_templates = (CondorJobTemplate(name='example',
                                         job_description=my_job_description,
                                         scheduler=my_scheduler,
                                        ),
                      )

      return job_templates

.. note::
    To define job templates the appropriate template class and any supporting classes must be imported from ``tethys_sdk.jobs``. In this case the template class `CondorJobTemplate` is imported along with the supporting class `CondorJobDescription`.

There is a corresponding job template class for every job type. In this example the `CondorJobTemplate` class is used, which corresponds to the :doc:`jobs/condor_job_type`. For a list of all possible job types see `Job Types`_.

When instantiating any job template class there is a required ``name`` parameter, which is used used to identify the template to the job manager (see `Using the Job Manager in your App`_). The template class for each job type may have additional required and/or optional parameters. In the above example the `job_description` and the `scheduler` parameters are required because the the `CondorJobTemplate` class is being instantiated. Job template classes may also support setting job attributes as parameters in the template. See the `Job Types`_ documentation for a list of acceptable parameters for the template class of each job type.

.. warning::
    The generic template class ``JobTemplate`` allong with the dictionary ``JOB_TYPES`` have been used to define job templates in the past but are being deprecated in favor of job-type specific templates classes (e.g. `CondorJobTemplate` or `CondorWorkflowTemplate`).

Job Types
---------
The Jobs API is designed to support multiple job types. Each job type provides a different framework and environment for executing jobs. To create a job of a particular job type, you must first create a job template from the template class corresponding to that job type (see `Defining Job Templates`_). After the job template for the job type you want has been instantiated you can create a new job instance using the job manager (see `Using the Job Manager in your App`_).

Once you have a newly created job from the job manager you can then customize the job by setting job attributes. All jobs have a common set of attributes, and then each job type may add additional attributes.

The following attributes can be defined for all job types:

    * ``name`` (string, required): a unique identifier for the job. This should not be confused with the job template name. The template name identifies a template from which jobs can be created and is set when the template is created. The job ``name`` attribute is defined when the job is created (see `Creating and Executing a Job`_).
    * ``description`` (string): a short description of the job.
    * ``workspace`` (string): a path to a directory that will act as the workspace for the job. Each job type may interact with the workspace differently. By default the workspace is set to the user's workspace in the app that is creating the job (see `Workspaces`_).
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

.. note::
    Job template classes may support passing in job attributes as additional arguments. See the documentation for each job type for a list of acceptable parameters for each template class add if additional arguments are supported.

Specific job types may define additional attributes. The following job types are available.

.. toctree::
   :maxdepth: 1

   jobs/basic_job_type
   jobs/condor_job_type
   jobs/condor_workflow_type



Workspaces
----------
Each job has it's own workspace, which by default is set to the user's workspace in the app where the job is created. However, the job may need to reference files that are in other workspaces. To make it easier to interact with workspaces in job templates, two special variables are defined: ``$(APP_WORKSPACE)`` and ``$(USER_WORKSPACE)``. These two variables are resolved to absolute paths when the job is created. These variables can only be used in job templates. To access the app's workspace and the user's workspace when working with a job in other places in your app use the :doc:`workspaces`.

.. _job-manager-label:

Job Manager
===========
The Job Manager is used in your app to interact with the jobs database. It facilitates creating and querying jobs.

Using the Job Manager in your App
=================================
To use the Job Manager in your app you first need to import the TethysAppBase subclass from the app.py module:

::

    from app import MyFirstApp as app

You can then get the job manager by calling the method ``get_job_manager`` on the app.

::

    job_manager = app.get_job_manager()

You can now use the job manager to create a new job, or retrieve an existing job or jobs.

Creating and Executing a Job
----------------------------
To create a job call the ``create_job`` method on the job manager. The required parameters are ``name``, ``user`` and ``template_name``. Any other job attributes can also be passed in as `kwargs`.

::

    # create a new job
    job = job_manager.create_job(name='job_name', user=request.user, template_name='example', description='my first job')

    # customize the job using methods provided by the job type
    job.set_attribute('arguments', 'input_2')

    # save or execute the job
    job.save()
    # or
    job.execute()

Before a controller returns a response the job must be saved or else all of the changes made to the job will be lost (executing the job automatically saves it). If submitting the job takes a long time (e.g. if a large amount of data has to be uploaded to a remote scheduler) then it may be best to use AJAX to execute the job.

.. tip::
   The `Jobs Table Gizmo`_ has a built-in mechanism for submitting jobs with AJAX. If the `Jobs Table Gizmo`_ is used to submit the jobs then be sure to save the job after it is created.

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

.. autoclass:: tethys_sdk.jobs.JobTemplate

References
==========

.. toctree::
   :maxdepth: 1

   jobs/condor_job_description