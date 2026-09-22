from tethys_sdk.testing import TethysTestCase
from tethys_services.models import SecureMapService
from unittest import mock
from django.core.exceptions import ObjectDoesNotExist, ValidationError


class SecureMapServiceTests(TethysTestCase):
    def test_str(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service", endpoint="http://example.com"
        )
        self.assertEqual("test_secure_map_service", str(secure_map_service))

    def test_clean_invalid_params(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            params="invalid_params"
        )

        with self.assertRaises(ValidationError) as context:
            secure_map_service.clean()
        self.assertEqual({"params": ['Parameters must be a JSON object (e.g. {"key": "value"})']}, context.exception.message_dict)

    def test_get_oauth_token_api_key(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            authentication_method="api_key",
        )

        with self.assertRaises(ValueError) as context:
            secure_map_service._get_oauth_token(user=None)
        self.assertEqual(
            str(context.exception),
            "Authentication method must be 'oauth2' to retrieve an OAuth2 token.",
        )

    def test_get_oauth_token_no_provider(self):
        secure_map_service = SecureMapService(
            name="test_secure_map_service",
            endpoint="http://example.com",
            authentication_method="oauth2",
        )

        with self.assertRaises(ValueError) as context:
            secure_map_service._get_oauth_token(user=None)
        self.assertEqual(
            str(context.exception),
            "OAuth2 provider must be specified to retrieve an OAuth2 token.",
        )

    def test_get_oauth_token_user_not_linked(self):
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

    def test_get_oauth_token_no_token(self):
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
        mock_user.social_auth.get.return_value.get_access_token.side_effect = AuthException(mock.MagicMock(), "access token failure")

        with self.assertRaises(ValueError) as context:
            secure_map_service._get_oauth_token(user=mock_user)
        self.assertEqual(
            str(context.exception),
            f"Failed to retrieve access Oauth2 token for {secure_map_service.oauth2_provider}: access token failure"
        )

    def test_get_oauth_token_success(self):
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

    def test_get_resolved_params(self):
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

        resolved_params = secure_map_service._get_resolved_params()
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

        self.assertEqual(str(context.exception), "new_params must be a JSON object (dict).")

        


