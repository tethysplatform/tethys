from unittest import mock
from django import test
from tethys_services.backends.arcgis_portal import ArcGISPortalOAuth2


@test.override_settings(
    OAUTH_CONFIG={
        'SOCIAL_AUTH_ARCGIS_PORTAL_URL': 'https://my.test.arcgis/portal'
    }
)
class ArcGISPortalBackendTest(test.SimpleTestCase):
    def setUp(self):
        self.strategy = mock.MagicMock()

    def tearDown(self):
        pass

    def test_attributes(self):
        inst = ArcGISPortalOAuth2(self.strategy)

        self.assertEqual('https://my.test.arcgis/portal', inst.PORTAL_URL)
        self.assertEqual(f'{inst.PORTAL_URL}/sharing/rest/oauth2/authorize',
                         inst.AUTHORIZATION_URL)
        self.assertEqual(f'{inst.PORTAL_URL}/sharing/rest/oauth2/token',
                         inst.ACCESS_TOKEN_URL)

    @test.override_settings(OAUTH_CONFIG={
        'SOCIAL_AUTH_ARCGIS_PORTAL_URL': ''
    })
    def test_oidc_endpoint__no_portal_url(self):
        with self.assertRaises(ValueError) as context:
            inst = ArcGISPortalOAuth2(self.strategy)
            inst.PORTAL_URL
        self.assertEqual('You must specify the url of your ArcGIS Enterprise Portal via '
                         'the "SOCIAL_AUTH_ARCGIS_PORTAL_URL" setting in your '
                         'portal_config.yml file.', str(context.exception))

    @test.override_settings(OAUTH_CONFIG={
        'SOCIAL_AUTH_ARCGIS_PORTAL_URL': 'https://my.test.arcgis/portal/'
    })
    def test_oidc_endpoint__portal_url_end_slash(self):
        inst = ArcGISPortalOAuth2(self.strategy)

        ret = inst.PORTAL_URL

        self.assertEqual('https://my.test.arcgis/portal', ret)

    def test_user_data(self):
        inst = ArcGISPortalOAuth2(self.strategy)
        inst.get_json = mock.MagicMock()
        inst.user_data('my_special_token_12345')
        inst.get_json.assert_called_once_with(
            'https://my.test.arcgis/portal/sharing/rest/community/self',
            params={
                'token': 'my_special_token_12345',
                'f': 'json'
            }
        )

    def test_get_user_details__no_fullname(self):
        response = {
            'username': 'user1920394',
            'fullName': '',
            'email': 'test@email.com'
        }

        inst = ArcGISPortalOAuth2(self.strategy)
        details = inst.get_user_details(response)

        self.assertEqual(details['username'], 'user1920394')
        self.assertEqual(details['email'], 'test@email.com')
        self.assertEqual(details['fullname'], '')
        self.assertEqual(details['first_name'], '')
        self.assertEqual(details['last_name'], '')

    def test_get_user_details__firstname_only(self):
        response = {
            'username': 'user1920394',
            'fullName': 'John',
            'email': 'test@email.com'
        }

        inst = ArcGISPortalOAuth2(self.strategy)
        details = inst.get_user_details(response)

        self.assertEqual(details['username'], 'user1920394')
        self.assertEqual(details['email'], 'test@email.com')
        self.assertEqual(details['fullname'], 'John')
        self.assertEqual(details['first_name'], 'John')
        self.assertEqual(details['last_name'], '')

    def test_get_user_details__fullname(self):
        response = {
            'username': 'user1920394',
            'fullName': 'John Doe',
            'email': 'test@email.com'
        }

        inst = ArcGISPortalOAuth2(self.strategy)
        details = inst.get_user_details(response)

        self.assertEqual(details['username'], 'user1920394')
        self.assertEqual(details['email'], 'test@email.com')
        self.assertEqual(details['fullname'], 'John Doe')
        self.assertEqual(details['first_name'], 'John')
        self.assertEqual(details['last_name'], 'Doe')
