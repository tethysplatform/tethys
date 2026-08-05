import pytest
import requests
from tethys_sdk.testing import TethysTestCase
from tethys_apps.models import TethysApp, SecureMapServiceSetting
from tethys_sdk.gizmos import MVLayer
from tethys_services.models import SecureMapService
from django.core.exceptions import ValidationError
from tethys_apps.exceptions import TethysAppSettingNotAssigned
from django.utils.functional import Promise
from django.utils.encoding import force_str
from unittest import mock


class SecureMapServiceSettingTests(TethysTestCase):
    def set_up(self):
        self.test_app = TethysApp.objects.get(package="test_app")
        self.test_user = self.create_test_user(username="testuser", password="testpassword")

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
            use_proxy=False
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
            use_proxy=False
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
            use_proxy=True
        )
        self.map_service_with_api_key_with_proxy.save()

        self.map_service_with_oauth_no_proxy = SecureMapService(
            name="oauth_no_proxy",
            legend_title="Map Service with OAuth No Proxy",
            endpoint="https://example.com/map_service",
            authentication_method="oauth",
            oauth_provider="test_oauth_provider",
            service_type="geojson",
            params=self.params_without_api_key,
            use_proxy=False
        )
        self.map_service_with_oauth_no_proxy.save()

        self.map_service_with_oauth_with_proxy = SecureMapService(
            name="oauth_with_proxy",
            legend_title="Map Service with OAuth With Proxy",
            endpoint="https://example.com/map_service",
            authentication_method="oauth",
            oauth_provider="test_oauth_provider",
            service_type="WMS",
            params=self.params_without_api_key,
            use_proxy=True
        )
        self.map_service_with_oauth_with_proxy.save()

    def tear_down(self):
        self.map_service_with_api_key_no_proxy.delete()
        self.map_service_with_api_key_with_proxy.delete()
        self.map_service_without_api_key_param_no_proxy.delete()
        self.map_service_with_oauth_no_proxy.delete()
        self.map_service_with_oauth_with_proxy.delete()

    def test_clean_validation_error(self):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = None
        setting.save()
        self.assertRaises(
            ValidationError, self.test_app.settings_set.select_subclasses().get(name="secure_map_service").clean,
        )

    def test__generate_request_none(self):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = None
        setting.save()

        self.assertRaises(
            TethysAppSettingNotAssigned,
            SecureMapServiceSetting.objects.get(name="secure_map_service")._generate_request,
        )

    def test__generate_request_with_proxy(self):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = self.map_service_with_api_key_with_proxy
        setting.save()

        url = SecureMapServiceSetting.objects.get(name="secure_map_service")._generate_request()

        self.assertIsInstance(url, Promise)
        self.assertEqual(f"/secure-map-proxy/{setting.secure_map_service.pk}/", force_str(url))
        
    def test__generate_request_without_proxy_with_api_key(self):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = self.map_service_with_api_key_no_proxy
        setting.save()

        url = SecureMapServiceSetting.objects.get(name="secure_map_service")._generate_request()

        self.assertEqual(
            url,
            "https://example.com/map_service?param1=value1&api_key=test_api_key"
        )

    def test__generate_request_without_proxy_without_api_key_param(self):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = self.map_service_without_api_key_param_no_proxy
        setting.save()

        url = SecureMapServiceSetting.objects.get(name="secure_map_service")._generate_request()

        self.assertEqual(
            url,
            "https://example.com/map_service?param1=value1&api_key=test_api_key"
        )

    def test__generate_request_param_overrides(self):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = self.map_service_with_api_key_no_proxy
        setting.save()

        url = SecureMapServiceSetting.objects.get(name="secure_map_service")._generate_request(
            param_overrides={"param1": "overridden_value", "param2": "value2"}
        )

        self.assertEqual(
            url,
            "https://example.com/map_service?param1=overridden_value&api_key=test_api_key&param2=value2"
        )

    def test__build_layer_none(self):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = None
        setting.save()

        self.assertRaises(
            TethysAppSettingNotAssigned,
            SecureMapServiceSetting.objects.get(name="secure_map_service")._build_layer,
        )

    def test__build_layer_with_api_key(self):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = self.map_service_with_api_key_no_proxy
        setting.save()

        layer = SecureMapServiceSetting.objects.get(name="secure_map_service")._build_layer()

        self.assertEqual(layer["source"], setting.secure_map_service.service_type)

        self.assertEqual(
            layer["options"]["url"],
            "https://example.com/map_service?param1=value1&api_key=test_api_key"
        )

    def test__build_layer_without_api_key_param(self):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = self.map_service_without_api_key_param_no_proxy
        setting.save()

        layer = SecureMapServiceSetting.objects.get(name="secure_map_service")._build_layer()

        self.assertEqual(layer["source"], setting.secure_map_service.service_type)
        self.assertEqual(
            layer["options"]["url"],
            "https://example.com/map_service?param1=value1&api_key=test_api_key"
        )

    def test__build_layer_with_proxy(self):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = self.map_service_with_api_key_with_proxy
        setting.save()

        layer = SecureMapServiceSetting.objects.get(name="secure_map_service")._build_layer()

        self.assertEqual(layer["source"], setting.secure_map_service.service_type)
        self.assertIsInstance(layer["options"]["url"], Promise)
        self.assertEqual(
            force_str(layer["options"]["url"]),
            f"/secure-map-proxy/{setting.secure_map_service.pk}/"
        )

    def test__build_layer_param_overrides(self):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = self.map_service_with_api_key_no_proxy
        setting.save()

        layer = SecureMapServiceSetting.objects.get(name="secure_map_service")._build_layer(
            param_overrides={"param1": "overridden_value", "param2": "value2"}
        )

        self.assertEqual(layer["source"], setting.secure_map_service.service_type)
        self.assertEqual(
            layer["options"]["url"],
            "https://example.com/map_service?param1=overridden_value&api_key=test_api_key&param2=value2"
        )

    @mock.patch("tethys_services.models.SecureMapService.get_oauth_token", return_value="test_oauth_token")
    def test__build_Layer_oauth(self, mock_got):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = self.map_service_with_oauth_no_proxy
        setting.save()

        layer = SecureMapServiceSetting.objects.get(name="secure_map_service")._build_layer(request_user=self.test_user)

        self.assertEqual(layer["source"], setting.secure_map_service.service_type)
        self.assertEqual(
            layer["options"]["url"],
            "https://example.com/map_service?param1=value1"
        )
        self.assertEqual(
            layer["options"]["token"], "test_oauth_token"
        )

    def test__build_Layer_oauth_no_request_user(self):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = self.map_service_with_oauth_no_proxy
        setting.save()

        self.assertRaises(
            ValueError,
            SecureMapServiceSetting.objects.get(name="secure_map_service")._build_layer,
            request_user=None
        )

    def test__fetch_response_none(self):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = None
        setting.save()

        self.assertRaises(
            TethysAppSettingNotAssigned,
            SecureMapServiceSetting.objects.get(name="secure_map_service")._fetch_response,
        )

    def test__fetch_response_no_request_user(self):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = self.map_service_with_oauth_no_proxy
        setting.save()

        self.assertRaises(
            ValueError,
            SecureMapServiceSetting.objects.get(name="secure_map_service")._fetch_response,
            request_user=None
        )

    @mock.patch("tethys_apps.models.requests.get")
    def test__fetch_response_with_api_key(self, mock_get):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = self.map_service_with_api_key_no_proxy
        setting.save()

        mock_response = mock.MagicMock(
            status_code=200,
            ok=True,
            url="https://example.com/map_service?param1=value1&api_key=test_api_key",
        )
        mock_get.return_value = mock_response

        response = SecureMapServiceSetting.objects.get(name="secure_map_service")._fetch_response()
        
        self.assertEqual(
            response.url,
            "https://example.com/map_service?param1=value1&api_key=test_api_key"
        )
        self.assertEqual(response.status_code, 200)

    @mock.patch("tethys_apps.models.SecureMapService.get_oauth_token", return_value="test_oauth_token")
    @mock.patch("tethys_apps.models.requests.get")
    def test__fetch_response_with_oauth_header(self, mock_get, mock_got):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = self.map_service_with_oauth_no_proxy
        setting.save()

        mock_response = mock.MagicMock(
            status_code=200,
            ok=True,
            url="https://example.com/map_service?param1=value1",
        )
        mock_get.return_value = mock_response

        response = SecureMapServiceSetting.objects.get(name="secure_map_service")._fetch_response(request_user=self.test_user)

        mock_got.assert_called_once_with(self.test_user)

        self.assertEqual(
            response.url,
            "https://example.com/map_service?param1=value1"
        )
        self.assertEqual(response.status_code, 200)

    @mock.patch("tethys_apps.models.log")
    @mock.patch("tethys_apps.models.SecureMapService.get_oauth_token", return_value="test_oauth_token")
    @mock.patch("tethys_apps.models.requests.get")
    def test__fetch_response_with_oauth_response_not_ok(self, mock_get, mock_got, mock_log):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = self.map_service_with_oauth_no_proxy
        setting.save()

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
            SecureMapServiceSetting.objects.get(name="secure_map_service")._fetch_response(request_user=self.test_user)
    
        mock_got.assert_called_once_with(self.test_user)
        mock_log.error.assert_called_once()
        logged = mock_log.error.call_args.args[0]
        self.assertIn(f"SecureMapService with name {setting.secure_map_service.name} request failed", logged)
        self.assertIn("status_code: 403", logged)
        self.assertIn("Forbidden access message", logged)

    @mock.patch("tethys_apps.models.SecureMapService.get_oauth_token", return_value="test_oauth_token")
    @mock.patch("tethys_apps.models.requests.get")
    def test__fetch_response_with_oauth_good_response(self, mock_get, mock_got):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = self.map_service_with_oauth_no_proxy
        setting.save()

        mock_response = mock.MagicMock(
            status_code=200,
            ok=True,
            url="https://example.com/map_service?param1=value1",
        )
        mock_get.return_value = mock_response

        response = SecureMapServiceSetting.objects.get(name="secure_map_service")._fetch_response(request_user=self.test_user)

        mock_got.assert_called_once_with(self.test_user)

        self.assertEqual(
            response, mock_response
        )
        self.assertEqual(response.status_code, 200)

    @mock.patch("tethys_apps.models.requests.get")
    def test__fetch_response_with_api_key_with_overrides(self, mock_get):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = self.map_service_with_api_key_no_proxy
        setting.save()

        mock_response = mock.MagicMock(
            status_code=200,
            ok=True,
            url="https://example.com/map_service?param1=overridden_value&api_key=test_api_key&param2=value2",
        )
        mock_get.return_value = mock_response

        response = SecureMapServiceSetting.objects.get(name="secure_map_service")._fetch_response(
            param_overrides={"param1": "overridden_value", "param2": "value2"}
        )

        self.assertEqual(
            response.url,
            "https://example.com/map_service?param1=overridden_value&api_key=test_api_key&param2=value2"
        )
        self.assertEqual(response.status_code, 200)

    def test_get_value_none(self):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = None
        setting.save()

        self.assertRaises(
            TethysAppSettingNotAssigned,
            SecureMapServiceSetting.objects.get(name="secure_map_service").get_value,
        )

    
    def test_get_value_as_endpoint(self):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = self.map_service_with_api_key_no_proxy
        setting.save()

        endpoint = SecureMapServiceSetting.objects.get(name="secure_map_service").get_value(as_endpoint=True)

        self.assertEqual(
            endpoint,
            "https://example.com/map_service?param1=value1&api_key=test_api_key"
        )

    def test_get_value_as_endpoint_with_overrides(self):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = self.map_service_with_api_key_no_proxy
        setting.save()

        endpoint = SecureMapServiceSetting.objects.get(name="secure_map_service").get_value(
            as_endpoint=True,
            param_overrides={"param1": "overridden_value", "param2": "value2"}
        )

        self.assertEqual(
            endpoint,
            "https://example.com/map_service?param1=overridden_value&api_key=test_api_key&param2=value2"
        )

    def test_get_value_as_layer(self):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = self.map_service_with_api_key_no_proxy
        setting.save()

        layer = SecureMapServiceSetting.objects.get(name="secure_map_service").get_value(as_layer=True)

        self.assertIsInstance(layer, MVLayer)
        self.assertEqual(layer["source"], setting.secure_map_service.service_type)
        self.assertEqual(
            layer["options"]["url"],
            "https://example.com/map_service?param1=value1&api_key=test_api_key"
        )

    def test_get_value_as_layer_with_overrides(self):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = self.map_service_with_api_key_no_proxy
        setting.save()

        layer = SecureMapServiceSetting.objects.get(name="secure_map_service").get_value(
            as_layer=True,
            param_overrides={"param1": "overridden_value", "param2": "value2"}
        )

        self.assertIsInstance(layer, MVLayer)
        self.assertEqual(layer["source"], setting.secure_map_service.service_type)
        self.assertEqual(
            layer["options"]["url"],
            "https://example.com/map_service?param1=overridden_value&api_key=test_api_key&param2=value2"
        )

    @mock.patch("tethys_apps.models.requests.get")
    def test_get_value_as_response(self, mock_get):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = self.map_service_with_api_key_no_proxy
        setting.save()
        
        mock_response = mock.MagicMock(
            status_code=200,
            ok=True,
            url="https://example.com/map_service?param1=value1&api_key=test_api_key",
        )
        mock_get.return_value = mock_response

        response = SecureMapServiceSetting.objects.get(name="secure_map_service").get_value(as_response=True)

        self.assertEqual(
            response.url,
            "https://example.com/map_service?param1=value1&api_key=test_api_key"
        )
        self.assertEqual(response.status_code, 200)

    @mock.patch("tethys_apps.models.requests.get")
    def test_get_value_as_response_with_overrides(self, mock_get):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = self.map_service_with_api_key_no_proxy
        setting.save()
        
        mock_response = mock.MagicMock(
            status_code=200,
            ok=True,
            url="https://example.com/map_service?param1=overridden_value&api_key=test_api_key&param2=value2",
        )
        mock_get.return_value = mock_response

        response = SecureMapServiceSetting.objects.get(name="secure_map_service").get_value(
            as_response=True,
            param_overrides={"param1": "overridden_value", "param2": "value2"}
        )

        self.assertEqual(
            response.url,
            "https://example.com/map_service?param1=overridden_value&api_key=test_api_key&param2=value2"
        )
        self.assertEqual(response.status_code, 200)

    def test_get_value_get_service(self):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = self.map_service_with_api_key_no_proxy
        setting.save()

        service = SecureMapServiceSetting.objects.get(name="secure_map_service").get_value()

        self.assertEqual(service, setting.secure_map_service)

    def test_update_params_none(self):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = None
        setting.save()

        self.assertRaises(
            TethysAppSettingNotAssigned,
            SecureMapServiceSetting.objects.get(name="secure_map_service").update_params,
            {"param1": "new_value"}
        )

    def test_update_params(self):
        setting = self.test_app.settings_set.select_subclasses().get(name="secure_map_service")
        setting.secure_map_service = self.map_service_with_api_key_no_proxy
        setting.save()

        new_params = {"param1": "new_value", "param3": "value3"}
        SecureMapServiceSetting.objects.get(name="secure_map_service").update_params(new_params)

        updated_service = SecureMapService.objects.get(pk=setting.secure_map_service.pk)
        expected_params = {"param1": "new_value", "api_key": "${api_key}", "param3": "value3"}
        self.assertEqual(updated_service.params, expected_params)