***************
Condor Job Type
***************

**Last Updated:** December 27, 2018


The :doc:`condor_job_type` (and :doc:`condor_workflow_type`) enable the real power of the jobs API by combining it with the :doc:`../compute`. This make it possible for jobs to be offloaded from the main web server to a scalable computing cluster, which in turn enables very large scale jobs to be processed.

.. seealso::
    The Condor Job and the Condor Workflow job types use the CondorPy library to submit jobs to HTCondor compute pools. For more information on CondorPy and HTCondor see the `CondorPy documentation <http://condorpy.readthedocs.org/en/latest/>`_ and specifically the `Overview of HTCondor <http://condorpy.readthedocs.org/en/latest/htcondor.html>`_.


Creating a Condor Job
=====================
To create a job call the ``create_job`` method on the job manager. The required parameters are ``name``, ``user`` and ``job_type``. Any other job attributes can also be passed in as `kwargs`.

::

    from tethys_sdk.compute import list_schedulers
    from .app import MyApp as app

    def some_controller(request):

        # get the path to the app workspace to reference job files
        app_workspace = app.get_app_workspace().path

        # create a new job from the job manager
        job = job_manager.create_job(
            name='myjob_{id}',  # required
            user=request.user,  # required
            job_type='CONDOR',  # required

            # any other properties can be passed in as kwargs
            attributes=dict(
                transfer_input_files=('../input_1', '../input_2'),
                transfer_output_files=('example_output1', example_output2),
            ),
            condorpy_template_name='vanilla_transfer_files',
            remote_input_files=(
                os.path.join(app_workspace, 'my_script.py'),
                os.path.join(app_workspace, 'input_1'),
                os.path.join(app_workspace, 'input_2')
            )
        )

        # properties can also be added after the job is created
        job.extended_properties = {'one': 1, 'two': 2}

        # each job type may provided methods to further specify the job
        job.set_attribute('executable', 'my_script.py')

        # get a scheduler for the job
        my_scheduler = list_schedulers()[0]
        job.scheduler = my_scheduler

        # save or execute the job
        job.save()
        # or
        job.execute()

Before a controller returns a response the job must be saved or else all of the changes made to the job will be lost (executing the job automatically saves it). If submitting the job takes a long time (e.g. if a large amount of data has to be uploaded to a remote scheduler) then it may be best to use AJAX to execute the job.

API Documentation
=================

.. autoclass:: tethys_compute.models.CondorJob

.. autoclass:: tethys_sdk.jobs.CondorJobTemplate