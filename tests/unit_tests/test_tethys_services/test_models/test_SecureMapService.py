from tethys_sdk.testing import TethysTestCase
from tethys_services.models import SecureMapService
import requests
from unittest import mock
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.functional import Promise
from django.utils.encoding import force_str


class SecureMapServiceTests(TethysTestCase):
    def set_up(self):
        self.test_user = self.create_test_user(
            username="testuser", password="testpassword"
        )
        self.params_with_api_key = {"param1": "value1", "api_key": "${api_key}"}
        self.params_without_api_key = {"param1": "value1"}

        self.map_service_with_api_key_no_proxy = SecureMapService(
            name="api_key_no_proxy",
            legend_title="Map Service with API Token No Proxy",
            endpoint="https://example.com/map_service",
            authentication_method="api_key",
            api_key="test_api_key",
            service_type="WMS",
            params=self.params_with_api_key,
            use_proxy=False,
            connection_timeout=14,
            read_timeout=29,
        )
        self.map_service_with_api_key_no_proxy.save()

        self.map_service_without_api_key_param_no_proxy = SecureMapService(
            name="no_api_key_params_no_proxy",
            legend_title="Map Service without API Token Param No Proxy",
            endpoint="https://example.com/map_service",
            authentication_method="api_key",
            api_key="test_api_key",
            service_type="WMS",
            params=self.params_without_api_key,
            use_proxy=False,
            connection_timeout=12,
            read_timeout=16,
        )
        self.map_service_without_api_key_param_no_proxy.save()

        self.map_service_with_api_key_with_proxy = SecureMapService(
            name="api_key_with_proxy",
            legend_title="Map Service with API Token With Proxy",
            endpoint="https://example.com/map_service",
            authentication_method="api_key",
            api_key="test_api_key",
            service_type="GML",
            params=self.params_with_api_key,
            use_proxy=True,
            connection_timeout=15,
            read_timeout=20,
        )
        self.map_service_with_api_key_with_proxy.save()

        self.map_service_with_oauth_no_proxy = SecureMapService(
            name="oauth_no_proxy",
            legend_title="Map Service with OAuth2 No Proxy",
            endpoint="https://example.com/map_service",
            authentication_method="oauth2",
            oauth2_provider="test_oauth2_provider",
            service_type="GML",
            params=self.params_without_api_key,
            use_proxy=False,
            connection_timeout=17,
            read_timeout=21,
        )
        self.map_service_with_oauth_no_proxy.save()

        self.map_service_with_oauth_with_proxy = SecureMapService(
            name="oauth_with_proxy",
            legend_title="Map Service with OAuth2 With Proxy",
            endpoint="https://example.com/map_service",
            authentication_method="oauth2",
            oauth2_provider="test_oauth2_provider",
            service_type="WMS",
            params=self.params_without_api_key,
            use_proxy=True,
            connection_timeout=16,
            read_timeout=27,
        )
        self.map_service_with_oauth_with_proxy.save()

    def tear_down(self):
        self.map_service_with_api_key_no_proxy.delete()
        self.map_service_with_api_key_with_proxy.delete()
        self.map_service_without_api_key_param_no_proxy.delete()
        self.map_service_with_oauth_no_proxy.delete()
        self.map_service_with_oauth_with_proxy.delete()

    def test_str(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service", endpoint="http://example.com"
        )
        self.assertEqual("test_secure_map_service", str(secure_map_service))

    def test_clean_invalid_params(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            params="invalid_params",
        )

        with self.assertRaises(ValidationError) as context:
            secure_map_service.clean()
        self.assertEqual(
            {"params": ['Parameters must be a JSON object (e.g. {"key": "value"})']},
            context.exception.message_dict,
        )

    def test__get_oauth_token_user_unauthenticated(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            authentication_method="oauth2",
            oauth2_provider="test_provider",
        )

        mock_user = mock.MagicMock()
        mock_user.is_authenticated = False

        with self.assertRaises(ValueError) as context:
            secure_map_service._get_oauth_token(user=mock_user)
        self.assertEqual(
            str(context.exception),
            "User must be authenticated to retrieve an OAuth2 token.",
        )

    def test__get_oauth_token_api_key(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            authentication_method="api_key",
        )
        mock_user = mock.MagicMock()
        mock_user.is_authenticated = True
        with self.assertRaises(ValueError) as context:
            secure_map_service._get_oauth_token(user=mock_user)
        self.assertEqual(
            str(context.exception),
            "Authentication method must be 'oauth2' to retrieve an OAuth2 token.",
        )

    def test__get_oauth_token_no_provider(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            authentication_method="oauth2",
        )
        mock_user = mock.MagicMock()
        mock_user.is_authenticated = True
        with self.assertRaises(ValueError) as context:
            secure_map_service._get_oauth_token(user=mock_user)
        self.assertEqual(
            str(context.exception),
            "OAuth2 provider must be specified to retrieve an OAuth2 token.",
        )

    def test__get_oauth_token_user_not_linked(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            authentication_method="oauth2",
            oauth2_provider="test_provider",
        )

        mock_user = mock.MagicMock()
        mock_user.social_auth.get.side_effect = ObjectDoesNotExist

        with self.assertRaises(ValueError) as context:
            secure_map_service._get_oauth_token(user=mock_user)
        self.assertEqual(
            str(context.exception),
            "User not linked to test_provider for OAuth2 authentication.",
        )

    def test__get_oauth_token_no_token(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            authentication_method="oauth2",
            oauth2_provider="test_provider",
        )

        mock_user = mock.MagicMock()
        mock_user.social_auth.get.return_value.get_access_token.return_value = None

        with self.assertRaises(ValueError) as context:
            secure_map_service._get_oauth_token(user=mock_user)
        self.assertEqual(str(context.exception), "No access token found for user.")

    def test__get_oauth_token_get_access_token_failure(self):
        from social_core.exceptions import AuthException

        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            authentication_method="oauth2",
            oauth2_provider="test_provider",
        )

        mock_user = mock.MagicMock()
        mock_user.social_auth.get.return_value.get_access_token.side_effect = (
            AuthException(mock.MagicMock(), "access token failure")
        )

        with self.assertRaises(ValueError) as context:
            secure_map_service._get_oauth_token(user=mock_user)
        self.assertEqual(
            str(context.exception),
            f"Failed to retrieve access Oauth2 token for {secure_map_service.oauth2_provider}: access token failure",
        )

    def test__get_oauth_token_without_expiry_success(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            authentication_method="oauth2",
            oauth2_provider="test_provider",
        )

        mock_user = mock.MagicMock()
        mock_user.social_auth.get.return_value.get_access_token.return_value = (
            "access_token12345"
        )
        token = secure_map_service._get_oauth_token(user=mock_user)
        self.assertEqual(token, "access_token12345")

    def test__get_oauth_token_with_expiry_success(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            authentication_method="oauth2",
            oauth2_provider="test_provider",
        )

        mock_user = mock.MagicMock()
        mock_auth = mock.MagicMock()
        mock_auth.get_access_token.return_value = "access_token12345"
        mock_expiration = mock.MagicMock()
        mock_expiration.total_seconds.return_value = 4
        mock_auth.expiration_timedelta.return_value = mock_expiration

        mock_user.social_auth.get.return_value = mock_auth

        token, expires_in = secure_map_service._get_oauth_token(
            user=mock_user, with_expiry=True
        )
        self.assertEqual(token, "access_token12345")
        self.assertEqual(expires_in, 4)

    def test__get_resolved_params(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            authentication_method="api_key",
            params=None,
        )

        result = secure_map_service._get_resolved_params()
        self.assertEqual(result, {})

    def test__get_resolved_params_invalid_params(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            authentication_method="api_key",
            params="invalid_params",
            api_key="api_key_12345",
        )

        with self.assertRaises(ValueError) as context:
            secure_map_service._get_resolved_params()
        self.assertEqual(
            str(context.exception),
            f"SecureMapService '{secure_map_service.name}': params must be a JSON object, got str.",
        )

    def test__get_resolved_params_with_api_key_with_different_name(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            authentication_method="api_key",
            params={
                "param1": "value1",
                "param2": "value2",
                "test_api_key": "${api_key}",
            },
            api_key="api_key_12345",
        )
        resolved_params = secure_map_service._get_resolved_params()
        self.assertEqual(
            resolved_params,
            {"param1": "value1", "param2": "value2", "test_api_key": "api_key_12345"},
        )

    def test__get_resolved_params_with_api_key_without_api_key_in_params(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            authentication_method="api_key",
            params={
                "param1": "value1",
                "param2": "value2",
            },
            api_key="api_key_12345",
        )

        resolved_params = secure_map_service._get_resolved_params()
        self.assertEqual(
            resolved_params,
            {"param1": "value1", "param2": "value2", "api_key": "api_key_12345"},
        )

    def test__get_resolved_params_with_missing_api_key(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            authentication_method="api_key",
            params={
                "param1": "value1",
                "param2": "value2",
                "test_api_key": "${api_key}",
            },
            api_key=None,
        )

        resolved_params = secure_map_service._get_resolved_params()
        self.assertEqual(
            resolved_params,
            {"param1": "value1", "param2": "value2", "test_api_key": ""},
        )

    def test__get_resolved_params_with_multiple_params(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            authentication_method="api_key",
            params={
                "param1": "value1",
                "name": "${name}",
                "test_api_key": "${api_key}",
            },
            api_key="api_key_12345",
        )

        resolved_params = secure_map_service._get_resolved_params()
        self.assertEqual(
            resolved_params,
            {
                "param1": "value1",
                "name": "test_secure_map_service",
                "test_api_key": "api_key_12345",
            },
        )

    def test__update_params(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            params={"param1": "value1", "param2": "value2"},
        )
        secure_map_service.save()

        secure_map_service._update_params({"param2": "new_value", "param3": "value3"})

        updated_service = SecureMapService.objects.get(pk=secure_map_service.pk)
        self.assertEqual(
            updated_service.params,
            {"param1": "value1", "param2": "new_value", "param3": "value3"},
        )

    def test__update_params_no_existing_params(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            params=None,
        )
        secure_map_service.save()

        secure_map_service._update_params({"param1": "value1"})

        updated_service = SecureMapService.objects.get(pk=secure_map_service.pk)
        self.assertEqual(updated_service.params, {"param1": "value1"})

    def test__update_params_invalid_params(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            params={"param1": "value1"},
        )
        secure_map_service.save()

        with self.assertRaises(ValueError) as context:
            secure_map_service._update_params(None)

        self.assertEqual(
            str(context.exception), "new_params must be a JSON object (dict)."
        )

    def test__generate_request_with_proxy(self):
        service = self.map_service_with_api_key_with_proxy

        url = service._generate_request()

        self.assertIsInstance(url, Promise)
        self.assertEqual(f"/secure-map-proxy/{service.pk}/", force_str(url))

    def test__generate_request_without_proxy_with_api_key(self):
        service = self.map_service_with_api_key_no_proxy
        url = service._generate_request()

        self.assertEqual(
            url, "https://example.com/map_service?param1=value1&api_key=test_api_key"
        )

    def test__generate_request_without_proxy_without_api_key_param(self):
        service = self.map_service_without_api_key_param_no_proxy
        url = service._generate_request()

        self.assertEqual(
            url, "https://example.com/map_service?param1=value1&api_key=test_api_key"
        )

    def test__generate_request_param_overrides_no_proxy(self):
        service = self.map_service_with_api_key_no_proxy

        url = service._generate_request(
            param_overrides={"param1": "overridden_value", "param2": "value2"}
        )

        self.assertEqual(
            url,
            "https://example.com/map_service?param1=overridden_value&api_key=test_api_key&param2=value2",
        )

    def test__generate_request__param_overrides_with_proxy(self):
        service = self.map_service_with_api_key_with_proxy

        url = service._generate_request(
            param_overrides={"param1": "overridden_value", "param2": "value2"}
        )

        self.assertIsInstance(url, Promise)
        self.assertEqual(
            f"/secure-map-proxy/{service.pk}/?param1=overridden_value&param2=value2",
            force_str(url),
        )

    def test__build_layer_with_api_key(self):
        service = self.map_service_with_api_key_no_proxy

        layer = service._build_layer()

        self.assertEqual(layer["source"], service.service_type)

        self.assertEqual(
            layer["options"]["url"],
            "https://example.com/map_service?param1=value1&api_key=test_api_key",
        )

    def test__build_layer_without_api_key_param(self):
        service = self.map_service_without_api_key_param_no_proxy
        layer = service._build_layer()

        self.assertEqual(layer["source"], service.service_type)
        self.assertEqual(
            layer["options"]["url"],
            "https://example.com/map_service?param1=value1&api_key=test_api_key",
        )

    def test__build_layer_with_proxy(self):
        service = self.map_service_with_api_key_with_proxy

        layer = service._build_layer()

        self.assertEqual(layer["source"], service.service_type)
        self.assertIsInstance(layer["options"]["url"], Promise)
        self.assertEqual(
            force_str(layer["options"]["url"]),
            f"/secure-map-proxy/{service.pk}/",
        )

    def test__build_layer_param_overrides(self):
        service = self.map_service_with_api_key_no_proxy

        layer = service._build_layer(
            param_overrides={"param1": "overridden_value", "param2": "value2"}
        )

        self.assertEqual(layer["source"], service.service_type)
        self.assertEqual(
            layer["options"]["url"],
            "https://example.com/map_service?param1=overridden_value&api_key=test_api_key&param2=value2",
        )

    @mock.patch(
        "tethys_services.models.SecureMapService._get_oauth_token",
        return_value="test_oauth_token",
    )
    def test__build_Layer_oauth(self, mock_got):
        service = self.map_service_with_oauth_no_proxy

        layer = service._build_layer()
        self.assertEqual(layer["source"], service.service_type)
        self.assertEqual(
            layer["options"]["url"], "https://example.com/map_service?param1=value1"
        )
        self.assertEqual(
            layer["options"]["token_url"],
            f"/secure-map-token/{service.id}/",
        )

    def test__fetch_response_no_request_user(self):
        service = self.map_service_with_oauth_no_proxy

        self.assertRaises(
            ValueError,
            service._fetch_response,
            request_user=None,
        )

    @mock.patch("tethys_services.models.requests.get")
    def test__fetch_response_with_api_key(self, mock_get):
        service = self.map_service_with_api_key_no_proxy

        mock_response = mock.MagicMock(
            status_code=200,
            ok=True,
            url="https://example.com/map_service?param1=value1&api_key=test_api_key",
        )
        mock_get.return_value = mock_response

        response = service._fetch_response()

        self.assertEqual(
            response.url,
            "https://example.com/map_service?param1=value1&api_key=test_api_key",
        )
        self.assertEqual(response.status_code, 200)

    @mock.patch(
        "tethys_services.models.SecureMapService._get_oauth_token",
        return_value="test_oauth_token",
    )
    @mock.patch("tethys_services.models.requests.get")
    def test__fetch_response_with_oauth_header(self, mock_get, mock_got):
        service = self.map_service_with_oauth_no_proxy

        mock_response = mock.MagicMock(
            status_code=200,
            ok=True,
            url="https://example.com/map_service?param1=value1",
        )
        mock_get.return_value = mock_response

        response = service._fetch_response(request_user=self.test_user)

        mock_got.assert_called_once_with(self.test_user)

        self.assertEqual(response.url, "https://example.com/map_service?param1=value1")
        self.assertEqual(response.status_code, 200)

    @mock.patch("tethys_services.models.log")
    @mock.patch(
        "tethys_services.models.SecureMapService._get_oauth_token",
        return_value="test_oauth_token",
    )
    @mock.patch("tethys_services.models.requests.get")
    def test__fetch_response_with_oauth_response_not_ok(
        self, mock_get, mock_got, mock_log
    ):
        service = self.map_service_with_oauth_no_proxy

        mock_response = mock.MagicMock(
            status_code=403,
            ok=False,
            url="https://example.com/map_service?param1=value1",
            text="Forbidden access message",
            raise_for_status=mock.MagicMock(
                side_effect=requests.HTTPError("403 Forbidden")
            ),
        )
        mock_get.return_value = mock_response

        with self.assertRaises(requests.HTTPError):
            service._fetch_response(request_user=self.test_user)

        mock_got.assert_called_once_with(self.test_user)
        mock_log.error.assert_called_once()
        logged = mock_log.error.call_args.args[0]
        self.assertIn(
            f"SecureMapService with name {service.name} request failed",
            logged,
        )
        self.assertIn("status_code: 403", logged)
        self.assertIn("Forbidden access message", logged)

    @mock.patch(
        "tethys_services.models.SecureMapService._get_oauth_token",
        return_value="test_oauth_token",
    )
    @mock.patch("tethys_services.models.requests.get")
    def test__fetch_response_with_oauth_good_response(self, mock_get, mock_got):
        service = self.map_service_with_oauth_no_proxy

        mock_response = mock.MagicMock(
            status_code=200,
            ok=True,
            url="https://example.com/map_service?param1=value1",
        )
        mock_get.return_value = mock_response

        response = service._fetch_response(request_user=self.test_user)

        mock_got.assert_called_once_with(self.test_user)

        self.assertEqual(response, mock_response)
        self.assertEqual(response.status_code, 200)

    @mock.patch("tethys_services.models.requests.get")
    def test__fetch_response_with_api_key_with_overrides(self, mock_get):
        service = self.map_service_with_api_key_no_proxy

        mock_response = mock.MagicMock(
            status_code=200,
            ok=True,
            url="https://example.com/map_service?param1=overridden_value&api_key=test_api_key&param2=value2",
        )
        mock_get.return_value = mock_response

        response = service._fetch_response(
            param_overrides={"param1": "overridden_value", "param2": "value2"}
        )

        self.assertEqual(
            response.url,
            "https://example.com/map_service?param1=overridden_value&api_key=test_api_key&param2=value2",
        )
        self.assertEqual(response.status_code, 200)

    @mock.patch("tethys_services.models.log")
    @mock.patch("tethys_services.models.requests.get")
    def test__fetch_response_request_timeout(self, mock_get, mock_log):
        service = self.map_service_with_api_key_no_proxy

        mock_get.side_effect = requests.Timeout

        with self.assertRaises(requests.exceptions.Timeout):
            service._fetch_response()
        mock_log.error.assert_called_with(
            "SecureMapService with name api_key_no_proxy request timed out. (connection_timeout: 14s, read_timeout: 29s)"
        )
