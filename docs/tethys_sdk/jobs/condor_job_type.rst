***************
Condor Job Type
***************

**Last Updated:** March 29, 2016



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

.. autoclass:: tethys_sdk.jobs.CondorJobTemplate

.. autoclass:: tethys_compute.models.CondorJob