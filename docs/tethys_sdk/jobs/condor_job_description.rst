**********************
Condor Job Description
**********************

**Last Updated:** March 29, 2016

**DEPRECATED**

Both the :doc:`./condor_job_type` or the :doc:`./condor_workflow_type` facilitate running jobs with HTCondor using the CondorPy library, and both use ``CondorJobDescription`` objects which stores attributes used to initialize the CondorPy job. The ``CondorJobDescription`` accepts as parameters any HTCondor job attributes.

.. note::
    In addition to any HTCondor job attributes, the ``CondorJobDescription`` also accepts a special parameter called ``condorpy_template_name``. This parameter accepts a string naming a CondorPy Template, which is a pre-configured set of HTCondor job attributes. For more information about CondorPy templates and HTCondor job attributes see the `CondorPy documentation <http://condorpy.readthedocs.org/en/latest/>`_.

.. important::
    Perhaps the most confusing part about ``CondorJobDescription`` parameters is the file paths. Different parameters require that the paths be defined relative to different locations. For more information about how to define paths for HTCondor job attributes see the `CondorPy documentation <http://condorpy.readthedocs.org/en/latest/>`_

Setting up a CondorJobDescription
=================================
::

  from tethys_sdk.jobs import CondorJobDescription

  ...

      my_job_description = CondorJobDescription(condorpy_template_name='vanilla_transfer_files',
                                                remote_input_files=('$(APP_WORKSPACE)/my_script.py', '$(APP_WORKSPACE)/input_1', '$(USER_WORKSPACE)/input_2'),
                                                executable='my_script.py',
                                                transfer_input_files=('../input_1', '../input_2'),
                                                transfer_output_files=('example_output1', example_output2),
                                                )

  ...
