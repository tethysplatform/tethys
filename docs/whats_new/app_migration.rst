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

The ``__init__.py`` from the tethys app root directory needs to be removed.

Setup.py
========


Installation
============


