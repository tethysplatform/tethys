import unittest
from unittest import mock
from tethys_services.backends.hydroshare import HydroShareOAuth2


class HydroShareBackendTest(unittest.TestCase):
    def setUp(self):
        self.auth_server_hostname = "www.hydroshare.org"
        self.http_scheme = "https"
        self.auth_server_full_url = "{0}://{1}".format(
            self.http_scheme, self.auth_server_hostname
        )
        self.name = "hydroshare"
        self.user_data_url = "{0}/hsapi/userInfo/".format(self.auth_server_full_url)

    def tearDown(self):
        pass

    def test_HydroShareOAuth2(self):
        hydro_share_auth2_obj = HydroShareOAuth2()

        expected_auth_server_full_url = "{0}://{1}".format(
            self.http_scheme, self.auth_server_hostname
        )
        self.assertEqual(
            expected_auth_server_full_url, hydro_share_auth2_obj.auth_server_full_url
        )

        expected_authorization_url = "{0}/o/authorize/".format(
            self.auth_server_full_url
        )
        self.assertEqual(
            expected_authorization_url, hydro_share_auth2_obj.AUTHORIZATION_URL
        )

        expected_access_token_url = "{0}/o/token/".format(self.auth_server_full_url)
        self.assertEqual(
            expected_access_token_url, hydro_share_auth2_obj.ACCESS_TOKEN_URL
        )

        # user data endpoint
        expected_user_data_url = "{0}/hsapi/userInfo/".format(self.auth_server_full_url)
        self.assertEqual(expected_user_data_url, hydro_share_auth2_obj.USER_DATA_URL)

    def test_extra_data(self):
        mock_response = dict(
            email="foo@gmail.com",
            username="user1",
            access_token="token1",
            token_type="type1",
            expires_in="500",
            expires_at="10000000",
            refresh_token="234234",
            scope="scope",
        )
        mock_details = dict(
            name="",
            alias="",
        )

        hydro_share_auth2_obj = HydroShareOAuth2()

        hydro_share_auth2_obj.set_expires_in_to = 100

        ret = hydro_share_auth2_obj.extra_data(
            "user1", "0001-009", mock_response, mock_details
        )

        self.assertEqual("foo@gmail.com", ret["email"])
        self.assertEqual("token1", ret["access_token"])
        self.assertEqual("type1", ret["token_type"])
        self.assertEqual(100, ret["expires_in"])
        self.assertEqual("234234", ret["refresh_token"])
        self.assertEqual("scope", ret["scope"])

    def test_get_user_details(self):
        hydro_share_auth2_obj = HydroShareOAuth2()
        mock_response = mock.MagicMock(username="name", email="email")
        mock_response.get("username").return_value = "name"
        mock_response.get("email").return_value = "email"
        ret = hydro_share_auth2_obj.get_user_details(mock_response)
        self.assertIn("username", ret)
        self.assertIn("email", ret)

    @mock.patch("tethys_services.backends.hydroshare.HydroShareOAuth2.get_json")
    def test_user_data(self, mock_get_json):
        # mock the jason response
        mock_json_rval = mock.MagicMock()
        mock_get_json.return_value = mock_json_rval
        access_token = "token1"

        hydro_share_auth2_obj = HydroShareOAuth2()
        ret = hydro_share_auth2_obj.user_data(access_token)

        self.assertEqual(mock_json_rval, ret)
        mock_get_json.assert_called_once_with(
            self.user_data_url, params={"access_token": "token1"}
        )

    @mock.patch("tethys_services.backends.hydroshare.HydroShareOAuth2.get_json")
    def test_user_data_value_error(self, mock_get_json):
        # mock the jason response
        mock_get_json.side_effect = ValueError
        access_token = "token1"
        hydro_share_auth2_obj = HydroShareOAuth2()
        ret = hydro_share_auth2_obj.user_data(access_token)

        self.assertEqual(None, ret)
        mock_get_json.assert_called_once_with(
            self.user_data_url, params={"access_token": "token1"}
        )

    @mock.patch("tethys_services.backends.hydroshare.BaseOAuth2.refresh_token")
    def test_refresh_token(self, mock_request):
        mock_response = dict(
            email="foo@gmail.com",
            username="user1",
            access_token="token1",
            token_type="type1",
            expires_in=500,
            expires_at=10000000,
            refresh_token="234234",
            scope="scope",
        )
        mock_request.return_value = mock_response

        hydro_share_auth2_obj = HydroShareOAuth2()

        hydro_share_auth2_obj.set_expires_in_to = 100

        ret = hydro_share_auth2_obj.refresh_token("token1")

        self.assertEqual("foo@gmail.com", ret["email"])
        self.assertEqual("token1", ret["access_token"])
        self.assertEqual("type1", ret["token_type"])
        self.assertEqual(100, ret["expires_in"])
        self.assertEqual("234234", ret["refresh_token"])
        self.assertEqual("scope", ret["scope"])
        self.assertIsNotNone(mock_response["expires_in"])

    @mock.patch("tethys_services.backends.hydroshare.BaseOAuth2.extra_data")
    def test_extra_data_type_error_fallback_old_signature(self, mock_super_extra_data):
        """Test extra_data when parent method raises TypeError and falls back to old signature"""
        mock_response = dict(
            email="foo@gmail.com",
            username="user1",
            access_token="token1",
            token_type="type1",
            expires_in=500,
            refresh_token="234234",
            scope="scope",
        )
        mock_details = dict(name="", alias="")

        # Create a call counter to track which call we're on
        call_count = 0

        def mock_extra_data_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            if call_count == 1:
                # First call (with *args, **kwargs) should fail
                raise TypeError("Invalid signature")
            elif call_count == 2:
                # Second call (with just 4 args) should succeed
                return mock_response.copy()
            else:
                raise TypeError("Unexpected call")

        mock_super_extra_data.side_effect = mock_extra_data_side_effect

        hydro_share_auth2_obj = HydroShareOAuth2()
        hydro_share_auth2_obj.set_expires_in_to = 100

        ret = hydro_share_auth2_obj.extra_data(
            "user1", "0001-009", mock_response, mock_details
        )

        # Verify the method was called 2 times
        self.assertEqual(mock_super_extra_data.call_count, 2)

        # Verify the result contains expected data
        self.assertEqual("foo@gmail.com", ret["email"])
        self.assertEqual("token1", ret["access_token"])
        self.assertEqual(
            100, ret["expires_in"]
        )  # Should be overridden by set_expires_in_to

    @mock.patch("tethys_services.backends.hydroshare.BaseOAuth2.extra_data")
    def test_extra_data_type_error_fallback_with_empty_pipeline(
        self, mock_super_extra_data
    ):
        """Test extra_data when parent method requires pipeline_kwargs as empty dict"""
        mock_response = dict(
            email="foo@gmail.com",
            username="user1",
            access_token="token1",
            token_type="type1",
            expires_in=500,
            refresh_token="234234",
            scope="scope",
        )
        mock_details = dict(name="", alias="")

        # Create a call counter to track which call we're on
        call_count = 0

        def mock_extra_data_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            if call_count == 1:
                # First call (with *args, **kwargs) should fail
                raise TypeError("Invalid signature")
            elif call_count == 2:
                # Second call (with just 4 args) should fail
                raise TypeError("Invalid signature")
            elif call_count == 3:
                # Third call (with empty dict) should succeed
                return mock_response.copy()
            else:
                raise TypeError("Unexpected call")

        mock_super_extra_data.side_effect = mock_extra_data_side_effect

        hydro_share_auth2_obj = HydroShareOAuth2()
        hydro_share_auth2_obj.set_expires_in_to = 200

        ret = hydro_share_auth2_obj.extra_data(
            "user1", "0001-009", mock_response, mock_details
        )

        # Verify the method was called 3 times
        self.assertEqual(mock_super_extra_data.call_count, 3)

        # Verify the result
        self.assertEqual("foo@gmail.com", ret["email"])
        self.assertEqual(200, ret["expires_in"])

    @mock.patch("tethys_services.backends.hydroshare.BaseOAuth2.extra_data")
    def test_extra_data_with_pipeline_kwargs(self, mock_super_extra_data):
        """Test extra_data when pipeline_kwargs is provided (new-style signature)"""
        mock_response = dict(
            email="test@example.com",
            username="testuser",
            access_token="test_token",
            token_type="bearer",
            expires_in=3600,
            refresh_token="refresh_token",
            scope="read",
        )
        mock_details = dict(name="Test User", alias="test")
        mock_pipeline_kwargs = {"some": "data"}

        mock_super_extra_data.return_value = mock_response.copy()

        hydro_share_auth2_obj = HydroShareOAuth2()

        ret = hydro_share_auth2_obj.extra_data(
            "testuser",
            "test-uid",
            mock_response,
            mock_details,
            pipeline_kwargs=mock_pipeline_kwargs,
        )

        # Verify the parent method was called with pipeline_kwargs
        mock_super_extra_data.assert_called_once_with(
            "testuser", "test-uid", mock_response, mock_details, mock_pipeline_kwargs
        )

        # Verify additional data was added
        self.assertIn("updated_at", ret)
        self.assertIn("expires_at", ret)
        self.assertIn("expires_at_str", ret)
        self.assertIn("token_dict", ret)
