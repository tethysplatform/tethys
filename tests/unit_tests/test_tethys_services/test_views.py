import unittest
from unittest import mock

from tethys_services.views import datasets_home, wps_home, wps_service, wps_process


class TethysServicesViewsTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch("tethys_services.views.render")
    def test_datasets_home(self, mock_render):
        mock_request = mock.MagicMock()
        mock_render.return_value = "datasets_home"
        context = {}

        self.assertEqual("datasets_home", datasets_home(mock_request))
        mock_render.assert_called_once_with(
            mock_request, "tethys_services/tethys_datasets/home.html", context
        )

    @mock.patch("tethys_services.views.list_wps_service_engines")
    @mock.patch("tethys_services.views.render")
    def test_wps_home(self, mock_render, mock_list_wps_service_engines):
        mock_request = mock.MagicMock()
        mock_render.return_value = "wps_home"
        mock_wps = mock.MagicMock()
        mock_list_wps_service_engines.return_value = mock_wps
        context = {"wps_services": mock_wps}

        self.assertEqual("wps_home", wps_home(mock_request))
        mock_render.assert_called_once_with(
            mock_request, "tethys_services/tethys_wps/home.html", context
        )

    @mock.patch("tethys_services.views.get_wps_service_engine")
    @mock.patch("tethys_services.views.render")
    def test_wps_service(self, mock_render, mock_get_wps_service_engine):
        mock_request = mock.MagicMock()
        mock_service = mock.MagicMock()
        mock_render.return_value = "wps_service"
        mock_wps = mock.MagicMock()
        mock_get_wps_service_engine.return_value = mock_wps
        context = {"wps": mock_wps, "service": mock_service}

        self.assertEqual("wps_service", wps_service(mock_request, mock_service))
        mock_render.assert_called_once_with(
            mock_request, "tethys_services/tethys_wps/service.html", context
        )
        mock_get_wps_service_engine.assert_called_once_with(mock_service)

    @mock.patch("tethys_services.views.abstract_is_link")
    @mock.patch("tethys_services.views.get_wps_service_engine")
    @mock.patch("tethys_services.views.render")
    def test_wps_process(
        self, mock_render, mock_get_wps_service_engine, mock_abstract_is_link
    ):
        mock_request = mock.MagicMock()
        mock_service = mock.MagicMock()
        mock_identifier = mock.MagicMock()
        mock_wps_process = mock.MagicMock()
        mock_render.return_value = "wps_process"
        mock_wps = mock.MagicMock()
        mock_wps.describeprocess.return_value = mock_wps_process
        mock_get_wps_service_engine.return_value = mock_wps

        self.assertEqual(
            "wps_process", wps_process(mock_request, mock_service, mock_identifier)
        )
        mock_render.assert_called_once()
        mock_get_wps_service_engine.assert_called_once_with(mock_service)
        mock_abstract_is_link.assert_called_once_with(mock_wps_process)
        mock_wps.describeprocess.assert_called_once_with(mock_identifier)
