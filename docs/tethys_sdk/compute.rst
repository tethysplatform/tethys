***********
Compute API
***********

**Last Updated:** February 11, 2015

Distributed computing in Tethys Platform is made possible with HTCondor. Portal wide HTCondor computing resources are managed through the :doc:`../tethys_portal/tethys_compute_admin_pages`. Accessing these resources in your app and configuring app specific resources is made possible through the Compute API.

.. seealso::
    For more information on HTCondor see `Overview of HTCondor <http://condorpy.readthedocs.org/en/latest/htcondor.html>`_ or the `HTCondor User Manual <http://research.cs.wisc.edu/htcondor/manual/>`_.

Key Concepts
============
HTCondor is a job and resources management middleware. It can be used to create High-Throughput Computing (HTC) systems from diverse computing units including desktop computers or cloud-computing resources. These HTC systems are known as HTCondor pools or clusters. In Tethys the Python library `TethysCluster <http://www.tethysplatform.org/TethysCluster/>`_ is used to automatically provision HTCondor clusters on Amazon Web Services (AWS) or Microsoft Azure. Portal-wide clusters can be configured by the Tethys Portal admin using the :doc:`../tethys_portal/tethys_compute_admin_pages`, or app-specific clusters can be configured in apps using the `ClusterManager`_. To run jobs to a clusters, it must have a ``Scheduler`` configured. Portal-wide schedulers can also be configured by the Tethys Portal admin using the :doc:`../tethys_portal/tethys_compute_admin_pages`, or app-specific schedulers can be set up through the Compute API.

.. seealso::
    To see how to configure a job with a ``Scheduler`` see the :doc:`jobs`.


.. _ClusterManager:

Working with the Cluster Manager
================================
The cluster manager can be used to create new computing clusters. It is accessed through the ``get_cluster_manager`` function.

::

    from tethys_sdk.compute import get_cluster_manager

    tethyscluster_config_file = '/path/to/TethysCluster/config/file'
    cluster_manager = get_cluster_manager(tethyscluster_config_file)

For more information on how to use the cluster manager see the `TethysCompute documentation <http://tethyscluster.readthedocs.org/en/dev/>`_

Working with Schedulers
=======================
Portal-wide schedulers can be accessed through the ``list_schedulers`` and the ``get_scheduler`` functions.

::

    from tethys_sdk.compute import list_schedulers, get_scheduler

    scheduler = list_schedulers()[0]

    # this assumes the Tethys Portal administrator has created a scheduler named 'Default'.
    scheduler = get_scheduler('Default')

App-specific schedulers can be created with the ``create_scheduler`` function.

::

    from tethys_sdk.compute import create_scheduler
    # For Condor Job
    scheduler = create_scheduler(name='my_app_scheduler', host='example.com', type='condor', username='root', private_key_path='/path/to/private/key')

    # For Dask Job
    scheduler = create_scheduler(name='my_app_scheduler', host='localhost:8786', type='dask', timeout=30, heartbeat_interval=2, dashboard='localhost:8787')

API Documentation
=================

.. autofunction:: tethys_sdk.compute.list_schedulers

.. autofunction:: tethys_sdk.compute.get_scheduler

.. autofunction:: tethys_sdk.compute.create_scheduler

.. autofunction:: tethys_sdk.compute.create_condor_scheduler

.. autofunction:: tethys_sdk.compute.create_dask_scheduler

