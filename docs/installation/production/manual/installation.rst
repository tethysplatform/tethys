.. _production_install_tethys:

***********************
Install Tethys Platform
***********************

**Last Updated:** September 2022

This article will provide an overview of how to install Tethys Portal in a production setup ready to host apps. Currently production installation of Tethys is only supported on Linux. Some parts of these instructions are optimized for Ubuntu, though installation on other Linux distributions will be similar.

Install Miniconda
=================

1. As of version 3.0, Tethys Platform can be installed using `conda <https://docs.conda.io/projects/conda/en/latest/user-guide/install/>`_. We recommend installing `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_ as it provides a minimal installation of conda that is appropriate for servers:

    .. code-block:: bash

        cd /tmp
        wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
        bash ./Miniconda3-latest-Linux-x86_64.sh

2. Read the license and accept when prompted. Install to the default location (:file:`~/miniconda3`) and configure the shell to start on startup.

Install Tethys Platform
=======================

1. Create a new conda environment called ``tethys`` with the ``tethys-platform`` package installed:

    .. code-block:: bash

        conda create -n tethys -c conda-forge -c tethysplatform tethys-platform

2. Activate the ``tethys`` conda environment after it is created:

    .. code-block:: bash

        conda activate tethys

Install Optional Dependencies
=============================

Beginning with Tethys v5.0 or if you are using ``microtethys`` many features of Tethys that require additional dependencies are optional. This allows you to select only the dependencies that you need for the features required in your deployment and maintains a minimal environment size. To the the list of optional features and their required dependencies see :ref:`optional_features`.

1. Gather the list of optional dependencies that you want to include in your portal. Refer to the :ref:`optional_features` documentation and ensure that you have any dependencies that are required by features used by the apps that you will install into your portal.


2. Ensure that your ``tethys`` conda environment is active:

    .. code-block:: bash

        conda activate tethys

3. Install the optional dependencies:

    .. code-block:: bash

        conda install -c conda-forge < DEPENDENCY_1 > < DEPENDENCY_2 > ...

    For example, if the list of optional dependencies you wanted to install was: ``django-session-security``, ``django-axes``, ``django-gravatar2``, ``social-auth-app-django``, ``postgresql``, ``psycopg2``, ``sqlalchemy``, and ``tethys_dataset_services``, then you would install them with the following command:

    .. code-block:: bash

        conda install -c conda-forge django-session-security django-axes django-gravatar2 social-auth-app-django postgresql psycopg2 "sqlalchemy<2" tethys_dataset_services

.. tip::

    To simplify the process of installing ``tethys-platform`` and any optional dependencies, consider creating a conda environment YAML file (:file:`environment.yml`) for your portal. For example:

    .. code-block:: yaml

        name: tethys

        channels:
        - conda-forge

        dependencies:
        - tethys-platform
        - django-session-security
        - django-axes
        - django-gravatar2
        - social-auth-app-django
        - postgresql
        - psycopg2
        - sqlalchemy<2
        - tethys_dataset_services

    Use the following command to create your environment from an environment YAML file:

    .. code-block:: bash

        conda env create -f environment.yml
