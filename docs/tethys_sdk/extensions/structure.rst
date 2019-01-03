************************
Extension File Structure
************************

**Last Updated:** February 22, 2018

The Tethys Extension file structure mimics that of Tethys Apps. Like apps, extensions have the ``templates`` and ``public`` directories and the ``controllers.py`` and ``model.py`` modules. These modules and directories are used in the same way as they are in apps.

There are some notable differences between apps and extensions, however. Rather than an ``app.py`` module, the configuration file for extensions is called ``ext.py``. Like the ``app.py``, the ``ext.py`` module contains a class that is used to configure the extension. Extensions also contain additional packages and directories such as the ``gizmos`` package and ``templates/gizmos`` directory.

.. note::

    Although extensions and apps are similar, extension classes do not support as many operations as the app classes. For example, you cannot specify any service settings (persistent store, spatial dataset, etc.) for extensions, nor can you perform the syncstores on an extension. The capabilities of extensions will certainly grow over time, but some limitations are deliberate.

The sturcture of a freshly scaffolded extension should looks something like this:

::

    tethysext-my_first_extension/
    |-- tethysext/
    |   |-- my_first_extension/
    |   |   |-- gizmos/
    |   |   |   |-- __init__.py
    |   |   |-- public/
    |   |   |   |-- js/
    |   |   |   |   |-- main.js
    |   |   |   |-- css/
    |   |   |   |   |-- main.css
    |   |   |-- templates/
    |   |   |   |-- my_first_extension/
    |   |   |   |-- gizmos/
    |   |   |-- __init__.py
    |   |   |-- contollers.py
    |   |   |-- ext.py
    |   |   |-- model.py
    |   |-- __init__.py
    |-- .gitignore
    |-- setup.py