"""
********************************************************************************
* Name: helpers.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
import os
from tethys_apps.harvester import SingletonHarvester


def get_tethysapp_dir():
    """
    Returns absolute path to the tethysapp directory.
    """
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tethysapp')


def get_installed_tethys_apps():
    """
    Returns a list apps installed in the tethysapp directory.
    """

    harvester = SingletonHarvester()
    installed_apps = harvester.app_modules

    tethys_apps = {}

    for app_name, app_module in installed_apps.items():
        try:
            app = __import__(app_module, fromlist=[''])
            tethys_apps[app_name] = app.__path__[0]
        except (IndexError, ImportError):
            '''DO NOTHING'''

    return tethys_apps


def get_installed_tethys_extensions():
    """
    Get a list of installed extensions
    """
    harvester = SingletonHarvester()
    install_extensions = harvester.extension_modules
    extension_paths = {}

    for extension_name, extension_module in install_extensions.items():
        try:
            extension = __import__(extension_module, fromlist=[''])
            extension_paths[extension_name] = extension.__path__[0]
        except (IndexError, ImportError):
            '''DO NOTHING'''

    return extension_paths
