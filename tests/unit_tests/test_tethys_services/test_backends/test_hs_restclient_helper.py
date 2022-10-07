import unittest
from unittest import mock
import time
from tethys_services.backends.hs_restclient_helper import HSClientInitException
import tethys_services.backends.hs_restclient_helper as hs_client_init_exception
from django.test import override_settings


class HsRestClientHelperTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        exc = HSClientInitException("foo")
        self.assertEqual("foo", exc.value)
        self.assertEqual("'foo'", str(exc))

    @mock.patch("tethys_services.backends.hs_restclient_helper.logger")
    def test_get_get_oauth_hs_main_exception(self, mock_logger):
        mock_request = mock.MagicMock()
        mock_request.user.social_auth.all.side_effect = Exception("foo")

        self.assertRaises(
            HSClientInitException, hs_client_init_exception.get_oauth_hs, mock_request
        )
        mock_logger.exception.assert_called_once_with(
            "Failed to initialize hs object: foo"
        )

    @override_settings(SOCIAL_AUTH_HYDROSHARE_KEY="", SOCIAL_AUTH_HYDROSHARE_SECRET="")
    @mock.patch("tethys_services.backends.hs_restclient_helper.hs_r")
    @mock.patch("tethys_services.backends.hs_restclient_helper.refresh_user_token")
    @mock.patch("tethys_services.backends.hs_restclient_helper.logger")
    def test_get_get_oauth_hs_one_hydroshare(
        self, mock_logger, mock_refresh_user_token, mock_hs_r
    ):
        mock_social_auth_obj = mock.MagicMock()
        mock_backend_instance = mock.MagicMock()
        mock_backend_instance.name = "hydroshare"
        mock_backend_instance.auth_server_hostname = "foo"
        mock_data1 = {
            "id": "id",
            "access_token": "my_access_token",
            "token_type": "my_token_type",
            "expires_in": "my_expires_in",
            "expires_at": "my_expires_at",
            "refresh_token": "my_refresh_token",
            "scope": "my_scope",
        }

        mock_request = mock.MagicMock()
        mock_request.user.social_auth.all.return_value = [mock_social_auth_obj]
        mock_social_auth_obj.get_backend_instance.return_value = mock_backend_instance
        mock_social_auth_obj.extra_data.return_value = mock_data1
        mock_refresh_user_token.return_value = True

        hs_client_init_exception.get_oauth_hs(mock_request)

        mock_logger.debug.assert_any_call("Found oauth backend: hydroshare")
        mock_refresh_user_token.assert_called_once_with(mock_social_auth_obj)
        mock_hs_r.HydroShareAuthOAuth2.assert_called_once_with(
            "", "", token=mock_social_auth_obj.extra_data
        )
        mock_hs_r.HydroShare.assert_called_once_with(
            auth=mock_hs_r.HydroShareAuthOAuth2(),
            hostname=mock_backend_instance.auth_server_hostname,
        )
        mock_logger.debug.assert_called_with(
            "hs object initialized: {0} @ {1}".format(
                mock_social_auth_obj.extra_data["id"],
                mock_backend_instance.auth_server_hostname,
            )
        )

    @override_settings(SOCIAL_AUTH_HYDROSHARE_KEY="", SOCIAL_AUTH_HYDROSHARE_SECRET="")
    @mock.patch("tethys_services.backends.hs_restclient_helper.hs_r")
    @mock.patch("tethys_services.backends.hs_restclient_helper.refresh_user_token")
    @mock.patch("tethys_services.backends.hs_restclient_helper.logger")
    def test_get_get_oauth_two_hydroshare_exception(
        self, mock_logger, mock_refresh_user_token, mock_hs_r
    ):
        mock_social_auth_obj = mock.MagicMock()
        mock_backend_instance = mock.MagicMock()
        mock_backend_instance.name = "hydroshare"
        mock_backend_instance.auth_server_hostname = "foo"
        mock_data1 = {
            "id": "id",
            "access_token": "my_access_token",
            "token_type": "my_token_type",
            "expires_in": "my_expires_in",
            "expires_at": "my_expires_at",
            "refresh_token": "my_refresh_token",
            "scope": "my_scope",
        }

        mock_request = mock.MagicMock()
        mock_request.user.social_auth.all.return_value = [
            mock_social_auth_obj,
            mock_social_auth_obj,
        ]
        mock_social_auth_obj.get_backend_instance.return_value = mock_backend_instance
        mock_social_auth_obj.extra_data.return_value = mock_data1
        mock_refresh_user_token.return_value = True

        self.assertRaises(
            HSClientInitException, hs_client_init_exception.get_oauth_hs, mock_request
        )

        mock_logger.debug.assert_any_call("Found oauth backend: hydroshare")
        mock_refresh_user_token.assert_called_once_with(mock_social_auth_obj)
        mock_hs_r.HydroShareAuthOAuth2.assert_called_once_with(
            "", "", token=mock_social_auth_obj.extra_data
        )
        mock_hs_r.HydroShare.assert_called_once_with(
            auth=mock_hs_r.HydroShareAuthOAuth2(),
            hostname=mock_backend_instance.auth_server_hostname,
        )
        mock_logger.debug.assert_any_call(
            "hs object initialized: {0} @ {1}".format(
                mock_social_auth_obj.extra_data["id"],
                mock_backend_instance.auth_server_hostname,
            )
        )
        mock_logger.debug.assert_called_with("Found oauth backend: hydroshare")
        mock_logger.exception.assert_called_once_with(
            "Failed to initialize hs object: Found another hydroshare oauth "
            "instance: {0} @ {1}".format(
                mock_social_auth_obj.extra_data["id"],
                mock_backend_instance.auth_server_hostname,
            )
        )

    @mock.patch("tethys_services.backends.hs_restclient_helper.logger")
    def test_get_get_oauth_no_hydroshare_exception(self, mock_logger):
        mock_request = mock.MagicMock()
        mock_request.user.social_auth.all.return_value = []

        self.assertRaises(
            HSClientInitException, hs_client_init_exception.get_oauth_hs, mock_request
        )

        mock_logger.exception.assert_called_once_with(
            "Failed to initialize hs object: Not logged in through " "HydroShare"
        )
        mock_request.user.social_auth.all.assert_called_once()

    @mock.patch("tethys_services.backends.hs_restclient_helper.logger")
    @mock.patch("tethys_services.backends.hs_restclient_helper.load_strategy")
    def test__send_refresh_request(self, mock_load_st, mock_log):
        # mock token data
        mock_data1 = {
            "access_token": "my_access_token",
            "token_type": "my_token_type",
            "expires_in": "my_expires_in",
            "expires_at": "my_expires_at",
            "refresh_token": "my_refresh_token",
            "scope": "my_scope",
        }
        # mock user social data as mock token data
        mock_user_social = mock.MagicMock()
        mock_user_social.refresh.return_value = True
        mock_user_social.extra_data.return_value = mock_data1
        mock_user_social.set_extra_data.return_value = True
        mock_user_social.save.return_value = True

        # mock the load_strategy() call
        mock_load_st.return_value = mock.MagicMock()

        # call the method to test
        hs_client_init_exception._send_refresh_request(mock_user_social)

        # check mock user_social is called with mock_load_st
        mock_user_social.refresh_token.assert_called_with(mock_load_st())
        mock_user_social.set_extra_data.assert_called_once_with(
            extra_data=mock_user_social.extra_data
        )
        mock_user_social.save.assert_called_once()
        mock_log.debug.assert_called()

    @mock.patch("tethys_services.backends.hs_restclient_helper._send_refresh_request")
    def test_refresh_user_token(self, mock_refresh_request):
        # mock user social data as mock token data
        mock_user_social = mock.MagicMock()
        mock_user_social.extra_data.get.return_value = int(time.time())

        # call the method to test
        hs_client_init_exception.refresh_user_token(mock_user_social)
        mock_user_social.extra_data.get.assert_called_once_with("expires_at")
        mock_refresh_request.assert_called_once_with(mock_user_social)

    @mock.patch("tethys_services.backends.hs_restclient_helper._send_refresh_request")
    def test_refresh_user_token_exception_1(self, mock_refresh_request):
        # mock user social data as mock token data
        mock_user_social = mock.MagicMock()
        mock_user_social.extra_data.get.side_effect = Exception

        # call the method to test
        hs_client_init_exception.refresh_user_token(mock_user_social)

        mock_user_social.extra_data.get.assert_called_once_with("expires_at")
        mock_refresh_request.assert_called_once_with(mock_user_social)

    @mock.patch("tethys_services.backends.hs_restclient_helper.logger")
    @mock.patch(
        "tethys_services.backends.hs_restclient_helper.time.time",
        side_effect=Exception("foo"),
    )
    @mock.patch("tethys_services.backends.hs_restclient_helper._send_refresh_request")
    def test_refresh_user_token_exception_2(
        self, mock_refresh_request, mock_time, mock_log
    ):
        # mock user social data as mock token data
        mock_user_social = mock.MagicMock()
        mock_user_social.extra_data.get.return_value = 5

        # call the method to test
        self.assertRaises(
            Exception, hs_client_init_exception.refresh_user_token, mock_user_social
        )

        mock_user_social.extra_data.get.assert_called_once_with("expires_at")
        mock_refresh_request.assert_not_called()
        mock_time.assert_called_once()
        mock_log.error.assert_called_once_with("Failed to refresh token: foo")
