"""
********************************************************************************
* Name: app_installation.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
import os
from setuptools.command.develop import develop
from setuptools.command.install import install


def find_resource_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


def get_tethysapp_directory():
    """
    Return the absolute path to the tethysapp directory.
    """
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tethysapp')


def _run_install(self):
    # Run the original install command
    install.run(self)


def _run_develop(self):
    # Run the original develop command
    develop.run(self)


def custom_install_command(app_package, app_package_dir, dependencies):
    """
    Returns a custom install command class that is tailored for the app calling it.
    """
    # Define the properties (and methods) for the class that will be created.
    properties = {'app_package': app_package,
                  'app_package_dir': app_package_dir,
                  'dependencies': dependencies,
                  'run': _run_install}

    return type('CustomInstallCommand', (install, object), properties)


def custom_develop_command(app_package, app_package_dir, dependencies):
    """
    Returns a custom develop command class that is tailored for the app calling it.
    """
    # Define the properties (and methods) for the class that will be created.
    properties = {'app_package': app_package,
                  'app_package_dir': app_package_dir,
                  'dependencies': dependencies,
                  'run': _run_develop}

    return type('CustomDevelopCommand', (develop, object), properties)
