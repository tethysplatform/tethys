********
Jobs API
********

**Last Updated:** February 11, 2016

The Jobs API provides a way for your app to run asynchronous tasks (meaning that after starting a task you don't have to wait for it to finish before moving on). As an example, you may need to run a model that takes a long time (potentially hours or days) to complete. Using the Jobs API you can create a job that will run the model, and then leave it to run while your app moves on and does other stuff. You can check the job's status at any time, and when the job is done the Jobs API will help retrieve the results.

.. note::
    The real power of the jobs API comes when it is combined with the :doc:`compute`. This make it possible for jobs to be offloaded from the main web server to a scalable computing cluster, which in turn enables very large scale jobs to be processed. This is done through the `CondorJob`_ type.


Key Concepts
============
To facilitate interacting with jobs asynchronously, they are stored in a database. The Jobs API provides a job manager to handle the details of working with the database, and provides a simple interface for creating and retrieving jobs. The first step to creating a job is to define a job template. A job template is like a blue print that describes certain key characteristics about the job, such as the job type and where the job will be run. The job manager uses a job template to create a new job that has all of the characteristics there were defined in the template. Once a job has been created from a template it can then be customized with any parameters that are needed for that specific job.


The Jobs API supports various types of jobs (see `Job Types`_), but the primary type, which is used in conjunction with the :doc:`compute`, is the `CondorJob`_ type.

.. seealso::
    The CondorJob type uses the CondorPy library to submit jobs to HTCondor compute pools. For more information on CondorPy and HTCondor see the `CondorPy documentation <http://condorpy.readthedocs.org/en/latest/>`_ and specifically the `Overview of HTCondor <http://condorpy.readthedocs.org/en/latest/htcondor.html>`_.

Defining Job Templates
======================
To create jobs in an app you first need to define job templates. A job template specifies the type of job, and also defines all of the static parameters of the job that will be the same for all instances of that template. These parameters often include the names of the executable, input files, and output files. Job templates are defined in a method on the ``TethysAppBase`` subclass in ``app.py`` module. The following code sample shows how this is done:

::

  from tethys_sdk.jobs import JobTemplate, JOB_TYPES
  from tethys_sdk.compute import list_schedulers

  def job_templates(cls):
      """
      Example job_templates method.
      """
      my_scheduler = list_schedulers()[0]

      job_templates = (JobTemplate(name='example',
                                   type=JOB_TYPES['CONDOR'],
                                   parameters={'executable': 'my_script.py',
                                               'condorpy_template_name': 'vanilla_transfer_files',
                                               'attributes': {'transfer_input_files': ('../input_1', '../input_2'),
                                                              'transfer_output_files': ('example_output1', example_output2),
                                                             },
                                               'scheduler': my_scheduler,
                                               'remote_input_files': ('$(APP_WORKSPACE)/my_script.py', '$(APP_WORKSPACE)/input_1', '$(USER_WORKSPACE)/input_2'),
                                              }
                                  ),
                      )

      return job_templates

Note that ``JobTemplate`` and ``JOB_TYPES`` need to be imported through the jobs SDK. A job template takes three arguments:

* ``name``: A string designating the name of the template. This will be used to identify the template in the app controllers.
* ``type``: The name of a Tethys job type. These can be accessed through the ``JOB_TYPES`` dictionary (see `Job Types`_).
* ``parameters``: A dictionary of job parameters. These are parameters that will be the same for all instances of this job template. Additional parameters can be added to a job once it is created from the template (see `Using the Job Manager in your App`_). The acceptable parameters are determined by the job type.

.. Note::
    In this example the ConorJob type is used. For more information about the CondorJob parameters see `CondorJob`_.

For convenience, templates for specific job types (e.g. ``CondorJobTemplate``) can be imported rather than the generic ``JobTemplate``. In this case the type is already defined; thus only the ``name`` and ``parameters`` arguments must be specified.

::

  from tethys_sdk.jobs import CondorJobTemplate
  from tethys_sdk.compute import list_schedulers

  def job_templates(cls):
      """
      Example job_templates method.
      """
      my_scheduler = list_schedulers()[0]

      job_templates = (CondorJobTemplate(name='example',
                                         parameters={'executable': 'my_script.py',
                                                     'condorpy_template_name': 'vanilla_transfer_files',
                                                     'attributes': {'transfer_input_files': ('../input_1', '../input_2'),
                                                                    'transfer_output_files': ('example_output1', example_output2),
                                                                   },
                                                     'scheduler': my_scheduler,
                                                     'remote_input_files': ('$(APP_WORKSPACE)/my_script.py', '$(APP_WORKSPACE)/input_1', '$(USER_WORKSPACE)/input_2'),
                                                    }
                                        ),
                      )

      return job_templates

Job Types
---------
The Jobs API is designed to support multiple job types. The job type defines the way the job is run. The following parameters can be defined for all job types:

    * ``description`` (string): a short description of the job.
    * ``workspace`` (string): a path to a directory that will act as the workspace for the job. Each job type may interact with the workspace differently. By default the workspace is set to the user's workspace in the app that is creating the job.
    * ``extended_properties`` (dict): a dictionary of additional properties.

Specific job types may define additional parameters. Currently there are only two: `BasicJob`_ and `CondorJob`_.

BasicJob
''''''''
The BasicJob type is a sample job type. It has all of the basic properties and methods of a job, but it doesn't have any mechanism for running jobs. It's primary purpose is for demonstration.

CondorJob
'''''''''
The CondorJob type facilitates running jobs on HTCondor using the CondorPy library. The following additional parameters can be defined for the CondorJob type:

    * ``executable`` (string): the file path to the job executable.
    * ``condorpy_template_name`` (string): the name of a template from the CondorPy library pre-configures certain job attributes.
    * ``attributes`` (dict): a dictionary of HTCondor job attributes.
    * ``remote_input_files`` (list of strings): a list of file paths for files that need to be transferred to the remote scheduler to run.
    * ``num_jobs`` (integer): the number of sub-jobs that will be executed as part of the job.
    * ``scheduler`` (Scheduler): a `Scheduler` object that contains the connection information for the remote scheduler where the job will be submitted to. If the ``scheduler`` parameter is not included, or defined as ``None``, then the job will be submitted to the local scheduler if it is configured. For more information about schedulers refer to the :doc:`compute`.

For more information about these parameters see the `CondorPy documentation <http://condorpy.readthedocs.org/en/latest/>`_.

.. note::
    These parameters to create a CondorPy Job object. Most of the CondorJob parameters are called the same as the CondorPy Job arguments that they are used for with a few exceptions:

    * the ``condorpy_template_name`` is used to access retrieve a CondorPy Template. The attributes of the template are combined with the ``attributes`` dict.
    * the ``scheduler`` is used to define the ``host``, ``username``, ``password``, ``private_key``, and ``private_key_pass``, in the CondorPy Job.
    * the ``workspace`` is used to set the CondorPy Job ``working_directory``.

.. important::
    Perhaps the most confusing part about CondorJob parameters is the file paths. Different parameters require that the paths be defined relative to different locations. For more information about how to define paths in CondorJob parameters see the `CondorPy documentation <http://condorpy.readthedocs.org/en/latest/>`_

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
To create a job call the ``create_job`` method on the job manager. The required parameters are ``name``, ``user`` and ``template_name``. Any other job parameters can also be passed in as `kwargs`.

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

.. autoclass:: tethys_sdk.jobs.BasicJobTemplate

.. autoclass:: tethys_sdk.jobs.CondorJobTemplate