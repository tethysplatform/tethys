********
Jobs API
********

**Last Updated:** September 3, 2015

- intro to jobs api
- allows you to define and submit jobs in an app
- condor jobs a run using the compute clusters

.. _job-manager-label:

Job Manager
===========


Defining Job Templates
----------------------
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

    In these examples the ``CondorJob`` type is being used which requires a ``Scheduler`` as a parameter. Schedulers can be listed through the ``list_schedulers`` function in the compute SDK. Schedulers must first be defined through the Tethys Portal admin pages (see `Schedulers <./compute.html#schedulers>`_ in the :doc:`compute`).

Job Types
.........
The job manager handles various job types that enables.

BasicJob
''''''''

CondorJob
'''''''''

Workspaces
..........

Using the Job Manager in your App
---------------------------------

API Documentation
=================

.. autoclass:: tethys_sdk.jobs.JobManager

.. autoclass:: tethys_sdk.jobs.JobTemplate

.. autoclass:: tethys_sdk.jobs.BasicJobTemplate

.. autoclass:: tethys_sdk.jobs.CondorJobTemplate