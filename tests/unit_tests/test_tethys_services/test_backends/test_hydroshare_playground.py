import unittest
from unittest import mock
from tethys_services.backends.hydroshare_playground import HydroSharePlaygroundOAuth2


class TestHydroSharePlayground(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch("tethys_services.backends.hydroshare_beta.HydroShareOAuth2")
    def test_HydroSharePlaygroundOAuth2(self, mock_hydro_share_auth2):
        hydro_share_beta_obj = HydroSharePlaygroundOAuth2(mock_hydro_share_auth2)

        expected_auth_server_full_url = "https://playground.hydroshare.org"
        self.assertEqual(
            expected_auth_server_full_url, hydro_share_beta_obj.auth_server_full_url
        )

        expected_authorization_url = "https://playground.hydroshare.org/o/authorize/"
        self.assertEqual(
            expected_authorization_url, hydro_share_beta_obj.AUTHORIZATION_URL
        )

        expected_access_toekn_url = "https://playground.hydroshare.org/o/token/"
        self.assertEqual(
            expected_access_toekn_url, hydro_share_beta_obj.ACCESS_TOKEN_URL
        )

        expected_user_info = "https://playground.hydroshare.org/hsapi/userInfo/"
        self.assertEqual(expected_user_info, hydro_share_beta_obj.USER_DATA_URL)
