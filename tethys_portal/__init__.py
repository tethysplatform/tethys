"""
********************************************************************************
* Name: tethys_portal/__init__.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

try:
    from ._version import version as __version__
    from ._version import version_tuple  # noqa: F401
except ImportError:
    print("WARNING: Unable to find version for package tethys-platform")
    __version__ = None
    version_tuple = None
