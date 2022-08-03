.. _development_installation:

***************
Getting Started
***************

**Last Updated:** June 2022

This section describes how to get Tethys Platform up and running as a fresh installation for app development. If you are upgrading an existing installation then refer to the :ref:`update_tethys` docs. If you are deploying a production instance of Tethys Portal refer to the :ref:`production_installation` docs. If you want to contribute to the Tethys Platform source code itself then refer to the :ref:`developer_installation` docs.

Prerequisites
-------------

Tethys Platform requires the `conda packaging system <https://docs.conda.io/en/latest/index.html>`_. If you do not already have an installation of ``Miniconda`` (or ``Anaconda``) then refer to their `documentation <https://docs.conda.io/en/latest/miniconda.html>`_ for installation instructions.

Also, be sure that the system you are using meets the minimum :ref:`system_reqs`.


1. Install the ``tethys-platform`` Conda Package
------------------------------------------------

a. To install the ``tethys-platform`` into a new conda environment then run the following commands:

.. code-block:: bash

    conda create -n tethys -c tethysplatform -c conda-forge tethys-platform

.. tip::

    If conda is taking too long to solve the Tethys environment, try using the [experimental libmamba solver](https://www.anaconda.com/blog/a-faster-conda-for-a-growing-community):

    .. code-block:: bash
    
        conda update -n base conda
    
    .. code-block:: bash

        conda install -n base conda-libmamba-solver

    .. code-block:: bash

        conda create --experimental-solver libmamba -n tethys -c tethysplatform -c conda-forge tethys-platform


.. note::

    To install the latest development build of ``tethys-platform`` add the ``tethys/label/dev`` channel to the list of conda channels::

        conda create -n tethys -c tethysplatform/label/dev -c tethysplatform -c conda-forge tethys-platform


    Alternatively, to install from source refer to the :ref:`developer_installation` docs.

2. Activate the Tethys Conda Environment
----------------------------------------

Anytime you want to work with Tethys Platform, you'll need to activate the ``tethys`` Conda environment. You will know the ``tethys`` environment is active when ``(tethys)`` is displayed to the left of the terminal prompt. Activate the ``tethys`` environment now as follows:

.. code-block:: bash

    conda activate tethys

3. Create a :file:`portal_config.yml` File
------------------------------------------

To add custom configurations such as the database and other local settings you will need to generate a :file:`portal_config.yml` file. To generate a new template :file:`portal_config.yml` run::

    tethys gen portal_config

You can customize your settings in the :file:`portal_config.yml` file after you generate it by manually editing the file or by using the :ref:`tethys_settings_cmd` command. Refer to the :ref:`tethys_configuration` documentation for more information.


4. Configure the Tethys Database
--------------------------------

Tethys Platform requires a PostgreSQL database server. There are several options for setting up a DB server: local, docker, or dedicated. For development environments you can use Tethys to create a local server::

    tethys db configure

.. note::

    The tethys db command (:ref:`tethys_db_cmd`) will create a local database server in the directory specified by the ``DIR`` setting in the ``DATABASES`` section of the :file:`portal_config.yml` file. If the value of ``DIR`` is a relative path then the database server will be created relative to directory specified by the ``TETHYS_HOME`` environment variable. By default ``TETHYS_HOME`` is at `~/.tethys`.

    As an alternative to creating a local database server you can also configure a Docker DB server (see :ref:`using_docker`). A local database server is only recommended for development environments. For production environments please refer to :ref:`production_installation`.

5. Start the Development Server
-------------------------------

Once you have a database successfully configured you can run the Tethys development server::

    tethys manage start

This will start up a locally running web server. You can access the Tethys Portal by going to `<http://localhost:8000>`_ in your browser.

.. tip::

    You can customize the port that the server is running on by adding the ``-p`` option.

    ::

        tethys manage start -p 8001

    See :ref:`tethys_manage_cmd` for more details.

6. Next Steps
-------------

There are several directions that you may want to go from here.

* Install an app you have already developed using the :ref:`app_installation` guide.
* Complete one or more :ref:`tutorials` to learn how to develop apps using Tethys Platform.
* Install one or both of the :ref:`installation_showcase_apps` to see live demos and code examples of Gizmos and Layouts.
* Checkout the :doc:`./installation/web_admin_setup` docs to customize your Tethys Portal.
* For help getting started with docker see :ref:`using_docker`


Related Docs
------------

.. toctree::
    :maxdepth: 1

    installation/system_requirements
    tethys_portal/configuration
    installation/application
    installation/showcase_apps
    installation/update
    installation/production
    installation/developer_installation
    installation/using_docker
    installation/web_admin_setup
