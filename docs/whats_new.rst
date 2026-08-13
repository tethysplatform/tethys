.. _whats_new:

**********
What's New
**********

**Last Updated:** August 2026

Refer to this article for information about each new release of Tethys Platform.

Release |version|
=================

Reported Job Statuses
---------------------

* Jobs can now have their status reported *to* the portal instead of only being polled for, through a new ``report-job-status`` callback endpoint authorized by a per-job signed token.
* For Condor workflows, reported per-node statuses are persisted, so the jobs table and the workflow diagram can be rendered from the database rather than querying the scheduler once per node on every poll. Where nothing reports, the views read live statuses exactly as before and there is nothing to configure.
* ``CondorWorkflow`` submissions now carry the job's id and report token as ClassAds, so a process running alongside the scheduler can report on a workflow's behalf without any change in an app.

.. note::

    This release adds columns to the jobs tables, one of them on the base job table that every job type shares. Apply migrations (``tethys db migrate``, step 4 of :ref:`update_tethys`) before serving with the new code, or job queries will fail for all job types until you do.

See: :ref:`jobs_api_report_status` and :ref:`tethys_jobs_condor_workflow_reporting`

Job Status Update Throttling
----------------------------

* ``TethysJob._last_status_update`` is now persisted to the database. It was previously held only in memory, so a job instance built fresh for each request always fell back to ``execute_time`` and ``TethysJob.is_time_to_update()`` effectively always returned ``True``.
* As a result ``update_status_interval`` now genuinely limits how often a job's status is refreshed from its source, for **all** job types. Apps that relied on every request refreshing a job's status will now see it refreshed at most once per ``update_status_interval`` (10 seconds by default). Set ``update_status_interval`` on the job if a different rate is needed.

See: :ref:`jobs_api`

Buy Me a Soda
-------------
* Tethys Platform has added a "Buy Me a Soda" button to the documentation, allowing users to support the project financially.
* This is a way for users to contribute to the ongoing development and maintenance of Tethys

See: :ref:`contribute_documentation`

Prior Release Notes
===================

.. toctree::
   :maxdepth: 2

   whats_new/prior_releases