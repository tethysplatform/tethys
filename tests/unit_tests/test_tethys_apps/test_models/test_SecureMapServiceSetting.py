from tethys_sdk.testing import TethysTestCase
from tethys_apps.models import TethysApp, SecureMapServiceSetting
from tethys_sdk.gizmos import MVLayer
from tethys_services.models import SecureMapService
from django.core.exceptions import ValidationError
from tethys_apps.exceptions import TethysAppSettingNotAssigned
from unittest import mock


class SecureMapServiceSettingTests(TethysTestCase):
    def set_up(self):
        self.test_app = TethysApp.objects.get(package="test_app")
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

    def test_clean_validation_error(self):
        setting = self.test_app.settings_set.select_subclasses().get(
            name="secure_map_service"
        )
        setting.secure_map_service = None
        setting.save()
        self.assertRaises(
            ValidationError,
            self.test_app.settings_set.select_subclasses()
            .get(name="secure_map_service")
            .clean,
        )

    def test_get_value_none(self):
        setting = self.test_app.settings_set.select_subclasses().get(
            name="secure_map_service"
        )
        setting.secure_map_service = None
        setting.save()

        self.assertRaises(
            TethysAppSettingNotAssigned,
            SecureMapServiceSetting.objects.get(name="secure_map_service").get_value,
        )

    def test_get_value_as_endpoint(self):
        setting = self.test_app.settings_set.select_subclasses().get(
            name="secure_map_service"
        )
        setting.secure_map_service = self.map_service_with_api_key_no_proxy
        setting.save()

        endpoint = SecureMapServiceSetting.objects.get(
            name="secure_map_service"
        ).get_value(as_endpoint=True)

        self.assertEqual(
            endpoint,
            "https://example.com/map_service?param1=value1&api_key=test_api_key",
        )

    def test_get_value_as_endpoint_with_overrides(self):
        setting = self.test_app.settings_set.select_subclasses().get(
            name="secure_map_service"
        )
        setting.secure_map_service = self.map_service_with_api_key_no_proxy
        setting.save()

        endpoint = SecureMapServiceSetting.objects.get(
            name="secure_map_service"
        ).get_value(
            as_endpoint=True,
            param_overrides={"param1": "overridden_value", "param2": "value2"},
        )

        self.assertEqual(
            endpoint,
            "https://example.com/map_service?param1=overridden_value&api_key=test_api_key&param2=value2",
        )

    def test_get_value_as_layer(self):
        setting = self.test_app.settings_set.select_subclasses().get(
            name="secure_map_service"
        )
        setting.secure_map_service = self.map_service_with_api_key_no_proxy
        setting.save()

        layer = SecureMapServiceSetting.objects.get(
            name="secure_map_service"
        ).get_value(as_layer=True)

        self.assertIsInstance(layer, MVLayer)
        self.assertEqual(layer["source"], setting.secure_map_service.service_type)
        self.assertEqual(
            layer["options"]["url"],
            "https://example.com/map_service?param1=value1&api_key=test_api_key",
        )

    def test_get_value_as_layer_with_overrides(self):
        setting = self.test_app.settings_set.select_subclasses().get(
            name="secure_map_service"
        )
        setting.secure_map_service = self.map_service_with_api_key_no_proxy
        setting.save()

        layer = SecureMapServiceSetting.objects.get(
            name="secure_map_service"
        ).get_value(
            as_layer=True,
            param_overrides={"param1": "overridden_value", "param2": "value2"},
        )

        self.assertIsInstance(layer, MVLayer)
        self.assertEqual(layer["source"], setting.secure_map_service.service_type)
        self.assertEqual(
            layer["options"]["url"],
            "https://example.com/map_service?param1=overridden_value&api_key=test_api_key&param2=value2",
        )

    def test_get_value_as_layer_with_source_options(self):
        setting = self.test_app.settings_set.select_subclasses().get(
            name="secure_map_service"
        )
        setting.secure_map_service = self.map_service_with_api_key_no_proxy
        setting.save()

        layer = SecureMapServiceSetting.objects.get(
            name="secure_map_service"
        ).get_value(
            as_layer=True,
            source_options={"custom_option": "custom_value"},
        )

        self.assertIsInstance(layer, MVLayer)
        self.assertEqual(layer["source"], setting.secure_map_service.service_type)
        self.assertEqual(
            layer["options"]["url"],
            "https://example.com/map_service?param1=value1&api_key=test_api_key",
        )
        self.assertEqual(layer["options"]["custom_option"], "custom_value")

    def test_get_value_as_layer_with_layer_options(self):
        setting = self.test_app.settings_set.select_subclasses().get(
            name="secure_map_service"
        )
        setting.secure_map_service = self.map_service_with_api_key_no_proxy
        setting.save()

        layer = SecureMapServiceSetting.objects.get(
            name="secure_map_service"
        ).get_value(
            as_layer=True,
            layer_options={"custom_layer_option": "custom_layer_value"},
        )

        self.assertIsInstance(layer, MVLayer)
        self.assertEqual(layer["source"], setting.secure_map_service.service_type)
        self.assertEqual(
            layer["options"]["url"],
            "https://example.com/map_service?param1=value1&api_key=test_api_key",
        )
        self.assertEqual(
            layer["layer_options"]["custom_layer_option"], "custom_layer_value"
        )

    @mock.patch("tethys_services.models.requests.get")
    def test_get_value_as_response(self, mock_get):
        setting = self.test_app.settings_set.select_subclasses().get(
            name="secure_map_service"
        )
        setting.secure_map_service = self.map_service_with_api_key_no_proxy
        setting.save()

        mock_response = mock.MagicMock(
            status_code=200,
            ok=True,
            url="https://example.com/map_service?param1=value1&api_key=test_api_key",
        )
        mock_get.return_value = mock_response

        response = SecureMapServiceSetting.objects.get(
            name="secure_map_service"
        ).get_value(as_response=True)

        self.assertEqual(
            response.url,
            "https://example.com/map_service?param1=value1&api_key=test_api_key",
        )
        self.assertEqual(response.status_code, 200)

    @mock.patch("tethys_services.models.requests.get")
    def test_get_value_as_response_with_overrides(self, mock_get):
        setting = self.test_app.settings_set.select_subclasses().get(
            name="secure_map_service"
        )
        setting.secure_map_service = self.map_service_with_api_key_no_proxy
        setting.save()

        mock_response = mock.MagicMock(
            status_code=200,
            ok=True,
            url="https://example.com/map_service?param1=overridden_value&api_key=test_api_key&param2=value2",
        )
        mock_get.return_value = mock_response

        response = SecureMapServiceSetting.objects.get(
            name="secure_map_service"
        ).get_value(
            as_response=True,
            param_overrides={"param1": "overridden_value", "param2": "value2"},
        )

        self.assertEqual(
            response.url,
            "https://example.com/map_service?param1=overridden_value&api_key=test_api_key&param2=value2",
        )
        self.assertEqual(response.status_code, 200)

    def test_get_value_get_service(self):
        setting = self.test_app.settings_set.select_subclasses().get(
            name="secure_map_service"
        )
        setting.secure_map_service = self.map_service_with_api_key_no_proxy
        setting.save()

        service = SecureMapServiceSetting.objects.get(
            name="secure_map_service"
        ).get_value()

        self.assertEqual(service, setting.secure_map_service)

    def test_get_value_as_token_no_user(self):
        setting = self.test_app.settings_set.select_subclasses().get(
            name="secure_map_service"
        )
        setting.secure_map_service = self.map_service_with_api_key_no_proxy
        setting.save()

        with self.assertRaises(ValueError) as context:
            SecureMapServiceSetting.objects.get(name="secure_map_service").get_value(
                as_token=True
            )

        self.assertIn(
            "request_user must be provided to retrieve an OAuth2 token.",
            str(context.exception),
        )

    @mock.patch("tethys_apps.models.SecureMapService._get_oauth_token")
    def test_get_value_as_token(self, mock_get_oauth_token):
        mock_get_oauth_token.return_value = "test_token"
        setting = self.test_app.settings_set.select_subclasses().get(
            name="secure_map_service"
        )
        setting.secure_map_service = self.map_service_with_api_key_no_proxy
        setting.save()

        token = SecureMapServiceSetting.objects.get(
            name="secure_map_service"
        ).get_value(as_token=True, request_user="test_user")

        self.assertEqual(token, "test_token")

    def test_update_params_none(self):
        setting = self.test_app.settings_set.select_subclasses().get(
            name="secure_map_service"
        )
        setting.secure_map_service = None
        setting.save()

        self.assertRaises(
            TethysAppSettingNotAssigned,
            SecureMapServiceSetting.objects.get(
                name="secure_map_service"
            )._update_params,
            {"param1": "new_value"},
        )

    def test_update_params(self):
        setting = self.test_app.settings_set.select_subclasses().get(
            name="secure_map_service"
        )
        setting.secure_map_service = self.map_service_with_api_key_no_proxy
        setting.save()

        new_params = {"param1": "new_value", "param3": "value3"}
        SecureMapServiceSetting.objects.get(name="secure_map_service")._update_params(
            new_params
        )

        updated_service = SecureMapService.objects.get(pk=setting.secure_map_service.pk)
        expected_params = {
            "param1": "new_value",
            "api_key": "${api_key}",
            "param3": "value3",
        }
        self.assertEqual(updated_service.params, expected_params)

    def test_get_value_as_endpoint_none(self):
        setting = self.test_app.settings_set.select_subclasses().get(
            name="secure_map_service"
        )
        setting.required = False
        setting.secure_map_service = None
        setting.save()

        with self.assertRaises(TethysAppSettingNotAssigned) as e:
            SecureMapServiceSetting.objects.get(name="secure_map_service").get_value(
                as_endpoint=True
            )
            assert (
                str(e.exception)
                == f'Cannot generate request for SecureMapServiceSetting "{setting.name}" for app "{self.test_app.package}": no SecureMapService assigned."'
            )

    def test_get_value_as_layer_none(self):
        setting = self.test_app.settings_set.select_subclasses().get(
            name="secure_map_service"
        )
        setting.required = False
        setting.secure_map_service = None
        setting.save()

        with self.assertRaises(TethysAppSettingNotAssigned) as e:
            SecureMapServiceSetting.objects.get(name="secure_map_service").get_value(
                as_layer=True
            )
            assert (
                str(e.exception)
                == f'Cannot build layer for SecureMapServiceSetting "{setting.name}" for app "{self.test_app.package}": no SecureMapService assigned."'
            )

    def test_get_value_as_response_none(self):
        setting = self.test_app.settings_set.select_subclasses().get(
            name="secure_map_service"
        )
        setting.required = False
        setting.secure_map_service = None
        setting.save()

        with self.assertRaises(TethysAppSettingNotAssigned) as e:
            SecureMapServiceSetting.objects.get(name="secure_map_service").get_value(
                as_response=True, request_user=self.test_user
            )
            assert (
                str(e.exception)
                == f'Cannot fetch response for SecureMapServiceSetting "{setting.name}" for app "{self.test_app.package}": no SecureMapService assigned."'
            )
