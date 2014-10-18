*****************
Distributing Apps
*****************

**Last Updated:** June 4, 2014

Once your app is complete, you will likely want to distribute it for others to use or at the very least install it in a production Tethys Apps environment. When you share your app with others, give them the entire :term:` release package` The :term:`release package` directory is also a great place to include a README with any instructions specific installing your app. If there are no special instructions, you can refer them to the installation instructions for apps found in the :doc:`../working_with_apps` section. It is also a good idea to include a copy of the license you are releasing the app under in the :term:`release package` directory.  Be sure to use the :term:`setup script` to make installation of your app and all the dependencies as easy as possible. An explanation of the :term:`setup script` is provided in the next section of this article.

Setup Script
============

When you generate your app using the scaffold, it will automatically come with a :term:`setup script` (:file:`setup.py`), located in the top level directory of the :term:`release package`. The :term:`setup script` is used to store metadata about your app, install your app into Python, and install any dependencies it may have. We have added some additinal functionality specific to Tethys Apps to make the app installation process streamlined and easy. Open the setup script for your app (:file:`~/tethysdev/ckanapp-my_first_app/setup.py`).

Variables Section
-----------------

The setup script is divided into several parts. The top of the script includes Python module imports followed by several variables similar to this example:

::

    import sys, os, shutil, subprocess

    from setuptools import setup, find_packages
    from setuptools.command.develop import develop
    from setuptools.command.install import install

    from ckanext.tethys_apps.lib.persistent_store import provision_persistent_stores
    from ckanext.tethys_apps.lib import get_ckanapp_directory

    ### App Packages ###
    # Don't change these
    app_package = 'my_frist_app'
    release_package = 'ckanapp-' + app_package
    app_class = 'my_frist_app.app:MyFirstAppApp'

    ### App Metadata ###
    # Change whatever you'd like here
    version = '1.0'
    author = 'Tethys User'
    author_email = ''
    short_description = 'This is my very first app.'
    long_description = ''
    url = ''
    license = ''
    keywords = ''

    ### Python Dependencies ###
    # List external Python dependencies here by name
    dependencies = [
        # -*- Add names of external Python dependencies here -*-
    ]

The variables section is where you will make most, if any, changes to the setup script. The variables under "App Packages" heading store information about the packages in your app including the :term:`app package` name, :term:`release package` name, and the path to the :term:`app class`. These variables should generally not be changed. The "App Metadata" section contains variables that store metadata about your app such as the version, author, and license of your app. Feel free to modify the variables in this section to meet your needs. The final variable section, "Python Dependencies" contains one variable: ``dependencies``. This variable is a list of Python package names that your app is dependent on. When they :term:`setup script` is run, it will also install any dependencies listed in this variable.

Custom Installation Classes Section
-----------------------------------

The next section of the :term:`setup script` includes two class definitions: `CustomInstallCommand` and `CustomDevelopCommand`. These classes are used by the :term:`setup script` to perform additional steps during installation that are required to fully install an app. Typically, this portion of the :term:`setup script` should not need to be modified. An example of what this section of the :term:`setup script` looks like is shown below: 

::

    class CustomInstallCommand(install):
        """
        When install command is used on setup.py, will copy app package to ckanapp directory.
        """
        def run(self):
            # Get paths
            ckanapp_dir = get_ckanapp_directory()
            app_package_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ckanapp', app_package)
            destination_dir = os.path.join(ckanapp_dir, app_package)
            
            # Notify user
            print 'Copying App Package: {0} to {1}'.format(app_package_dir, destination_dir)
            
            # Copy files
            try: 
                shutil.copytree(app_package_dir, destination_dir)
            except:
                try:
                    shutil.rmtree(destination_dir)
                except:
                    os.remove(destination_dir)
                    
                shutil.copytree(app_package_dir, destination_dir)
        
            # Install dependencies
            for dependency in dependencies:
                subprocess.call(['pip', 'install', dependency])
            
            # Run the original install command
            install.run(self)

    class CustomDevelopCommand(develop):
        """
        When develop command is used on setup.py, will create symbolic link from app package to ckanapp directory.
        """
        def run(self):
            # Get paths
            ckanapp_dir = get_ckanapp_directory()
            app_package_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ckanapp', app_package)
            destination_dir = os.path.join(ckanapp_dir, app_package)
            
            # Notify user
            print 'Creating Symbolic Link to App Package: {0} to {1}'.format(app_package_dir, destination_dir)
            
            # Create symbolic link
            try:
                os.symlink(app_package_dir, destination_dir)
            except:
                try:
                    shutil.rmtree(destination_dir)
                except:
                    os.remove(destination_dir)
                
                os.symlink(app_package_dir, destination_dir)
        
            # Install dependencies
            for dependency in dependencies:
                subprocess.call(['pip', 'install', dependency])
                
            # Run the original develop command
            develop.run(self)

Setup Function Section
----------------------

The next section of the setup script contains the actual call to the ``setup()`` function. This function takes all the variables from the section above as arguments with a few others that won't be discussed in detail here. It is this function that actually runs the installation of your app. There are many other options that can be specified in the ``setup()`` function. Review the `setuptools <https://pythonhosted.org/setuptools/setuptools.html#installing-setuptools>`_ documentation for more information if you wish to take advatage of these options.

::
           
    setup(
        name=release_package,
        version=version,
        description=short_description,
        long_description=long_description,
        classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        keywords=keywords,
        author=author,
        author_email=author_email,
        url=url,
        license=license,
        packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
        namespace_packages=['ckanapp', 'ckanapp.' + app_package],
        include_package_data=True,
        zip_safe=False,
        install_requires=dependencies,
        entry_points=\
        """
        """,
        cmdclass={
            'install': CustomInstallCommand,
            'develop': CustomDevelopCommand
        }
    )

Database Provisioning Function Section
--------------------------------------

The final section of the :term:`setup script` is a call to the ``provision_persisnent_stores()`` function. This function automatically creates any databases that you have requeseted in the :term:`app configuration file` (:file:`app.py`) using the ``registerPersistentStores()`` method. There should be no need to modify this section of the :term:`setup script`, but it could be helpful to know that this exists. For more information on automatic database provisioning, see :doc:`persistent_stores`.

::

    # Provision tethys databases for app
    provision_persistent_stores(app_class)

Production Installation
=======================

Follow the instructions found in the :doc:`../working_with_apps` section to install apps in production.

