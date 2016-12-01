"""
********************************************************************************
* Name: hydroshare.py
* Author: Nathan Swain and Ezra Rice
* Created On: July 31, 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
from social.backends.oauth import BaseOAuth2

class HydroShareOAuth2(BaseOAuth2):
    """
    HydroShare OAuth2 authentication backend.
    """
    auth_server_hostname = "beta.hydroshare.org"  # www.hydroshare.org:8080
    http_scheme = "https"  # "http" or "https"
    name = 'hydroshare_beta'

    auth_server_full_url = "{0}://{1}".format(http_scheme, auth_server_hostname)
    AUTHORIZATION_URL = '{0}/o/authorize/'.format(auth_server_full_url)
    ACCESS_TOKEN_URL = '{0}/o/token/'.format(auth_server_full_url)
    ACCESS_TOKEN_METHOD = 'POST'
    SCOPE_SEPARATOR = ','
    ID_KEY = 'username'
    EXTRA_DATA = [
        ('email', 'email'),
        ('username', 'id'),
        ('expires_in', 'expires_in'),
        ('token_type', 'token_type'),
        ('refresh_token', 'refresh_token'),
        ('scope', 'scope'),
        ('token_dict', 'token_dict'),
    ]

    def extra_data(self, user, uid, response, details=None, *args, **kwargs):
        data = super(HydroShareOAuth2, self).extra_data(user, uid, response,
                                                        details,
                                                        *args, **kwargs)

        # Reconstitute token dictionary for client convenience
        hs_restclient_para_dict = {}
        hs_restclient_para_dict['token'] = {
            'access_token': data['access_token'],
            'token_type': data['token_type'],
            'expires_in': data['expires_in'],
            'refresh_token': data['refresh_token'],
            'scope': data['scope']
            }

        hs_restclient_para_dict['key_name'] = "SOCIAL_AUTH_{0}_KEY".format(self.name.upper())
        hs_restclient_para_dict['secret_name'] = "SOCIAL_AUTH_{0}_SECRET".format(self.name.upper())
        hs_restclient_para_dict['auth_server_hostname'] = self.auth_server_hostname
        hs_restclient_para_dict["http_scheme"] = self.http_scheme

        data['hs_restclient'] = hs_restclient_para_dict

        # backward compatible
        token_dict = {
            'access_token': data['access_token'],
            'token_type': data['token_type'],
            'expires_in': data['expires_in'],
            'refresh_token': data['refresh_token'],
            'scope': data['scope']
        }
        data['token_dict'] = token_dict

        return data

    def get_user_details(self, response):
        """
        Return user details from HydroShare account.
        """
        return {'username': response.get('username'),
                'email': response.get('email'),
                }

    def user_data(self, access_token, *args, **kwargs):
        """
        Loads user data from service.
        """
        url = '{0}/hsapi/userInfo/'.format(self.auth_server_full_url)
        try:
            return self.get_json(url, params={'access_token': access_token})
        except ValueError:
            return None
