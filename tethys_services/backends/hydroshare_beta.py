"""
********************************************************************************
* Name: hydroshare.py
* Author: Nathan Swain and Ezra Rice
* Created On: July 31, 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
from hydroshare import HydroShareOAuth2

class HydroShareBetaOAuth2(HydroShareOAuth2):

    # override necessary settings
    auth_server_hostname = "beta.hydroshare.org"
    name = 'hydroshare_beta'
