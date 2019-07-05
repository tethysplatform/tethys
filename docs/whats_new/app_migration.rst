******************************
Migrating Apps from Tethys 2-3
******************************

Tethys 3 facilitates app installation by providing a new ``install`` command. This command replaces the previous
`Python setup.py <install/develop>`. Some of the main changes to the app installation process are updates to the
directory structure of the app, the setup.py file, and the addition of new functionality to facilitate the installation
and setup of apps including app service configuration using a predefined custim yml file or an interactive mode.

Tethys apps are now python package that are installed in the tethys conda environment and can be imported as shown below:

.. code-block:: python

    # imports test_app
    from tethysapp import test_app

Init.py
=======

The file structure of old tethys apps needs to be slightly modified to work with the new ``install`` command.

.. figure:: ../images/app_package_django.png
	:alt: diagram of a Tethys app project for an app named my_first_app

	**Figure 1. An example of a Tethys app project for an app named "my_first_app".**

The ``__init__.py`` from the ``Project`` and the ``tethysapp`` directories need to be deleted.

The ``__init__.py`` from the ``App Package`` directory needs to be empty.

For example:

Remove the following contents from ``tethysapp-my_first_app/tethysapp/my_first_app/__init__.py``:

.. code-block:: python

    # this is a namespace package
    try:
        import pkg_resources
        pkg_resources.declare_namespace(__name__)
    except ImportError:
        import pkgutil
        __path__ = pkgutil.extend_path(__path__, __name__)


Setup.py
========


Installation
============


