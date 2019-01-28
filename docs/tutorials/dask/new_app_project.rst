**********************
New Tethys App Project
**********************

**Last Updated:** November 2018

1. Setting up the scaffold
==========================

Tethys Platform provides an easy way to create new app projects called a scaffold. The scaffold generates a Tethys app project with the minimum files and the folder structure that is required (see :doc:`../../supplementary/app_project`).

Create a new app using the instructions here: :doc:`../getting_started/new_app_project`. For this tutorial we will be calling our project ``dask_tutorial``, so replace all instances of ``dam_inventory`` with ``dask_tutorial`` in the tutorial.


2. Dask
=======

Documentation for Dask may be found at `<https://dask.org>`_

Dask is a tool for natively scaling and parallelizing python. It can broadly be categorized into dynamic task scheduling, and "big data" collections.

Dask Delayed tasks operate lazily. This means that execution is split onto a separate thread for completion and then return.

Dask Distributed is a tool for managing a medium sized cluster. See `<https://distributed.readthedocs.io/en/latest/>`_
