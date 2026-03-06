from tethys_sdk.testing import TethysTestCase
from tethys_apps.models import (
    TethysApp,
    PersistentStoreConnectionSetting,
    PostgresPersistentStoreService,
    SQLitePersistentStoreService,
)
from django.core.exceptions import ValidationError
from tethys_apps.exceptions import TethysAppSettingNotAssigned
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import sessionmaker


class PostgresPersistentStoreConnectionSettingTests(TethysTestCase):
    def set_up(self):
        self.test_app = TethysApp.objects.get(package="test_app")

        self.pss_postgres = PostgresPersistentStoreService(
            name="test_ps_postgres",
            host="localhost",
            port="5432",
            username="foo",
            password="password",
        )
        self.pss_postgres.save()

        self.pss_sqlite = SQLitePersistentStoreService(
            name="test_ps_sqlite",
            dir_path="/tmp",
        )
        self.pss_sqlite.save()
        pass

    def tear_down(self):
        self.pss_postgres.delete()
        self.pss_sqlite.delete()

    def test_clean_empty_validation_error(self):
        ps_cs_setting = self.test_app.settings_set.select_subclasses().get(
            name="primary"
        )
        ps_cs_setting.persistent_store_service_postgres = None
        ps_cs_setting.save()
        # Check ValidationError
        self.assertRaises(
            ValidationError,
            PersistentStoreConnectionSetting.objects.get(name="primary").clean,
        )

    def test_get_value_postgres(self):
        ps_cs_setting = self.test_app.settings_set.select_subclasses().get(
            name="primary"
        )
        ps_cs_setting.persistent_store_service_postgres = self.pss_postgres
        ps_cs_setting.save()

        # Execute
        ret = PersistentStoreConnectionSetting.objects.get(name="primary").get_value()

        # Check if ret is an instance of PostgresPersistentStoreService
        self.assertIsInstance(ret, PostgresPersistentStoreService)
        self.assertEqual("test_ps_postgres", ret.name)
        self.assertEqual("localhost", ret.host)
        self.assertEqual(5432, ret.port)
        self.assertEqual("foo", ret.username)
        self.assertEqual("password", ret.password)

    def test_get_value_sqlite(self):
        ps_cs_setting = self.test_app.settings_set.select_subclasses().get(
            name="primary"
        )
        ps_cs_setting.persistent_store_service_sqlite = self.pss_sqlite
        ps_cs_setting.save()

        # Execute
        ret = PersistentStoreConnectionSetting.objects.get(name="primary").get_value()

        # Check if ret is an instance of SQLitePersistentStoreService
        self.assertIsInstance(ret, SQLitePersistentStoreService)
        self.assertEqual("test_ps_sqlite", ret.name)
        self.assertEqual("/tmp", ret.dir_path)

    def test_get_value_none(self):
        ps_cs_setting = self.test_app.settings_set.select_subclasses().get(
            name="primary"
        )
        ps_cs_setting.persistent_store_service_postgres = None
        ps_cs_setting.persistent_store_service_sqlite = None
        ps_cs_setting.save()

        # Check TethysAppSettingNotAssigned
        self.assertRaises(
            TethysAppSettingNotAssigned,
            PersistentStoreConnectionSetting.objects.get(name="primary").get_value,
        )

    def test_get_value_as_engine(self):
        ps_cs_setting = self.test_app.settings_set.select_subclasses().get(
            name="primary"
        )
        ps_cs_setting.persistent_store_service_postgres = self.pss_postgres
        ps_cs_setting.save()

        # Execute
        ret = PersistentStoreConnectionSetting.objects.get(name="primary").get_value(
            as_engine=True
        )

        # Check if ret is an instance of sqlalchemy Engine
        self.assertIsInstance(ret, Engine)
        self.assertEqual("postgresql://foo:password@localhost:5432", str(ret.url))

    def test_get_value_as_sessionmaker(self):
        ps_cs_setting = self.test_app.settings_set.select_subclasses().get(
            name="primary"
        )
        ps_cs_setting.persistent_store_service_postgres = self.pss_postgres
        ps_cs_setting.save()

        # Execute
        ret = PersistentStoreConnectionSetting.objects.get(name="primary").get_value(
            as_sessionmaker=True
        )

        # Check if ret is an instance of sqlalchemy sessionmaker
        self.assertIsInstance(ret, sessionmaker)
        self.assertEqual(
            "postgresql://foo:password@localhost:5432", str(ret.kw["bind"].url)
        )

    def test_get_value_as_url(self):
        ps_cs_setting = self.test_app.settings_set.select_subclasses().get(
            name="primary"
        )
        ps_cs_setting.persistent_store_service_postgres = self.pss_postgres
        ps_cs_setting.save()

        # Execute
        ret = PersistentStoreConnectionSetting.objects.get(name="primary").get_value(
            as_url=True
        )

        # Check Url
        self.assertEqual("postgresql://foo:password@localhost:5432", str(ret))
