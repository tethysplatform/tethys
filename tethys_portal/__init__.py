"""
********************************************************************************
* Name: tethys_portal/__init__.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("tethys-platform")
except PackageNotFoundError:
    print("WARNING: Unable to find version for package tethys-platform")
    __version__ = None
