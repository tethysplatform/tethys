from unittest import mock
from tethys_sdk.testing import TethysTestCase
from tethys_apps.models import TethysApp
from tethys_apps.exceptions import TethysAppSettingNotAssigned
from django.core.exceptions import ValidationError
from tethys_services.models import SpatialDatasetService


class SpatialDatasetServiceTests(TethysTestCase):
    def set_up(self):
        self.test_app = TethysApp.objects.get(package="test_app")

        pass

    def tear_down(self):
        pass

    def test_clean(self):
        sds_setting = self.test_app.settings_set.select_subclasses().get(
            name="primary_geoserver"
        )
        sds_setting.spatial_dataset_service = None
        sds_setting.save()
        # Check ValidationError
        self.assertRaises(
            ValidationError,
            self.test_app.settings_set.select_subclasses()
            .get(name="primary_geoserver")
            .clean,
        )

    def test_get_value(self):
        sds = SpatialDatasetService(
            name="test_sds",
            endpoint="http://localhost/geoserver/rest/",
            public_endpoint="http://publichost/geoserver/rest/",
            apikey="test_api",
            username="foo",
            password="password",
        )
        sds.save()
        sds_setting = self.test_app.settings_set.select_subclasses().get(
            name="primary_geoserver"
        )
        sds_setting.spatial_dataset_service = sds
        sds_setting.save()

        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="primary_geoserver")
            .get_value()
        )

        # Check result
        self.assertEqual("test_sds", ret.name)
        self.assertEqual("http://localhost/geoserver/rest/", ret.endpoint)
        self.assertEqual("http://publichost/geoserver/rest/", ret.public_endpoint)
        self.assertEqual("test_api", ret.apikey)
        self.assertEqual("foo", ret.username)
        self.assertEqual("password", ret.password)

    def test_get_value_NotAssigned(self):
        sds_setting = self.test_app.settings_set.select_subclasses().get(
            name="primary_geoserver"
        )
        sds_setting.spatial_dataset_service = None
        sds_setting.save()
        self.assertRaises(
            TethysAppSettingNotAssigned,
            self.test_app.settings_set.select_subclasses()
            .get(name="primary_geoserver")
            .get_value,
        )

    def test_get_value_check_if_geoserver(self):
        sds = SpatialDatasetService(
            name="test_sds",
            engine=SpatialDatasetService.GEOSERVER,
            endpoint="http://localhost/geoserver/rest/",
            public_endpoint="http://publichost/geoserver/rest/",
            apikey="test_api",
            username="foo",
            password="password",
        )
        sds.save()
        sds_setting = self.test_app.settings_set.select_subclasses().get(
            name="primary_geoserver"
        )
        sds_setting.spatial_dataset_service = sds
        sds_setting.save()

        # Check as_engine
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="primary_geoserver")
            .get_value(as_engine=True)
        )
        # Check result
        self.assertEqual("GEOSERVER", ret.type)
        self.assertEqual("http://localhost/geoserver/rest/", ret.endpoint)

        # Check as wms
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="primary_geoserver")
            .get_value(as_wms=True)
        )
        # Check result
        self.assertEqual("http://localhost/geoserver/wms", ret)

        # Check as wfs
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="primary_geoserver")
            .get_value(as_wfs=True)
        )
        # Check result
        self.assertEqual("http://localhost/geoserver/ows", ret)

        # Check as wcs
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="primary_geoserver")
            .get_value(as_wcs=True)
        )
        # Check result
        self.assertEqual("http://localhost/geoserver/wcs", ret)

        # Check as_endpoint
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="primary_geoserver")
            .get_value(as_endpoint=True)
        )
        # Check result
        self.assertEqual("http://localhost/geoserver/rest/", ret)

        # Check as_endpoint
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="primary_geoserver")
            .get_value(as_public_endpoint=True)
        )
        # Check result
        self.assertEqual("http://publichost/geoserver/rest/", ret)

    @mock.patch("tethys_services.models.TDSCatalog")
    def test_get_value_check_if_thredds(self, mock_TDSCatalog):
        sds = SpatialDatasetService(
            name="test_sds",
            engine=SpatialDatasetService.THREDDS,
            endpoint="http://localhost/thredds/",
            public_endpoint="http://publichost/thredds/",
            apikey="test_api",
            username="foo",
            password="password",
        )
        sds.save()
        sds_setting = self.test_app.settings_set.select_subclasses().get(
            name="primary_thredds"
        )
        sds_setting.spatial_dataset_service = sds
        sds_setting.save()

        # Check as_engine
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="primary_thredds")
            .get_value(as_engine=True)
        )
        # Check result
        mock_TDSCatalog.assert_called_with("http://localhost/thredds/catalog.xml")
        self.assertEqual(mock_TDSCatalog(), ret)

        # Check as wms
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="primary_thredds")
            .get_value(as_wms=True)
        )
        # Check result
        self.assertEqual("http://localhost/thredds/wms", ret)

        # Check as wfs
        self.assertRaises(
            ValueError,
            self.test_app.settings_set.select_subclasses()
            .get(name="primary_thredds")
            .get_value,
            as_wfs=True,
        )

        # Check as wcs
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="primary_thredds")
            .get_value(as_wcs=True)
        )
        # Check result
        self.assertEqual("http://localhost/thredds/wcs", ret)

        # Check as_endpoint
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="primary_thredds")
            .get_value(as_endpoint=True)
        )
        # Check result
        self.assertEqual("http://localhost/thredds/", ret)

        # Check as_endpoint
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="primary_thredds")
            .get_value(as_public_endpoint=True)
        )
        # Check result
        self.assertEqual("http://publichost/thredds/", ret)
