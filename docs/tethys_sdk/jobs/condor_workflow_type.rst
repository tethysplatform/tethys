************************
Condor Workflow Job Type
************************

**Last Updated:** March 29, 2016

A Condor Workflow provides a way to run a group of jobs (which can have hierarchical relationships) as a single (Tethys) job. The hierarchical relationships are defined as parent-child relationships. For example, suppose a workflow is defined with three jobs: ``JobA``, ``JobB``, and ``JobC``, which must be run in that order. These jobs would be defined the following relationships: ``JobA`` is the parent of ``JobB``, and ``JobB`` is the parent of ``JobC``. An example of defining these relationships the CondorWorkflowTemplate is show in `Setting up a CondorWorkflowTemplate`_.

.. seealso::
    The CondorJob type uses the CondorPy library to submit jobs to HTCondor compute pools. For more information on CondorPy and HTCondor see the `CondorPy documentation <http://condorpy.readthedocs.org/en/latest/>`_ and specifically the `Overview of HTCondor <http://condorpy.readthedocs.org/en/latest/htcondor.html>`_.


Setting up a CondorWorkflowTemplate
===================================
A CondorWorkflowTemplate requires a list of CondorWorkflowJobTemplates. A CondorWorkflowJobTemplate is similar to a CondorJobTemplate, but it is meant to be part of a CondorWorkflowTemplate rather than a standalone job. Like the CondorJobTemplate a CondorWorkflowJobTemplate requires a CondorJobDescription (see :doc:`condor_job_description`).

::

  from tethys_sdk.jobs import CondorWorkflowTemplate, CondorWorkflowJobTemplate, CondorJobDescription
  from tethys_sdk.compute import list_schedulers

  def job_templates(cls):
      """
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
      job_templates = (CondorWorkflowTemplate(name='',
                                              job_list=[job_a, job_b, job_c],
                                              scheduler=None,
                                              ),
                       )

If the you want to use the same job as both part of a workflow and as a stand alone job then define both and use the same job description:

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
      job_a = CondorWorkflowJobTemplate(name='',
                                        job_description=reusable_job_a_description,
                                        )
      job_b1 = CondorWorkflowJobTemplate(name='',
                                         job_description=reusable_job_a_description,
                                         parents=[job_a]
                                         )
      job_b2 = CondorWorkflowJobTemplate(name='',
                                         job_description=reusable_job_a_description,
                                         parents=[job_a]
                                         )
      job_c = CondorWorkflowJobTemplate(name='',
                                        job_description=reusable_job_a_description,
                                        parents=[job_b1, job_b2]
                                        )
      job_templates = (CondorWorkflowTemplate(name='',
                                              job_list=[job_a, job_b1, job_b2, job_c],
                                              scheduler=None,
                                              ),
                       CondorJobTemplate(name='',
                                         job_description=reusable_job_a_description,
                                         scheduler=None,
                                         ),
                       )
