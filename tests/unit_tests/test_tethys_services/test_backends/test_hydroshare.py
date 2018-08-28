import unittest
import mock
from tethys_services.backends.hydroshare import HydroShareOAuth2


class HydroShareBackendTest(unittest.TestCase):

    def setUp(self):
        self.auth_server_hostname = "www.hydroshare.org"
        self.http_scheme = "https"
        self.auth_server_full_url = "{0}://{1}".format(self.http_scheme, self.auth_server_hostname)
        self.name = 'hydroshare'
        self.user_data_url = '{0}/hsapi/userInfo/'.format(self.auth_server_full_url)

    def tearDown(self):
        pass

    @mock.patch('tethys_services.backends.hydroshare.BaseOAuth2')
    def test_HydroShareOAuth2(self, mock_base_auth):
        hydro_share_auth2_obj = HydroShareOAuth2(mock_base_auth)

        expected_auth_server_full_url = "{0}://{1}".format(self.http_scheme, self.auth_server_hostname)
        self.assertEqual(expected_auth_server_full_url, hydro_share_auth2_obj.auth_server_full_url)

        expected_authorization_url = '{0}/o/authorize/'.format(self.auth_server_full_url)
        self.assertEqual(expected_authorization_url, hydro_share_auth2_obj.AUTHORIZATION_URL)

        expected_access_token_url = '{0}/o/token/'.format(self.auth_server_full_url)
        self.assertEqual(expected_access_token_url, hydro_share_auth2_obj.ACCESS_TOKEN_URL)

        # user data endpoint
        expected_user_data_url = '{0}/hsapi/userInfo/'.format(self.auth_server_full_url)
        self.assertEqual(expected_user_data_url, hydro_share_auth2_obj.USER_DATA_URL)

    # @mock.patch('tethys_services.backends.hydroshare.BaseOAuth2.extra_data')
    # @mock.patch('tethys_services.backends.hydroshare.BaseOAuth2')
    # def test_extra_data(self, mock_base_auth, mock_base_extra_data):
    #
    #     import pdb; pdb.set_trace()
    #     # mock return data object from base class
    #     mock_data = dict(
    #         access_token='',
    #         token_type='',
    #         expires_in='',
    #         expires_at='',
    #         refresh_token='',
    #         scope=''
    #     )
    #
    #     # mock the return value of data from the super class extract_data call
    #     mock_base_extra_data.return_value = mock_data
    #
    #     # mock BaseOAuth2 when creating instance of hydro_share_auth2_obj
    #     hydro_share_auth2_obj = HydroShareOAuth2(mock_base_auth)
    #
    #     hydro_share_auth2_obj.set_expires_in_to = 100
    #
    #     response = mock.MagicMock()
    #
    #     ret = hydro_share_auth2_obj.extra_data('user1', '0001-009', response)
    #     self.assertEquals('foo', ret)

    @mock.patch('tethys_services.backends.hydroshare.BaseOAuth2')
    def test_get_user_details(self, mock_base_auth):

        hydro_share_auth2_obj = HydroShareOAuth2(mock_base_auth)
        mock_response = mock.MagicMock(username='name', email='email')
        mock_response.get('username').return_value = 'name'
        mock_response.get('email').return_value = 'email'
        ret = hydro_share_auth2_obj.get_user_details(mock_response)
        self.assertIn('username', ret)
        self.assertIn('email', ret)

    @mock.patch('tethys_services.backends.hydroshare.HydroShareOAuth2.get_json')
    @mock.patch('tethys_services.backends.hydroshare.BaseOAuth2')
    def test_user_data(self, mock_base_auth, mock_get_json):
        # mock the jason response
        mock_json_rval = mock.MagicMock()
        mock_get_json.return_value = mock_json_rval
        access_token = 'token1'

        hydro_share_auth2_obj = HydroShareOAuth2(mock_base_auth)
        ret = hydro_share_auth2_obj.user_data(access_token)

        self.assertEquals(mock_json_rval, ret)
        mock_get_json.assert_called_once_with(self.user_data_url, params={'access_token': 'token1'})

    @mock.patch('tethys_services.backends.hydroshare.HydroShareOAuth2.get_json')
    @mock.patch('tethys_services.backends.hydroshare.BaseOAuth2')
    def test_user_data_value_error(self, mock_base_auth, mock_get_json):
        # mock the jason response
        mock_get_json.side_effect = ValueError
        access_token = 'token1'

        hydro_share_auth2_obj = HydroShareOAuth2(mock_base_auth)
        ret = hydro_share_auth2_obj.user_data(access_token)

        self.assertEquals(None, ret)
        mock_get_json.assert_called_once_with(self.user_data_url, params={'access_token': 'token1'})

    # @mock.patch('tethys_services.backends.hydroshare.BaseOAuth2')
    # def test_refresh_token(self, mock_base_auth):
    #     mock_data = dict(
    #                 access_token='',
    #                 token_type='',
    #                 expires_in='',
    #                 expires_at='',
    #                 refresh_token='',
    #                 scope=''
    #                 )
    #     mock_base_auth.refresh_token.return_value = mock_data
    #     hydro_share_auth2_obj = HydroShareOAuth2()
    #     hydro_share_auth2_obj.set_expires_in_to = 100
    #     ret = hydro_share_auth2_obj.refresh_token('tok1')


