*********************
App Project Structure
*********************


**Last Updated:** May 20, 2014

The source code for a Tethys App project is contained in a series of Python packages. :ref:`app-figure-1` illustrates the key components of a Tethys App project for an app called "myapp". The top level package is called the :term:`release package` and it contains the :term:`app package` for the app and other files that are needed to distribute the app.The key components of the :term:`release package` and the :term:`app package` will be explained in this article.  

.. _app-figure-1:

.. figure:: ../images/app_package.png
	:alt: diagram of a Tethys App project for an app named myapp

	**Figure 1. An example of a Tethys App project for an app named "myapp".**  

Release Package
===============

As the name suggests, the release package is the package that you will use to release and develop your app. The entire :term:`release package` should be provided when you release your app.The name of a :term:`release package` follows a specific naming convention.The name of the directory should always start with "ckanapp-" followed by a *unique* name for the app. The name of the app may not have spaces, dashes, or other special characters (however, underscores are allowed). For example, :ref:`app-figure-1` shows the project structure for an app with name "myapp"; thus, the name of the :term:`release package` is "ckanapp-myapp". The name of your app should be unique with any other apps running on a CKAN instance to avoid conflicts. 

The release package must contain a setup script (:file:`setup.py`) and :file:`ckanapp` package at a minimum. This directory would also be a good place to put any accessory files for the app such as a readme file or the license file. Nothing that is required for the app to run should be stored in this directory. The setup script is used during installation of the app to install any dependencies of your app and make Python aware of the modules in your app project. A basic setup script is generated as part of the scaffolding for a new app project. For more information on writing setup scripts refer to this article: `Writing the Setup Script <http://docs.python.org/2/distutils/setupscript.html>`_.

The :file:`ckanapp` package is a `Python namespace <http://docs.python.org/2/tutorial/classes.html#python-scopes-and-namespaces>`_ package. It provides a way to mimic the production environment during development of the app (i.e.: when the app is installed, it will reside in a namespace package called :file:`ckanapp`). This package contains the :term:`app package`, which has the same name as your app name by convention.

.. caution::

	When you generate a new app project using the command line tool, you will notice that many of the directories contain a :file:`\_\_init\_\_.py` file, many of which are empty. These are omitted in the diagram for simplicity. DO NOT DELETE THE :file:`\_\_init\_\_.py` FILES. These files indicate to Python that the directories that contains them are `Python packages <http://docs.python.org/2/tutorial/modules.html#packages>`_. Your app will not work properly without the :file:`\_\_init\_\_.py` files.  

The App Package
===============

The :term:`app package` contains all of the source code and resources that are needed by the Tethys Apps plugin to run your app. When your app is installed, the :term:`app package` will be copied into the :file:`ckanapp` package of the Tethys Apps plugin. As discussed in the :doc:`./app_harvesting` section, all:term:`app packages` contained in the :file:`ckanapp` package of the Tethys Apps plugin will be loaded as apps when CKAN is loaded.

The :term:`app package` contains several files, packages, and directories including: :file:`app.py`, :file:`model.py`, :file:`controllers`, :file:`templates`, and :file:`public`. The :file:`model.py`, :file:`templates`, and :file:`controllers` file and packages correspond with the Model View Controller approach that is used to build apps. The data structures, classes, and methods that are used to interact with the data of the app are contained in the :file:`model.py` file. The :file:`templates` directory contains all the Jinja2 HTML templates that are used to generate the views of the app and the :file:`controllers` package contains Python files for each controller of the app. The :file:`public` directory is used for static resources such as images, JavaScript and CSS files. The :file:`app.py` file contains all the configuration parameters for the app. Each of these components will be discussed in more detail on the following pages.

Naming Conventions
==================

There are a few naming conventions that need to be followed to avoid conflicts with other apps. The more obvious one is the :term:`app package` name. All :term:`app package` names must be unique. The other important naming convention is related to the public and template directories. Follow the suggested structure shown in :ref:`app-figure-1` for public and template directories. Nest all documents that are in these directories inside a directory with the same name as your :term:`app package`. This ensures that when your app calls for :file:`index.html` it finds the correct one and not an :file:`index.html` from another app.
