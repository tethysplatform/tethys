.. _conda_and_tethys:

*************************
Conda and Tethys Platform
*************************

**Last Updated:** September 2024

This guide provides tips for using `Conda <https://docs.conda.io/en/latest/>`_ effectively in your Tethys environment.

.. _conda_channels:

Conda Channels
==============

All of the dependencies for Tethys Platform are installed from the ``conda-forge`` channel (see: `Conda-Forge <https://conda-forge.org/>`_). We recommend that you install any additional packages that you need for development from ``conda-forge`` as well to ensure compatibility with the dependencies already installed. To do so, provide the ``-c`` option when installing packages:

.. code-block:: bash

    conda install -c conda-forge <package>

Install from Conda-Forge Automatically
--------------------------------------

You may wish to configure your conda environment to automatically install packages from the ``conda-forge`` channel as follows:

.. code-block:: bash

    conda config --add channels conda-forge

This command will add the ``conda-forge`` channel to the top of the channel list, making it the highest priority channel for retrieving packages. To learn more see `Conda User Guide - Manage channels <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-channels.html>`_.

.. _libmamba_solver:

Using the libmamba Solver
=========================

The default solver for Conda is notoriously slow, especially in environments that have a lot of dependencies. Tethys development environments can accumulate dependencies as you install more packages and more apps.

The ``libmamba`` solver is a much more efficient solver for Conda and is recommended when you run into issues where your environment is taking too long to solve or fails to solve (see: `A Faster Solver for Conda: Libmamba <https://www.anaconda.com/blog/a-faster-conda-for-a-growing-community>`_). Follow the steps below to use the ``libmamba`` solver with Tethys Platform.

1. Install ``libmamba`` in base environment:

.. code-block:: bash

    conda update -n base conda
    conda install -n base conda-libmamba-solver

2. Optionally, you may wish to set the ``libmamba`` solver as the default solver:

.. code-block:: bash

    conda config --set solver libmamba

Install Tethys Platform
-----------------------

To install Tethys Platform using the ``libmamba`` solver, run the command with the ``--solver`` option:

.. code-block:: bash

    conda create --solver libmamba -n tethys -c tethysplatform -c conda-forge tethys-platform django=<DJANGO_VERSION>

Alternatively, if you set ``libmamba`` to be the default solver in step 2, run the install command as usual and ``libmamba`` will be used automatically:

.. code-block:: bash

    conda create -n tethys -c tethysplatform -c conda-forge tethys-platform django=<DJANGO_VERSION>


.. important::

    **Django Version**

    As of Tethys 4.3 and above, the version of Django is no longer pinned in the ``tethys-platform`` package. You will need to specify the version of Django that you want to use when creating the environment. This is especially important for production installations, as only the LTS versions of Django recieve bug and security fixes. For development installations, we recommend using the same version of Django that you plan to use in production. For production installations, we recommend using the current LTS version of Django (see: `How to get Django - Supported Versions <https://www.djangoproject.com/download/>`_. Failing to provide the Django version will result in installing the latest version of Django which may not be the LTS version.

Install Packages
----------------

You can also use the ``--solver`` option to install new packages in the Tethys environment. Don't forget to activate the Tethys environment first:

.. code-block:: bash

    conda activate tethys
    conda install --solver libmamba -c conda-forge <package>

App Installation
----------------

The ``tethys install`` command that is used to install apps, also installs dependencies of the app that are listed in its ``install.yml``. The ``tethys install`` command will use the default solver you have configured. So to install app dependencies using the ``libmamba`` solver, set the default solver to be ``libmamba`` (see above) and then run the ``tethys install`` command as usual.
