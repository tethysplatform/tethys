.. _app_project_structure:

*********************
App Project Structure
*********************


**Last Updated:** November 17, 2014

The source code for a Tethys app project is organized in a specific file structure. Figure 1 illustrates the key components of a Tethys app project called "my_first_app". The top level package is called the :term:`release package` and it contains the :term:`app package` for the app and other files that are needed to distribute the app. The key components of the :term:`release package` and the :term:`app package` will be explained in this article.

.. figure:: ../images/app_package_django.png
	:alt: diagram of a Tethys app project for an app named my_first_app

	**Figure 1. An example of a Tethys app project for an app named "my_first_app".**

Release Package
===============

As the name suggests, the release package is the package that you will use to release and develop your app. The entire :term:`release package` should be provided when you share your app with others.

The name of a :term:`release package` follows a specific naming convention.The name of the directory should always start with "tethysapp-" followed by a *unique* name for the app. The name of the app may not have spaces, dashes, or other special characters (however, underscores are allowed). For example, Figure 1 shows the project structure for an app with name "my_first_app" and the name of the :term:`release package` is "tethysapp-my_first_app".

The release package must contain a setup script (:file:`setup.py`) and :file:`tethysapp` namespace package at a minimum. This directory would also be a good place to put any accessory files for the app such as a README file or LICENSE file. No code that is required by the app to run should be in this directory.

The setup script to install your app and its dependencies. A basic setup script is generated as part of the scaffolding for a new app project. For more information on writing setup scripts refer to this article: `Writing the Setup Script <https://setuptools.pypa.io/en/latest/userguide/quickstart.html>`_.

The :file:`tethysapp` package is a `Python namespace <https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces>`_ package. It provides a way to mimic the production environment during development of the app (i.e.: when the app is installed, it will reside in a namespace package called :file:`tethysapp`). This package contains the :term:`app package`, which has the same name as your app name by convention.

.. caution::

	When you generate a new app project using the command line tool, you will notice that many of the directories contain a :file:`\_\_init\_\_.py` file, many of which are empty. These are omitted in the diagram for simplicity. DO NOT DELETE THE :file:`\_\_init\_\_.py` FILES. These files indicate to Python that the directories containing them are `Python packages <https://docs.python.org/3/tutorial/modules.html>`_. Your app will not work properly without the :file:`\_\_init\_\_.py` files.

The App Package
===============

The :term:`app package` contains all of the source code and resources that are needed by the Tethys Platform to run your app. The :file:`model.py`, :file:`templates`, and :file:`controllers.py` modules and directories correspond with the Model View Controller approach that is used to build apps.

The data structures, classes, and methods that are used to define the data model :file:`model.py` module. The :file:`templates` directory contains all the Django HTML templates that are used to generate the views of the app. The :file:`controllers.py` module contains Python files for each controller of the app. The :file:`public` directory is used for static resources such as images, JavaScript and CSS files. The :file:`app.py` file contains all the configuration parameters for the app.

To learn how to work with the files in the :term:`app package`, see the :ref:`key_concepts_tutorial` tutorial.

Naming Conventions
==================

There are a few naming conventions that need to be followed to avoid conflicts with other apps. The more obvious one is the :term:`app package` name. Like all Python modules, :term:`app package` names must be unique.

All templates should be contained in a directory that shares the same name as the :term:`app package` within the :file:`templates` directory (see Figure 1). This ensures that when your app calls for a template like :file:`home.html` it finds the correct one and not an :file:`home.html` from another app.
