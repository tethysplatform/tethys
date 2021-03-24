"""
********************************************************************************
* Name: arcgis_portal.py
* Author: Shawn Crawley
* Created On: March 2, 2021
* License: BSD 2-Clause
********************************************************************************
"""
from social_core.backends.arcgis import ArcGISOAuth2
from django.conf import settings


class ArcGISPortalOAuth2(ArcGISOAuth2):
    """
    ArcGISPortal OAuth2 authentication backend.
    """
    name = 'arcgis_portal'
    EXTRA_DATA = [
        ('refresh_token', 'refresh_token'),
        ('expires_in', 'expires_in'),
    ]

    @property
    def PORTAL_URL(self):
        portal_url = ''
        try:
            portal_url = settings.OAUTH_CONFIG['SOCIAL_AUTH_ARCGIS_PORTAL_URL']
            if not portal_url:
                raise ValueError()
            if portal_url[-1] == '/':
                portal_url = portal_url[0:-1]
        except (AttributeError, KeyError, ValueError):
            raise ValueError('You must specify the url of your ArcGIS Enterprise Portal via '
                             'the "SOCIAL_AUTH_ARCGIS_PORTAL_URL" setting in your '
                             'portal_config.yml file.')
        return portal_url

    @property
    def AUTHORIZATION_URL(self):
        return f'{self.PORTAL_URL}/sharing/rest/oauth2/authorize'

    @property
    def ACCESS_TOKEN_URL(self):
        return f'{self.PORTAL_URL}/sharing/rest/oauth2/token'

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        return self.get_json(
            f'{self.PORTAL_URL}/sharing/rest/community/self',
            params={
                'token': access_token,
                'f': 'json'
            }
        )

    def get_user_details(self, response):
        """Return user details from ArcGIS Enterprise Portal account"""
        name_parts = response['fullName'].split(' ')
        first_name = name_parts[0]
        last_name = ''
        if len(name_parts) > 1:
            last_name = name_parts[-1]

        return {
            'username': response['username'],
            'email': response['email'],
            'fullname': response['fullName'],
            'first_name': first_name,
            'last_name': last_name
        }
