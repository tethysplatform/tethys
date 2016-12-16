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
    http_scheme = "https"

    auth_server_full_url = "{0}://{1}".format(http_scheme, auth_server_hostname)
    AUTHORIZATION_URL = '{0}/o/authorize/'.format(auth_server_full_url)
    ACCESS_TOKEN_URL = '{0}/o/token/'.format(auth_server_full_url)
    USER_DATA_URL = '{0}/hsapi/userInfo/'.format(auth_server_full_url)
