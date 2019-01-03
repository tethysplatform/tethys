************************
Condor Workflow Job Type
************************

**Last Updated:** December 27, 2018

A Condor Workflow provides a way to run a group of jobs (which can have hierarchical relationships) as a single (Tethys) job. The hierarchical relationships are defined as parent-child relationships. For example, suppose a workflow is defined with three jobs: ``JobA``, ``JobB``, and ``JobC``, which must be run in that order. These jobs would be defined with the following relationships: ``JobA`` is the parent of ``JobB``, and ``JobB`` is the parent of ``JobC``.

.. seealso::
    The Condor Workflow job type uses the CondorPy library to submit jobs to HTCondor compute pools. For more information on CondorPy and HTCondor see the `CondorPy documentation <http://condorpy.readthedocs.org/en/latest/>`_ and specifically the `Overview of HTCondor <http://condorpy.readthedocs.org/en/latest/htcondor.html>`_.

Creating a Condor Workflow
==========================
Creating a Condor Workflow job involves 3 steps:

    1. Create an empty Workflow job from the job manager.
    2. Create the jobs that will make up the workflow with `CondorWorkflowJobNode`
    3. Define the relationships among the nodes


::

    from tethys_sdk.jobs import CondorWorkflowJobNode
    from .app import MyApp as app

    def some_controller(request):

        # get the path to the app workspace to reference job files
        app_workspace = app.get_app_workspace().path

        workflow = job_manager.create_job(
            name='MyWorkflowABC',
            user=request.user,
            job_type='CONDORWORKFLOW',
            scheduler=None,
        )
        workflow.save()

        job_a = CondorWorkflowJobNode(
            name='JobA',
            workflow=workflow,
            condorpy_template_name='vanilla_transfer_files',
            remote_input_files=(
                os.path.join(app_workspace, 'my_script.py'),
                os.path.join(app_workspace, 'input_1'),
                os.path.join(app_workspace, 'input_2')
            ),
            attributes=dict(
                executable='my_script.py',
                transfer_input_files=('../input_1', '../input_2'),
                transfer_output_files=('example_output1', 'example_output2'),
            )
        )
        job_a.save()

        job_b = CondorWorkflowJobNode(
            name='JobB',
            workflow=workflow,
            condorpy_template_name='vanilla_transfer_files',
            remote_input_files=(
                os.path.join(app_workspace, 'my_script.py'),
                os.path.join(app_workspace, 'input_1'),
                os.path.join(app_workspace, 'input_2')
            ),
            attributes=dict(
                executable='my_script.py',
                transfer_input_files=('../input_1', '../input_2'),
                transfer_output_files=('example_output1', 'example_output2'),
            ),
        )
        job_b.save()

        job_c = CondorWorkflowJobNode(
            name='JobC',
            workflow=workflow,
            condorpy_template_name='vanilla_transfer_files',
            remote_input_files=(
                os.path.join(app_workspace, 'my_script.py'),
                os.path.join(app_workspace, 'input_1'),
                os.path.join(app_workspace, 'input_2')
            ),
            attributes=dict(
                executable='my_script.py',
                transfer_input_files=('../input_1', '../input_2'),
                transfer_output_files=('example_output1', 'example_output2'),
            ),
        )
        job_c.save()

        job_b.add_parent(job_a)
        job_c.add_parent(job_b)

        workflow.save()
        # or
        workflow.execute()

.. note::

    The `CondorWorkflow` object must be saved before the `CondorWorkflowJobNode` objects can be instantiated, and the `CondorWorkflowJobNode` objects must be saved before you can define the relationships.

Before a controller returns a response the job must be saved or else all of the changes made to the job will be lost (executing the job automatically saves it). If submitting the job takes a long time (e.g. if a large amount of data has to be uploaded to a remote scheduler) then it may be best to use AJAX to execute the job.

API Documentation
=================

.. autoclass:: tethys_compute.models.CondorWorkflow

.. autoclass:: tethys_compute.models.CondorWorkflowNode

.. autoclass:: tethys_compute.models.CondorWorkflowJobNode

.. autoclass:: tethys_sdk.jobs.CondorWorkflowTemplate

.. autoclass:: tethys_sdk.jobs.CondorWorkflowJobTemplate