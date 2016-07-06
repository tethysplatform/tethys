"""
********************************************************************************
* Name: models.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
from tethys_apps.app_harvester import SingletonAppHarvester

# Perform App Harvesting
harvester = SingletonAppHarvester()
harvester.harvest_apps()
