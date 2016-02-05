***********
Compute API
***********

**Last Updated:** September 3, 2015

Distributed computing in Tethys Platform is made possible with HTCondor. HTCondor computing resources are managed through the :doc:`../tethys_portal/admin_pages`. Access to these resources is made possible to app developers through the Compute API and the :doc:`jobs`.

.. seealso::
    For more information on HTCondor see `Overview of HTCondor <http://condorpy.readthedocs.org/en/latest/htcondor.html>`_ or the `HTCondor User Manual <http://research.cs.wisc.edu/htcondor/manual/>`_.

Key Concepts
============


.. _configuring-schedulers-label:

Configuring Schedulers
======================


Working with Schedulers
=======================


API Documentation
=================


.. autofunction:: tethys_sdk.compute.list_schedulers

.. autofunction:: tethys_sdk.compute.get_scheduler