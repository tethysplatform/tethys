#!/usr/bin/env python
"""
********************************************************************************
* Name: manage.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

from os import environ
from sys import argv

if __name__ == "__main__":
    environ.setdefault("DJANGO_SETTINGS_MODULE", "tethys_portal.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(argv)
