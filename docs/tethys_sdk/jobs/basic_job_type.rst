**************
Basic Job Type
**************

**Last Updated:** March 29, 2016

The Basic Job type is a sample job type for creating dummy jobs. It has all of the basic properties and methods of a job, but it doesn't have any mechanism for running jobs. It's primary purpose is for demonstration. There are no additional attributes for the BasicJob type other than the common set of job attributes. The only required parameter for the `BasicJobTemplate` class is ``name``, but it also supports passing in other job attributes as additional arguments.

Setting up a BasicJobTemplate
=============================
::

  from tethys_sdk.jobs import BasicJobTemplate

  def job_templates(cls):
      """
      Example job_templates method with a BasicJob type.
      """

      job_templates = (BasicJobTemplate(name='example',
                                        description='This is a sample basic job. It can't actually compute anything.',
                                        extended_properties={'app_spcific_property': 'default_value',
                                                             'persistent_store_id': None,  # Will be defined when job is created
                                                             }
                                        ),
                      )

      return job_templates

Creating and Customizing a Job
==============================
To create a job call the ``create_job`` method on the job manager. The required parameters are ``name``, ``user`` and ``template_name``. Any other job attributes can also be passed in as `kwargs`.

::

    # create a new job
    job = job_manager.create_job(name='unique_job_name', user=request.user, template_name='example', description='my first job')

Before a controller returns a response the job must be saved or else all of the changes made to the job will be lost (executing the job automatically saves it). If submitting the job takes a long time (e.g. if a large amount of data has to be uploaded to a remote scheduler) then it may be best to use AJAX to execute the job.

API Documentation
=================

.. autoclass:: tethys_sdk.jobs.BasicJobTemplate

.. autoclass:: tethys_compute.models.BasicJob