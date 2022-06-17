**********************
New Tethys App Project
**********************

**Last Updated:** May 2022

1. Setting up the scaffold
==========================

Tethys Platform provides an easy way to create new app projects called a scaffold. The scaffold generates a Tethys app project with the minimum files and the folder structure that is required (see :doc:`../../supplementary/app_project`).

Create a new app for this tutorial as follows:

a. Activate the Tethys conda environment:

    .. code-block:: bash

        conda activate tethys

b. Scaffold a new app named ``dask_tutorial``:

    .. code-block:: bash

        tethys scaffold dask_tutorial

c. Install the app in development mode:

    .. code-block:: bash

        cd tethysapp-dask_tutorial
        tethys install -d

d. Start the Tethys development server:

    .. code-block:: bash

        tethys manage start

2. Dask
=======

Documentation for Dask may be found at `<https://dask.org>`_

Dask is a tool for natively scaling and parallelizing python. It can broadly be categorized into dynamic task scheduling, and "big data" collections.

Dask Delayed tasks operate lazily. This means that execution is split onto a separate thread for completion and then return.

Dask Distributed is a tool for managing a medium sized cluster. See `<https://distributed.readthedocs.io/en/latest/>`_
