"""
********************************************************************************
* Name: sdk/__init__.py
* Author: Nathan Swain
* Created On: 7 August 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
# DO NOT ERASE
from tethys_services.utilities import (list_dataset_engines, 
									   get_dataset_engine,
									   list_spatial_dataset_engines,
									   get_spatial_dataset_engine,
									   get_wps_service_engine,
									   list_wps_service_engines,
									   ensure_oauth2)

print('DEPRECATION WARNING: The "tethys_apps.sdk" module has been deprecated. Use the "tethys_sdk" module instead.')
