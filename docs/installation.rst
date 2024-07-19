.. _development_installation:

***************
Getting Started
***************

**Last Updated:** June 2024

Here is the quickest way to get started with Tethys Platform:

.. code-block:: bash

    conda create -n tethys -c conda-forge micro-tethys-platform
    conda activate tethys
    tethys quickstart

.. note::
    The prerequisites for the above are that you:
    * Meet the minimum :ref:`system_reqs`.
    * Have an existing installation of `Miniconda <https://docs.anaconda.com/miniconda/miniconda-install/>`_ or `Anaconda <https://docs.anaconda.com/anaconda/install/>`_.

Now open your browser to http://127.0.0.1:8000/ and log in with:

|
| **username**: admin
| **password**: pass
|

.. figure:: images/getting_started/hello_world_login.png
    :width: 600px
    :align: center

Voilá! Your very own Hello World application!

.. figure:: images/getting_started/hello_world_app.png
    :width: 600px
    :align: center

Time to develop! The code behind your Hello World app can be found at ``<YOUR_USER_HOME_FOLDER>/.tethys/apps/tethysapp-hello_world``.

Next Steps
----------

There are several directions that you may want to go from here.

* Install an app you have already developed using the :ref:`app_installation` guide.
* Complete one or more :ref:`tutorials` to learn how to develop apps using Tethys Platform.
* Install one or both of the :ref:`installation_showcase_apps` to see live demos and code examples of Gizmos and Layouts.
* Checkout the :doc:`./installation/web_admin_setup` docs to customize your Tethys Portal.
* For help getting started with docker see :ref:`using_docker`
