"""
********************************************************************************
* Name: setup.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
import os
from pathlib import Path
from setuptools import setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# mangle settings.py if it exists to prevent from being included in installation
settings = Path('tethys_portal/settings.py')
temp_settings = Path('tethys_portal/__settings.tmp')
if settings.is_file():
    settings.rename(temp_settings)

setup(
    setup_requires=['pbr'],
    pbr=True,
)

# restore mangled settings.py
if temp_settings.is_file():
    temp_settings.rename(settings)
