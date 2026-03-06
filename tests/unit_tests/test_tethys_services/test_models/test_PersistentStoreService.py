from tethys_sdk.testing import TethysTestCase
import tethys_services.models as service_model
from unittest import mock
from django.apps import apps


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

        # Execute
        ret = pss.get_url()

        self.assertEqual("sqlite:////tmp", str(ret))

    @mock.patch("sqlalchemy.create_engine")
    def test_get_engine(self, mock_ce):
        pss = service_model.SQLitePersistentStoreService(
            name="test_pss", dir_path="/tmp"
        )

        # Execute
        pss.get_engine()

        # Check if called correctly
        mock_ce.assert_called_with("sqlite:////tmp")


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
