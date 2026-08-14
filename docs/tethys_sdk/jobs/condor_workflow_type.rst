.. _tethys_jobs_condor_workflow:

************************
Condor Workflow Job Type
************************

**Last Updated:** January 2022

.. important::

    This feature requires the ``condorpy`` library to be installed. Starting with Tethys 5.0 or if you are using ``micro-tethys-platform``, you will need to install ``condorpy`` using conda or pip as follows:

    .. code-block:: bash

        # conda: conda-forge channel strongly recommended
        conda install -c conda-forge condorpy

        # pip
        pip install condorpy

A Condor Workflow provides a way to run a group of jobs (which can have hierarchical relationships) as a single (Tethys) job. The hierarchical relationships are defined as parent-child relationships. For example, suppose a workflow is defined with three jobs: ``JobA``, ``JobB``, and ``JobC``, which must be run in that order. These jobs would be defined with the following relationships: ``JobA`` is the parent of ``JobB``, and ``JobB`` is the parent of ``JobC``.

.. seealso::
    The Condor Workflow job type uses the CondorPy library to submit jobs to HTCondor compute pools. For more information on CondorPy and HTCondor see the `CondorPy documentation <https://condorpy.readthedocs.io/en/latest/>`_ and specifically the `Overview of HTCondor <https://condorpy.readthedocs.io/en/latest/htcondor.html>`_.

Creating a Condor Workflow
==========================
Creating a Condor Workflow job involves 3 steps:

    1. Create an empty Workflow job from the job manager.
    2. Create the jobs that will make up the workflow with `CondorWorkflowJobNode`
    3. Define the relationships among the nodes


::

    from tethys_sdk.jobs import CondorWorkflowJobNode
    from tethys_sdk.routing import controller
    from .app import App

    job_manager = App.get_job_manager()


    @controller(
        app_workspace=True,
    )
    def some_controller(request, app_workspace):
        workflow = job_manager.create_job(
            name='MyWorkflowABC',
            user=request.user,
            job_type='CONDORWORKFLOW',
            scheduler=app.get_scheduler('condor_primary'),
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

Before a controller returns a response the job must be saved, otherwise, the changes made to the job will be lost (executing the job automatically saves it). If submitting the job takes a long time (e.g. if a large amount of data has to be uploaded to a remote scheduler) then it may be best to use AJAX to execute the job.

.. _tethys_jobs_condor_workflow_reporting:

Status Reporting
================
Rendering a workflow's diagram normally costs the portal one query to the scheduler per node, on every poll, from every viewer watching it. A workflow can instead have its statuses pushed to the portal by something running alongside the scheduler, where the queue is a local query, and then the jobs table and the diagram are served from the database. See :ref:`jobs_api_report_status` for the endpoint itself.

To make that possible, ``CondorWorkflow.execute()`` attaches two ClassAds to the DAGMan job:

.. code-block::

    +TethysJobId = "42"
    +TethysJobToken = "<signed token>"

A reporter reads them off the queue — for example with ``condor_q -long`` — and has everything it needs to POST to ``report-job-status``: the ``TethysJob`` id the DAG belongs to, and a token authorizing reports for that job. The ads are inert on a pool where nothing is reporting, and no change is needed in an app to get them.

The attribute names are available as ``CondorWorkflow.JOB_ID_AD`` and ``CondorWorkflow.JOB_TOKEN_AD``.

Node statuses are keyed by *CondorPy job name*, not the node name as stored in the database. CondorPy builds it by replacing spaces with underscores, so a node named ``Prep Data`` is reported as ``Prep_Data``.

.. warning::

    ``TethysJobToken`` is a bearer credential. HTCondor makes job ClassAds readable to users who can query the scheduler, so on a shared pool anyone able to run ``condor_q -long`` against these jobs can read the token and report status for them — which for a terminal status also triggers the job's results processing. Treat status reporting as trusted only to the extent the pool is. The token also appears in the submit command, so avoid configuring CondorPy's logger at ``INFO`` or below in production, where it would be written to the portal's logs.

.. note::

    A reporter must send node statuses periodically rather than only when they change, or the cached statuses expire and the views resume querying the scheduler per node. See :ref:`jobs_api_report_status_heartbeat`.

API Documentation
=================

.. autoclass:: tethys_compute.models.CondorWorkflow

.. autoclass:: tethys_compute.models.CondorWorkflowNode

.. autoclass:: tethys_compute.models.CondorWorkflowJobNode
