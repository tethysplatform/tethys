from tethys_sdk.testing import TethysTestCase
from tethys_services.models import SecureMapService
from unittest import mock
from django.core.exceptions import ObjectDoesNotExist


class SecureMapServiceTests(TethysTestCase):
    def test_str(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service", endpoint="http://example.com"
        )
        self.assertEqual("test_secure_map_service", str(secure_map_service))

    def test_get_authentication_method_options(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service", endpoint="http://example.com"
        )

        expected_options = ["api_key", "oauth"]

        actual_options = secure_map_service.get_authentication_method_options()
        for option in expected_options:
            self.assertIn(option, actual_options)

    def test_get_oauth_token_api_key(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            authentication_method="api_key",
        )

        with self.assertRaises(ValueError) as context:
            secure_map_service.get_oauth_token(user=None)
        self.assertEqual(
            str(context.exception),
            "Authentication method must be 'oauth' to retrieve an OAuth token.",
        )

    def test_get_oauth_token_no_provider(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            authentication_method="oauth",
        )

        with self.assertRaises(ValueError) as context:
            secure_map_service.get_oauth_token(user=None)
        self.assertEqual(
            str(context.exception),
            "OAuth provider must be specified to retrieve an OAuth token.",
        )

    def test_get_oauth_token_user_not_linked(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            authentication_method="oauth",
            oauth_provider="test_provider",
        )

        mock_user = mock.MagicMock()
        mock_user.social_auth.get.side_effect = ObjectDoesNotExist

        with self.assertRaises(ValueError) as context:
            secure_map_service.get_oauth_token(user=mock_user)
        self.assertEqual(str(context.exception), "User not linked to test_provider.")

    def test_get_oauth_token_no_token(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            authentication_method="oauth",
            oauth_provider="test_provider",
        )

        mock_user = mock.MagicMock()
        mock_user.social_auth.get.return_value.extra_data = {}

        with self.assertRaises(ValueError) as context:
            secure_map_service.get_oauth_token(user=mock_user)
        self.assertEqual(str(context.exception), "No access token found for user.")

    def test_get_oauth_token_success(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            authentication_method="oauth",
            oauth_provider="test_provider",
        )

        mock_user = mock.MagicMock()
        mock_user.social_auth.get.return_value.extra_data = {
            "access_token": "access_token12345"
        }

        token = secure_map_service.get_oauth_token(user=mock_user)
        self.assertEqual(token, "access_token12345")

    def test_get_resolved_params(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            authentication_method="api_key",
            params=None,
        )

        result = secure_map_service.get_resolved_params()
        self.assertEqual(result, {})

    def test_get_resolved_params_with_api_key(self):
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

        resolved_params = secure_map_service.get_resolved_params()
        self.assertEqual(
            resolved_params,
            {"param1": "value1", "param2": "value2", "test_api_key": "api_key_12345"},
        )

    def test_get_resolved_params_with_missing_api_key(self):
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

        resolved_params = secure_map_service.get_resolved_params()
        self.assertEqual(
            resolved_params,
            {"param1": "value1", "param2": "value2", "test_api_key": ""},
        )

    def test_get_resolved_params_with_multiple_params(self):
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

        resolved_params = secure_map_service.get_resolved_params()
        self.assertEqual(
            resolved_params,
            {
                "param1": "value1",
                "name": "test_secure_map_service",
                "test_api_key": "api_key_12345",
            },
        )
