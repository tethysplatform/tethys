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


def find_resource_files(directory, relative_to=None):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            if relative_to is not None:
                paths.append(os.path.join(os.path.relpath(path, relative_to), filename))
            else:
                paths.append(os.path.join('..', path, filename))
    return paths


def get_tethysapp_directory():
    """
    Return the absolute path to the tethysapp directory.
    """
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tethysapp')
