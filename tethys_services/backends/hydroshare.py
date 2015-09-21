"""
********************************************************************************
* Name: hydroshare.py
* Author: Nathan Swain
* Created On: July 31, 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
import json
from urllib import urlencode
from social.backends.oauth import BaseOAuth2


class HydroShareOAuth2(BaseOAuth2):
    """
    HydroShare OAuth2 authentication backend.

    TODO: This is just an example shell of how to define the HydroShareOAuth2 backend. This needs to be configured when
          the HydroShare OAuth2 authentication service is working. See this article for more details about custom
          python social auth backends: http://psa.matiasaguirre.net/docs/backends/implementation.html
    """
    name = 'hydroshare-oauth2'
    AUTHORIZATION_URL = 'http://playground.hydroshare.org/o/authorize'
    ACCESS_TOKEN_URL = 'http://playground.hydroshare.org/accounts/callback/hydroshare-test/'
    SCOPE_SEPARATOR = ','
    EXTRA_DATA = [
        ('id', 'id'),
        ('expires', 'expires'),
    ]

    def get_user_details(self, response):
        """
        Return user details from HydroShare account.
        """
        return {'username': response.get('username'),
                'email': response.get('email') or '',
                'first_name': response.get('name')}

    def user_data(self, access_token, *args, **kwargs):
        """
        Loads user data from service.
        """
        url = 'https://www.hydroshare.org/hsapi/user' + urlencode({
            'access_token': access_token
        })
        try:
            return json.load(self.urlopen(url))
        except ValueError:
            return None
