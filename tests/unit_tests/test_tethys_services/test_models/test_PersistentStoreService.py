from tethys_sdk.testing import TethysTestCase
import tethys_services.models as service_model
from unittest import mock
from django.apps import apps
import os
import pytest


class PostgresPersistentStoreServiceTests(TethysTestCase):
    def set_up(self):
        pass

    def tear_down(self):
        pass

    def test_unicode(self):
        pss = service_model.PostgresPersistentStoreService(
            name="test_pss", username="foo", password="pass"
        )
        self.assertEqual("test_pss", str(pss))

    def test_get_url(self):
        pss = service_model.PostgresPersistentStoreService(
            name="test_pss", username="foo", password="pass"
        )

        # Execute
        ret = pss.get_url()

        self.assertEqual("postgresql://foo:pass@localhost:5435", str(ret))

    @mock.patch("tethys_services.models.PostgresPersistentStoreService.get_url")
    @mock.patch("sqlalchemy.create_engine")
    def test_get_engine(self, mock_ce, mock_url):
        pss = service_model.PostgresPersistentStoreService(
            name="test_pss", username="foo", password="pass"
        )

        mock_url.return_value = "test_url"
        # Execute
        pss.get_engine()

        # Check if called correctly
        mock_ce.assert_called_with("test_url")


class SQLitePersistentStoreServiceTests(TethysTestCase):
    def set_up(self):
        pass

    def tear_down(self):
        pass

    def test_unicode(self):
        pss = service_model.SQLitePersistentStoreService(name="test_pss")
        self.assertEqual("test_pss", str(pss))

    def test_get_url(self):
        pss = service_model.SQLitePersistentStoreService(
            name="test_pss", dir_path="/tmp"
        )
        pss.database = "test_db"

        # Execute
        ret = pss.get_url()

        self.assertEqual("sqlite:////tmp/test_db.sqlite", str(ret))

    @mock.patch("sqlalchemy.create_engine")
    def test_get_engine(self, mock_ce):
        pss = service_model.SQLitePersistentStoreService(
            name="test_pss", dir_path="/tmp"
        )
        pss.database = "test_db"

        # Execute
        pss.get_engine()

        # Check if called correctly
        mock_ce.assert_called_with("sqlite:////tmp/test_db.sqlite")

    @mock.patch("sqlalchemy.create_engine")
    @mock.patch("sqlalchemy.event.listen")
    @mock.patch("geoalchemy2.load_spatialite")
    def test_get_spatial_engine(self, mock_load_spatialite, mock_listen, mock_ce):
        pss = service_model.SQLitePersistentStoreService(
            name="test_pss", dir_path="/tmp"
        )
        pss.database = "test_db"

        # Execute
        with mock.patch.dict(os.environ, {"SPATIALITE_LIBRARY_PATH": "some_path"}):
            pss.get_engine(spatial=True)

        # Check if called correctly
        mock_listen.assert_called_with(
            mock_ce.return_value, "connect", mock_load_spatialite
        )
        mock_ce.assert_called_with("sqlite:////tmp/test_db.sqlite")

    @mock.patch("sqlalchemy.create_engine")
    @mock.patch("sqlalchemy.event.listen")
    def test_get_spatial_engine_missing_environ(self, mock_listen, mock_ce):
        pss = service_model.SQLitePersistentStoreService(
            name="test_pss", dir_path="/tmp"
        )
        pss.database = "test_db"

        # Execute
        with pytest.raises(EnvironmentError) as exc_info:
            with mock.patch.dict(os.environ, {"SPATIALITE_LIBRARY_PATH": ""}):
                pss.get_engine(spatial=True)

        self.assertIn(
            "SPATIALITE_LIBRARY_PATH environment variable must be set to enable spatial features on SQLite persistent stores. To enable SpatiaLite support, Install and set the SPATIALITE_LIBRARY_PATH environment variable to the path of the SpatiaLite library on your system. Check https://www.gaia-gis.it/fossil/libspatialite/home for installation instructions.",
            str(exc_info.value),
        )

        # Check if called correctly
        mock_ce.assert_called_with("sqlite:////tmp/test_db.sqlite")
        mock_listen.assert_not_called()


class TestConcreteStoreTests(TethysTestCase):
    def set_up(self):
        class TestConcreteStore(service_model.PersistentStoreServiceBase):
            class Meta:
                app_label = "test_app"
                verbose_name = "Test Store"
                verbose_name_plural = "Test Stores"
                db_table = "test_concrete_store"

        self.TestConcreteStore = TestConcreteStore

    def tear_down(self):
        # Clean up: remove model from app registry
        if apps.is_installed("test_app"):
            try:
                del apps.all_models["test_app"]["testconcretestore"]
            except KeyError:
                pass

    def test_get_url(self):
        store = self.TestConcreteStore(name="Test", engine="sqlite")
        self.assertIsNone(store.get_url())
