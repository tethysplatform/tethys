*****************
Distributing Apps
*****************

**Last Updated:** November 17, 2014

Once your app is complete, you will likely want to distribute it for others to use or at the very least install it in a production Tethys Platform environment. When you share your app with others, you will share the entire :term:`release package`, which is the outermost directory of your :term:`app project`. For these tutorials, your release package is called "tethysapp-my_first_app".

The release package contains the source code for your app and a :term:`setup script` (:file:`setup.py`). You may also wish to include a README file and a LICENSE file in this directory. The :term:`setup script` can be used to streamline installation of your app and any Python dependencies it may have. You already used the :term:`setup script` without realizing it in the :doc:`./scaffold` tutorial when you installed your app for the first time (this command: ``python setup.py develop``). A brief introduction to the :term:`setup script` will be provided in this tutorial.

Setup Script
============

When you generate your app using the scaffold, it will automatically generate a :term:`setup script` (:file:`setup.py`). Open the :term:`setup script` for your app located at :file:`~/tethysdev/tethysapp-my_first_app/setup.py`. It should look something like this:

::

    import os
    import sys
    from setuptools import setup, find_packages
    from tethys_apps.app_installation import custom_develop_command, custom_install_command

    ### Apps Definition ###
    app_package = 'my_first_app'
    release_package = 'tethysapp-' + app_package
    app_class = 'my_first_app.app:MyFirstApp'
    app_package_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tethysapp', app_package)

    ### Python Dependencies ###
    dependencies = []

    setup(
        name=release_package,
        version='0.0',
        description='',
        long_description='',
        keywords='',
        author='',
        author_email='',
        url='',
        license='',
        packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
        namespace_packages=['tethysapp', 'tethysapp.' + app_package],
        include_package_data=True,
        zip_safe=False,
        install_requires=dependencies,
        cmdclass={
            'install': custom_install_command(app_package, app_package_dir, dependencies),
            'develop': custom_develop_command(app_package, app_package_dir, dependencies)
        }
    )

As a general rule, you should never modify the parameters under the "Apps Definition" heading. These parameters are used by the :term:`setup script` to find the source code for your app and changing their values could result in your app not working properly. If you use Python libraries that are external to your app or Tethys Platform, you will need add the library name to the ``dependencies`` list in the :term:`setup script`. These libraries will automatically be installed when your app is installed.

The final part of the setup script makes a call to the ``setup()`` function that is provided by the ``setuptools`` library. You will see the metadata that you defined during the scaffold process listed here. As you release subsequent versions of your app, you may wish to increment the ``version`` parameter of this function.

Setup Script Installation
=========================

The setup script is used to install your app and there are two types of installation that can be performed: ``install`` and ``develop``. The ``install`` type of installation hard copies the source code of your app into the :file:`site-packages` directory of your Python installation. The :file:`site-packages` directory is where Python keeps all of the code for external modules and libraries that have been installed.

This is the type of installation you would use for a completed app that is being installed in a production environment. To perform this type of installation, open a terminal, change into the :term:`release package` directory of your app, and run the ``install`` command on the :term:`setup script` as follows:

::

    cd ~/tethysdev/tethysapp-my_first_app
    python setup.py install

The ``install`` type of installation is not well suited for working with your app during development, because you would need to reinstall it (i.e.: run the commands above) every time you made a change to the app source code. This is why the ``develop`` type of installation exists. When an app is installed with the ``develop`` command, the source code for your app is only linked to the :file:`site-packages` directory. This allows you to change your code and test the changes without reinstalling the app.

You already performed this type of installation on your app during the :doc:`./scaffold` tutorial. To perform this type of installation, open a terminal, change into the :term:`release package` directory, and run the ``develop`` command on the :term:`setup script` like so:

::

    cd ~/tethysdev/tethysapp-my_first_app
    python setup.py develop


.. tip::

  For more information about ``setuptools`` and the :term:`setup script`, see the `Setuptools Documentation <https://pythonhosted.org/setuptools/setuptools.html>`_.





