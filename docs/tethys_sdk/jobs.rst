********
Jobs API
********

**Last Updated:** January 29, 2016

The Jobs API provides a way for your app to run asynchronous tasks (meaning that after starting a task you don't have to wait for it to finish before moving on). As an example, you may need to run a model that takes a long time (potentially hours or days) to complete. Using the Jobs API you can create a job that will run the model, and then leave it to run while your app moves on and does other stuff. You can check the job's status at any time, and when the job is done the Jobs API will help retrieve the results.

.. note::
    The real power of the jobs API comes when it is combined with the :doc:`compute`. This make it possible for jobs to be offloaded from the main web server to a scalable computing cluster, which in turn enables very large scale jobs to be processed. This is done through the `CondorJob`_ type.


Key Concepts
============
To facilitate interacting with jobs asynchronously, they are stored in a database. The Jobs API provides a job manager to handle the details of working with the database, and provides a simple interface for creating and retrieving jobs. The first step to creating a job is to define a job template. A job template is like a blue print that describes certain key characteristics about the job, such as the job type. The job manager uses a job template to create a new job that has all of the characteristics there were defined in the template. Once a job has been created from a template it can then be customized with any parameters that are needed for that specific job.


The Jobs API supports various types of jobs, but the primary type, which is used in conjunction with the :doc:`compute`, is the `CondorJob`_ type.

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
                                               'remote_input_files': ('my_script.py', 'input_1', '$(USER_WORKSPACE)/input_2'),
                                              }
                                  ),
                      )

      return job_templates

Note that ``JobTemplate`` and ``JOB_TYPES`` need to be imported through the jobs SDK. A job template takes three arguments:

* ``name``: A string designating the name of the template. This will be used to identify the template in the app controllers.
* ``type``: The name of a Tethys job type. These can be accessed through the ``JOB_TYPES`` dictionary (see `Job Types`_).
* ``parameters``: A dictionary of job parameters. These are parameters that will be the same for all instances of this job template. Additional parameters can be added to a job once it is created from the template (see `Using the Job Manager in your App`_).

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
                                                     'remote_input_files': ('my_script.py', 'input_1', '$(USER_WORKSPACE)/input_2'),
                                                    }
                                        ),
                      )

      return job_templates

.. note::

    In these examples the `CondorJob`_ type is being used which requires a `Scheduler` as a parameter. Schedulers can be listed through the ``list_schedulers`` function in the :doc:`compute`. Schedulers must first be defined through the Tethys Portal admin pages (see :ref:`configuring-schedulers-label`).

Job Types
---------
The job manager handles various job types that enables.

BasicJob
''''''''

CondorJob
'''''''''

Workspaces
----------


.. _job-manager-label:

Job Manager
===========

Using the Job Manager in your App
=================================

API Documentation
=================

.. autoclass:: tethys_compute.job_manager.JobManager

.. autoclass:: tethys_sdk.jobs.JobTemplate

.. autoclass:: tethys_sdk.jobs.BasicJobTemplate

.. autoclass:: tethys_sdk.jobs.CondorJobTemplate