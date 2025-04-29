.. _index:

*************************
Tethys Platform |version|
*************************

**Last Updated:** April 2025

Tethys is a platform that can be used to develop and host geoscientific web apps. It includes a suite of free and open source software (FOSS) that has been carefully selected to address the unique development needs of geoscientific web apps. Tethys web apps are developed using a Python software development kit (SDK) which includes programmatic links to each software component. Tethys Platform is powered by the Django Python web framework giving it a solid web foundation with excellent security and performance. Refer to the :doc:`./features` article for an overview of the features of Tethys Platform.

.. important::

    Tethys Platform |version| has arrived! Check out the :doc:`./whats_new` article for a description of the new features and changes.

.. _quickstart:

Quick Start
===========

First create a :ref:`virtual_environment` with the tool of your choice and then run the following commands:

|

.. tabs::

    .. tab:: Conda

        .. code-block:: bash

            conda install -c conda-forge tethys-platform
            tethys quickstart

    .. tab:: Pip

        .. code-block:: bash

            pip install tethys-platform
            tethys quickstart

.. tip::
    
    To learn what goes on behind the scenes during ``tethys quickstart`` see :ref:`development_installation`.
    
Your browser will automatically open to http://127.0.0.1:8000/. 

.. figure:: images/getting_started/hello_world_login.png
    :width: 600px
    :align: center

.. admonition:: Log in with:

   **Username**: admin
   
   **Password**: pass

Voilá! Your very own Hello World application!

.. figure:: images/getting_started/hello_world_app.png
    :width: 600px
    :align: center

Time to develop! The code behind your Hello World app can be found in your current working directory in the newly-created ``tethysapp-hello_world`` folder.

Next Steps
----------

There are several directions that you may want to go from here.

* Install an app you have already developed using the :ref:`app_installation` guide.
* Complete one or more :ref:`tutorials` to learn how to develop apps using Tethys Platform.
* Install one or both of the :ref:`installation_showcase_apps` to see live demos and code examples of Gizmos and Layouts.
* Checkout the :doc:`./installation/web_admin_setup` docs to customize your Tethys Portal.
* For help getting started with docker see :ref:`using_docker`

Acknowledgements
================

This material is based upon work supported by the National Science Foundation under Grant No. 1135482

.. toctree::
   :maxdepth: 1
   :hidden:
   
   Quick Start <self>

.. toctree::
   :maxdepth: 2
   :hidden:

   tutorials
   recipes
   dev_guides

.. toctree::
   :maxdepth: 1
   :hidden:

   tethys_development

.. toctree::
   :maxdepth: 3
   :hidden:

   installation/production

.. toctree::
   :maxdepth: 1
   :hidden:

   whats_new
   installation/update
