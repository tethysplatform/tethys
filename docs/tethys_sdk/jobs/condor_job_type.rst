***************
Condor Job Type
***************

**Last Updated:** March 29, 2016

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

Setting up a CondorJobTemplate
==============================
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
                                                transfer_output_files=('example_output1', example_output2),
                                                )

      job_templates = (CondorJobTemplate(name='example',
                                         job_description=my_job_description,
                                         scheduler=my_scheduler,
                                        ),
                      )

      return job_templates