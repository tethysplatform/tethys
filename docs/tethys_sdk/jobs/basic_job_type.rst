**************
Basic Job Type
**************

**Last Updated:** March 29, 2016

The BasicJob type is a sample job type. It has all of the basic properties and methods of a job, but it doesn't have any mechanism for running jobs. It's primary purpose is for demonstration. There are no additional parameters for the BasicJob type other than the generic job parameters.

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

