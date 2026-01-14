**********************
New Tethys App Project
**********************

**Last Updated:** August 2024

1. Generate Scaffold
====================

Tethys Platform provides an easy way to create new app projects called a scaffold. The scaffold generates a Tethys app project with the minimum files and the folder structure that is required (see :doc:`../../supplementary/app_project`).

Create a new app for this tutorial as follows:

a. :ref:`activate_environment`

b. Scaffold a new app named ``dask_tutorial``:

    .. code-block:: bash

        tethys scaffold dask_tutorial

2. Add App Dependencies to :file:`install.yml`
==============================================

App dependencies should be managed using the :file:`install.yml` instead of the :file:`setup.py`. This app will require the ``dask`` and ``tethys_dask_scheduler`` packages. Both packages are available on ``conda-forge``, which is the preferred Conda channel for Tethys. Open :file:`tethysapp-dask_tutorial/install.yml` and add these dependencies to the ``requirements.conda`` section of the file:

.. code-block:: yaml

    # This file should be committed to your app code.
    version: 1.0
    # This should match the app - package name in your setup.py
    name: dask_tutorial

    requirements:
      # Putting in a skip true param will skip the entire section. Ignoring the option will assume it be set to False
      skip: false
      conda:
        channels:
          - conda-forge
        packages:
          - dask
          - tethys_dask_scheduler

      pip:

    post:

3. Development Installation
===========================

Install the app and it's dependencies into your development Tethys Portal. In a terminal, change into the :file:`tethysapp-dask_tutorial` directory and execute the :command:`tethys install -d` command.

.. code-block:: bash

    cd tethysapp-dask_tutorial
    tethys install -d

5. View Your New App
====================

1. Start up the development server to view the new app:

.. code-block:: bash

    tethys manage start

.. tip::

    To stop the development server press :kbd:`CTRL-C`.

2. Browse to `<http://127.0.0.1:8000/apps/>`_ in a web browser and login. The default portal user is:

* **username**: admin
* **password**: pass

6. Dask
=======

Documentation for Dask may be found at `<https://www.dask.org/>`_

Dask is a tool for natively scaling and parallelizing python. It can broadly be categorized into dynamic task scheduling, and "big data" collections.

Dask Delayed tasks operate lazily. This means that execution is split onto a separate thread for completion and then return.

Dask Distributed is a tool for managing a medium sized cluster. See `<https://distributed.dask.org/en/latest/>`_
