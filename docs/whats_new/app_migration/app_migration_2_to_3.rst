
.. _migrate_2_to_3:

*********************************
Migrating Apps from Tethys 2 to 3
*********************************

Porting your App to Python 3.6+
===============================

Porting Python 2 apps to Python 3 can be done in a systematic way, and is usually less complicated than expected. We
recommend using the `2to3 <https://docs.python.org/2/library/2to3.html>`_ Python program to translate your Python 2 apps
into Python 3 automatically.

New Tethys App Installation
===========================

Tethys 3 facilitates app installation by providing a new ``install`` command. This command replaces the previous
`Python setup.py <install/develop>`. Some of the main changes to the app installation process are updates to the
directory structure of the app, the ``setup.py`` file, and the addition of new functionality to facilitate the
installation and setup of apps including app service configuration using a predefined custim yml file or an interactive
mode.

Tethys apps are now python package that are installed in the tethys conda environment and can be imported as shown
below:

.. code-block:: python

    # imports test_app
    from tethysapp import test_app

Init.py
-------

The ``__init__.py`` files in the file structure of old tethys apps need to be slightly modified to work with the new
``install`` command.

.. figure:: ../../images/app_package_django.png
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
--------

The setup.py file has been simplified. In addition, the ``find_packages`` function has been replaced with the
``find_namespace_packages``. A new function ``find_resource_files`` is used to carry additional package data such as
templates along with the setup installation.

Example of new ``setup.py`` file:

.. code-block:: python

    from setuptools import setup, find_namespace_packages
    from tethys_apps.app_installation import find_resource_files

    # -- Apps Definition -- #
    app_package = 'test_app'
    release_package = 'tethysapp-' + app_package

    # -- Python Dependencies -- #
    dependencies = []

    # -- Get Resource File -- #
    resource_files = find_resource_files('tethysapp/' + app_package + '/templates', 'tethysapp/' + app_package)
    resource_files += find_resource_files('tethysapp/' + app_package + '/public', 'tethysapp/' + app_package)

    setup(
        name=release_package,
        version='0.0.1',
        description='',
        long_description='',
        keywords='',
        author='',
        author_email='',
        url='',
        license='',
        packages=find_namespace_packages(),
        package_data={'': resource_files},
        include_package_data=True,
        zip_safe=False,
        install_requires=dependencies,
    )

.. note::

    Do not list app dependencies in the ``setup.py``. Dependencies should now be listed using the ``install.yml`` file
    (see :ref:`app_installation`).

App Base Template
-----------------

If you'd like your app to support setting the app icon to use an image from an external source (e.g. "http://example.com/example.jpg"), you'll need to update the `base.html` located in your templates directory. Either remove the `app_icon` block or change it to:

.. code-block:: html+django

    {% block app_icon %}
      {# The path you provided in your app.py is accessible through the tethys_app.icon context variable #}
      <img src="{% if 'http' in tethys_app.icon %}{{ tethys_app.icon }}{% else %}{% static tethys_app.icon %}{% endif %}" />
    {% endblock %}

App Installation
----------------

Tethys apps are now installed using the ``install`` command. See :ref:`app_installation` for an example of
how to use the ``install`` command, how to use ``yml`` files in combination with the ``install`` command, and a list of
available parameters.

::

    # Install Tethys App
    tethys install

    # Install Tethys App with develop
    tethys install -d

    # Skip interactive mode
    tethys install -q

    # Tethys install with custom options
    tethys install -d -f install.yml

Presentation
============

Use this presentation in workshops and training courses to provide an overview of the app migration process: `Migrate Apps from Tethys 2 to Tethys 3 Presentation <https://docs.google.com/presentation/d/16C9Lx4wB84aNrpzW_-PxOwzU_KGgAg54d_g6yfpLdEk/edit>`_.
