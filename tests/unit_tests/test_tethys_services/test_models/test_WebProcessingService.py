from tethys_sdk.testing import TethysTestCase
import tethys_services.models as service_model
from unittest import mock

from tethys_services.models import HTTPError, URLError


class WebProcessingServiceTests(TethysTestCase):
    def set_up(self):
        pass

    def tear_down(self):
        pass

    def test_unicode(self):
        wps = service_model.WebProcessingService(
            name="test_sds",
        )
        self.assertEqual("test_sds", str(wps))

    def test_activate(self):
        wps = service_model.WebProcessingService(
            name="test_sds",
            endpoint="http://localhost/geoserver/rest/",
            public_endpoint="http://publichost/geoserver/rest/",
            username="foo",
            password="password",
        )
        wps.save()
        # Check result
        mock_wps = mock.MagicMock()
        mock_wps.getcapabilities.return_value = "test"

        ret = wps.activate(mock_wps)

        mock_wps.getcapabilities.assert_called()
        self.assertEqual(mock_wps, ret)

    def test_activate_http_error_404(self):
        wps = service_model.WebProcessingService(
            name="test_sds",
            endpoint="http://localhost/geoserver/rest/",
            public_endpoint="http://publichost/geoserver/rest/",
            username="foo",
            password="password",
        )

        # Check result
        mock_wps = mock.MagicMock()
        mock_wps.getcapabilities.side_effect = HTTPError(
            url="test_url", code=404, msg="test_message", hdrs="test_header", fp=None
        )

        self.assertRaises(HTTPError, wps.activate, mock_wps)

    def test_activate_http_error_not_404(self):
        wps = service_model.WebProcessingService(
            name="test_sds",
            endpoint="http://localhost/geoserver/rest/",
            public_endpoint="http://publichost/geoserver/rest/",
            username="foo",
            password="password",
        )

        # Check result
        mock_wps = mock.MagicMock()
        mock_wps.getcapabilities.side_effect = HTTPError(
            url="test_url", code=500, msg="test_message", hdrs="test_header", fp=None
        )

        self.assertRaises(HTTPError, wps.activate, mock_wps)

    def test_activate_url_error(self):
        wps = service_model.WebProcessingService(
            name="test_sds",
            endpoint="http://localhost/geoserver/rest/",
            public_endpoint="http://publichost/geoserver/rest/",
            username="foo",
            password="password",
        )

        # Check result
        mock_wps = mock.MagicMock()
        mock_wps.getcapabilities.side_effect = URLError(reason="test_url")

        ret = wps.activate(mock_wps)

        self.assertIsNone(ret)

    def test_activate_error(self):
        wps = service_model.WebProcessingService(
            name="test_sds",
            endpoint="http://localhost/geoserver/rest/",
            public_endpoint="http://publichost/geoserver/rest/",
            username="foo",
            password="password",
        )

        # Check result
        mock_wps = mock.MagicMock()
        mock_wps.getcapabilities.side_effect = Exception

        self.assertRaises(Exception, wps.activate, mock_wps)

    @mock.patch("tethys_services.models.WebProcessingService.activate")
    @mock.patch("tethys_services.models.WPS")
    def test_get_engine(self, mock_wps, mock_activate):
        wps = service_model.WebProcessingService(
            name="test_sds",
            endpoint="http://localhost/geoserver/rest/",
            public_endpoint="http://publichost/geoserver/rest/",
            username="foo",
            password="password",
        )
        wps.save()
        # Execute
        wps.get_engine()

        # Check called
        mock_wps.assert_called_with(
            "http://localhost/geoserver/rest/",
            password="password",
            skip_caps=True,
            username="foo",
            verbose=False,
        )
        mock_activate.assert_called_with(wps=mock_wps())
