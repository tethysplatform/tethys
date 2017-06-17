************************
Condor Workflow Job Type
************************

**Last Updated:** March 29, 2016

A Condor Workflow provides a way to run a group of jobs (which can have hierarchical relationships) as a single (Tethys) job. The hierarchical relationships are defined as parent-child relationships. For example, suppose a workflow is defined with three jobs: ``JobA``, ``JobB``, and ``JobC``, which must be run in that order. These jobs would be defined with the following relationships: ``JobA`` is the parent of ``JobB``, and ``JobB`` is the parent of ``JobC``.

.. seealso::
    The Condor Workflow job type uses the CondorPy library to submit jobs to HTCondor compute pools. For more information on CondorPy and HTCondor see the `CondorPy documentation <http://condorpy.readthedocs.org/en/latest/>`_ and specifically the `Overview of HTCondor <http://condorpy.readthedocs.org/en/latest/htcondor.html>`_.

Setting up a CondorWorkflowTemplate
===================================
Creating a `CondorWorkflowTemplate` involves 3 steps:

    1. Define job descriptions for each of the sub-jobs using `CondorJobDescription` (see :doc:`condor_job_description`).
    2. Create the sub-jobs and define relationships using `CondorWorkflowJobTemplate`.
    3. Create the `CondorWorkflowTemplate`.

.. note::
    The `CondorWorkflowJobTemplate` is similar to a `CondorJobTemplate` in that it represents a single HTCondor job and requires a `CondorJobDescription` to define the attributes of that job. However, unlike a `CondorJobTemplate` a `CondorWorkflowJobTemplate` cannot be run independently; it can only be part of a `CondorWorkflowTemplate`. Also, note that the `CondorWorkflowJobTemplate` has a `parents` parameter, which is used to define relationships between jobs.

The following code sample demonstrates how to set up a `CondorWorkflowTemplate`:

::

      Example job_templates method with a CondorWorkflow type.
      """

      job_a_description = CondorJobDescription(condorpy_template_name='vanilla_transfer_files',
                                               remote_input_files=('$(APP_WORKSPACE)/my_script.py', '$(APP_WORKSPACE)/input_1', '$(USER_WORKSPACE)/input_2'),
                                               executable='my_script.py',
                                               transfer_input_files=('../input_1', '../input_2'),
                                               transfer_output_files=('example_output1', example_output2),
                                               )
      job_b_description = CondorJobDescription(condorpy_template_name='vanilla_transfer_files',
                                               remote_input_files=('$(APP_WORKSPACE)/my_script.py', '$(APP_WORKSPACE)/input_1', '$(USER_WORKSPACE)/input_2'),
                                               executable='my_script.py',
                                               transfer_input_files=('../input_1', '../input_2'),
                                               transfer_output_files=('example_output1', example_output2),
                                               )
      job_c_description = CondorJobDescription(condorpy_template_name='vanilla_transfer_files',
                                               remote_input_files=('$(APP_WORKSPACE)/my_script.py', '$(APP_WORKSPACE)/input_1', '$(USER_WORKSPACE)/input_2'),
                                               executable='my_script.py',
                                               transfer_input_files=('../input_1', '../input_2'),
                                               transfer_output_files=('example_output1', example_output2),
                                               )
      job_a = CondorWorkflowJobTemplate(name='JobA',
                                        job_description=job_a_description,
                                        )
      job_b = CondorWorkflowJobTemplate(name='JobB',
                                        job_description=job_b_description,
                                        parents=[job_a]
                                        )
      job_c = CondorWorkflowJobTemplate(name='JobC',
                                        job_description=job_c_description,
                                        parents=[job_b]
                                        )
      job_templates = (CondorWorkflowTemplate(name='WorkflowABC',
                                              job_list=[job_a, job_b, job_c],
                                              scheduler=None,
                                              ),
                       )

If the you want to use the same job both as part of a workflow and as a stand alone job then use the same job description in setting up the `CondorJobTemplate` and the `CondorWorkflowJobTemplate`. This process is demonstrated below:


::

  from tethys_sdk.jobs import CondorJobTemplate, CondorWorkflowTemplate, CondorWorkflowJobTemplate, CondorJobDescription
  from tethys_sdk.compute import list_schedulers

  def job_templates(cls):
      """
      Example job_templates method with a CondorWorkflow type.
      """

      reusable_job_a_description = CondorJobDescription(condorpy_template_name='vanilla_transfer_files',
                                                        remote_input_files=('$(APP_WORKSPACE)/my_script.py', '$(APP_WORKSPACE)/input_1', '$(USER_WORKSPACE)/input_2'),
                                                        executable='my_script.py',
                                                        transfer_input_files=('../input_1', '../input_2'),
                                                        transfer_output_files=('example_output1', example_output2),
                                                        )
      job_b1_description = CondorJobDescription(condorpy_template_name='vanilla_transfer_files',
                                                remote_input_files=('$(APP_WORKSPACE)/my_script.py', '$(APP_WORKSPACE)/input_1', '$(USER_WORKSPACE)/input_2'),
                                                executable='my_script.py',
                                                transfer_input_files=('../input_1', '../input_2'),
                                                transfer_output_files=('example_output1', example_output2),
                                                )
      job_b2_description = CondorJobDescription(condorpy_template_name='vanilla_transfer_files',
                                                remote_input_files=('$(APP_WORKSPACE)/my_script.py', '$(APP_WORKSPACE)/input_1', '$(USER_WORKSPACE)/input_2'),
                                                executable='my_script.py',
                                                transfer_input_files=('../input_1', '../input_2'),
                                                transfer_output_files=('example_output1', example_output2),
                                                )
      job_c_description = CondorJobDescription(condorpy_template_name='vanilla_transfer_files',
                                               remote_input_files=('$(APP_WORKSPACE)/my_script.py', '$(APP_WORKSPACE)/input_1', '$(USER_WORKSPACE)/input_2'),
                                               executable='my_script.py',
                                               transfer_input_files=('../input_1', '../input_2'),
                                               transfer_output_files=('example_output1', example_output2),
                                               )
      job_a = CondorWorkflowJobTemplate(name='JobA',
                                        job_description=reusable_job_a_description,
                                        )
      job_b1 = CondorWorkflowJobTemplate(name='JobB1',
                                         job_description=reusable_job_a_description,
                                         parents=[job_a]
                                         )
      job_b2 = CondorWorkflowJobTemplate(name='JobB2',
                                         job_description=reusable_job_a_description,
                                         parents=[job_a]
                                         )
      job_c = CondorWorkflowJobTemplate(name='JobC',
                                        job_description=reusable_job_a_description,
                                        parents=[job_b1, job_b2]
                                        )
      job_templates = (CondorWorkflowTemplate(name='DiamondWorkflow',
                                              job_list=[job_a, job_b1, job_b2, job_c],
                                              scheduler=None,
                                              ),
                       CondorJobTemplate(name='JobAStandAlone',
                                         job_description=reusable_job_a_description,
                                         scheduler=None,
                                         ),
                       )


Creating and Customizing a Job
==============================
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

API Documentation
=================

.. autoclass:: tethys_sdk.jobs.CondorWorkflowTemplate

.. autoclass:: tethys_sdk.jobs.CondorWorkflowJobTemplate

.. autoclass:: tethys_compute.models.CondorWorkflow

.. autoclass:: tethys_compute.models.CondorWorkflowJobNode