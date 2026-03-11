import pytest
from tethys_sdk.testing import TethysTestCase
from tethys_apps.models import (
    TethysApp,
    PersistentStoreDatabaseSetting,
)
from tethys_services.models import (
    PostgresPersistentStoreService,
    SQLitePersistentStoreService,
)
from django.core.exceptions import ValidationError
from tethys_apps.exceptions import (
    TethysAppSettingNotAssigned,
    PersistentStoreInitializerError,
)
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from unittest import mock


class PersistentStoreDatabaseSettingTests(TethysTestCase):
    def set_up(self):
        self.test_app = TethysApp.objects.get(package="test_app")

        self.conn = {
            "USER": "tethys_super",
            "PASSWORD": "pass",
            "HOST": "localhost",
            "PORT": "5435",
        }

        self.expected_url = "postgresql://{}:{}@{}:{}".format(
            self.conn["USER"],
            self.conn["PASSWORD"],
            self.conn["HOST"],
            self.conn["PORT"],
        )

        self.pss_postgres = PostgresPersistentStoreService(
            name="test_ps_postgres",
            host=self.conn["HOST"],
            port=self.conn["PORT"],
            username=self.conn["USER"],
            password=self.conn["PASSWORD"],
        )

        self.pss_postgres.save()

        self.pss_sqlite = SQLitePersistentStoreService(
            name="test_ps_sqlite",
            dir_path="/tmp",
        )
        self.pss_sqlite.save()

    def tear_down(self):
        self.pss_postgres.delete()
        self.pss_sqlite.delete()

    def test_clean_validation_error(self):
        ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        )
        ps_ds_setting.persistent_store_service = None
        ps_ds_setting.save()
        # Check ValidationError
        self.assertRaises(
            ValidationError,
            self.test_app.settings_set.select_subclasses().get(name="spatial_db").clean,
        )

    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.create_persistent_store_database"
    )
    def test_initialize(self, mock_create):
        ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        )
        ps_ds_setting.persistent_store_service = self.pss_postgres
        ps_ds_setting.save()

        # Execute
        self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        ).initialize()

        mock_create.assert_called()

    @mock.patch("tethys_apps.models.is_testing_environment")
    def test_get_namespaced_persistent_store_name(self, mock_ite):
        mock_ite.return_value = False
        ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        )
        ps_ds_setting.persistent_store_service = self.pss_postgres
        ps_ds_setting.save()

        # Execute
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="spatial_db")
            .get_namespaced_persistent_store_name()
        )

        # Check result
        self.assertEqual("test_app_spatial_db", ret)

    @mock.patch("tethys_apps.models.is_testing_environment")
    def test_get_namespaced_persistent_store_name_testing(self, mock_ite):
        mock_ite.return_value = True
        ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        )
        ps_ds_setting.persistent_store_service = self.pss_postgres
        ps_ds_setting.save()

        # Execute
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="spatial_db")
            .get_namespaced_persistent_store_name()
        )

        # Check result
        self.assertEqual("test_app_tethys-testing_spatial_db", ret)

    def test_get_value_postgres(self):
        ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        )
        ps_ds_setting.persistent_store_service = self.pss_postgres
        ps_ds_setting.save()

        # Execute
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="spatial_db")
            .get_value(with_db=True)
        )

        # Check results
        self.assertIsInstance(ret, PostgresPersistentStoreService)
        self.assertEqual("test_ps_postgres", ret.name)
        self.assertEqual(self.conn["HOST"], ret.host)
        self.assertEqual(int(self.conn["PORT"]), ret.port)
        self.assertEqual(self.conn["USER"], ret.username)
        self.assertEqual(self.conn["PASSWORD"], ret.password)

    def test_get_value_sqlite(self):
        ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        )
        ps_ds_setting.persistent_store_service = self.pss_sqlite
        ps_ds_setting.save()

        # Execute
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="spatial_db")
            .get_value(with_db=True)
        )

        # Check results
        self.assertIsInstance(ret, SQLitePersistentStoreService)
        self.assertEqual("test_ps_sqlite", ret.name)
        self.assertEqual("/tmp", ret.dir_path)

    def test_get_value_none(self):
        ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        )
        ps_ds_setting.persistent_store_service = None
        ps_ds_setting.save()

        self.assertRaises(
            TethysAppSettingNotAssigned,
            PersistentStoreDatabaseSetting.objects.get(name="spatial_db").get_value,
        )

    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.get_namespaced_persistent_store_name"
    )
    def test_get_value_with_db(self, mock_gn):
        mock_gn.return_value = "test_database"
        ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        )
        ps_ds_setting.persistent_store_service = self.pss_postgres
        ps_ds_setting.save()

        # Execute
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="spatial_db")
            .get_value(with_db=True)
        )

        self.assertIsInstance(ret, PostgresPersistentStoreService)
        self.assertEqual("test_database", ret.database)

    def test_get_value_as_engine(self):
        ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        )
        ps_ds_setting.persistent_store_service = self.pss_postgres
        ps_ds_setting.save()

        # Execute
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="spatial_db")
            .get_value(as_engine=True)
        )

        self.assertIsInstance(ret, Engine)
        self.assertEqual(self.expected_url, str(ret.url))

    def test_get_value_as_sessionmaker(self):
        ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        )
        ps_ds_setting.persistent_store_service = self.pss_postgres
        ps_ds_setting.save()

        # Execute
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="spatial_db")
            .get_value(as_sessionmaker=True)
        )

        self.assertIsInstance(ret, sessionmaker)
        self.assertEqual(self.expected_url, str(ret.kw["bind"].url))

    def test_get_value_as_url(self):
        ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        )
        ps_ds_setting.persistent_store_service = self.pss_postgres
        ps_ds_setting.save()

        # Execute
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="spatial_db")
            .get_value(as_url=True)
        )

        # check URL
        self.assertEqual(self.expected_url, str(ret))

    @mock.patch("tethys_apps.models.PostgresDatabaseHandler")
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting.get_value")
    def test_persistent_store_database_exists(self, mock_get_value, mock_db_handler):
        mock_engine = mock.MagicMock()
        mock_url = mock.MagicMock(username="test_app")
        mock_pss = mock.MagicMock(engine="postgresql")
        mock_get_value.side_effect = [mock_pss, mock_url, mock_engine]

        # Set up the handler mock so every new instance uses it
        mock_handler = mock.MagicMock()
        mock_handler.database_exists.return_value = True
        mock_db_handler.return_value = mock_handler

        with mock.patch.dict(
            "tethys_apps.models.DB_ENGINE_HANDLERS", {"postgresql": mock_db_handler}
        ):
            ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
                name="spatial_db"
            )
            self.assertTrue(ps_ds_setting.persistent_store_database_exists())

    @mock.patch("tethys_apps.models.PostgresDatabaseHandler")
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting.get_value")
    def test_persistent_store_database_exists_false(
        self, mock_get_value, mock_db_handler
    ):
        mock_engine = mock.MagicMock()
        mock_url = mock.MagicMock(username="test_app")
        mock_pss = mock.MagicMock(engine="postgresql")
        mock_get_value.side_effect = [mock_pss, mock_url, mock_engine]

        # Set up the handler mock so every new instance uses it
        mock_handler = mock.MagicMock()
        mock_handler.database_exists.return_value = False
        mock_db_handler.return_value = mock_handler

        with mock.patch.dict(
            "tethys_apps.models.DB_ENGINE_HANDLERS", {"postgresql": mock_db_handler}
        ):
            ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
                name="spatial_db"
            )
            self.assertFalse(ps_ds_setting.persistent_store_database_exists())

    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting.get_value")
    def test_persistent_store_database_handler_not_implemented(self, mock_get_value):
        mock_engine = mock.MagicMock()
        mock_url = mock.MagicMock(username="test_app")
        mock_pss = mock.MagicMock(engine="bad_engine")
        mock_get_value.side_effect = [mock_pss, mock_url, mock_engine]

        with pytest.raises(NotImplementedError) as excinfo:
            self.test_app.settings_set.select_subclasses().get(
                name="spatial_db"
            ).persistent_store_database_exists()
            self.assertIn(
                "No db_handler for engine type: bad_engine", str(excinfo.value)
            )

    @mock.patch("tethys_apps.models.PostgresDatabaseHandler")
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting.get_value")
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.persistent_store_database_exists"
    )
    def test_drop_persistent_store_database_db_exists(
        self, mock_persistent_store_database_exists, mock_get_value, mock_db_handler
    ):
        mock_engine = mock.MagicMock()
        mock_url = mock.MagicMock(username="test_app")
        mock_pss = mock.MagicMock(engine="postgresql")
        mock_get_value.side_effect = [mock_pss, mock_url, mock_engine]

        # Set up the handler mock so every new instance uses it
        mock_handler = mock.MagicMock()
        mock_db_handler.return_value = mock_handler
        mock_persistent_store_database_exists.return_value = True

        with mock.patch.dict(
            "tethys_apps.models.DB_ENGINE_HANDLERS", {"postgresql": mock_db_handler}
        ):
            ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
                name="spatial_db"
            )
            ps_ds_setting.drop_persistent_store_database()

        mock_handler.drop_database.assert_called()

    @mock.patch("tethys_apps.models.PostgresDatabaseHandler")
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting.get_value")
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.persistent_store_database_exists"
    )
    def test_drop_persistent_store_database_db_not_exists(
        self, mock_persistent_store_database_exists, mock_get_value, mock_db_handler
    ):
        # Set up the handler mock so every new instance uses it
        mock_handler = mock.MagicMock()
        mock_db_handler.return_value = mock_handler
        mock_persistent_store_database_exists.return_value = False

        with mock.patch.dict(
            "tethys_apps.models.DB_ENGINE_HANDLERS", {"postgresql": mock_db_handler}
        ):
            ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
                name="spatial_db"
            )
            ps_ds_setting.drop_persistent_store_database()

        mock_get_value.assert_not_called()
        mock_handler.drop_database.assert_not_called()

    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting.get_value")
    def test_drop_persistent_store_database_not_implemented(self, mock_get_value):
        mock_engine = mock.MagicMock()
        mock_url = mock.MagicMock(username="test_app")
        mock_pss = mock.MagicMock(engine="bad_engine")
        mock_get_value.side_effect = [mock_pss, mock_url, mock_engine]

        with pytest.raises(NotImplementedError) as excinfo:
            self.test_app.settings_set.select_subclasses().get(
                name="spatial_db"
            ).drop_persistent_store_database()
            self.assertIn(
                "No db_handler for engine type: bad_engine", str(excinfo.value)
            )

    @mock.patch("tethys_apps.models.PostgresDatabaseHandler")
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting.get_value")
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.get_namespaced_persistent_store_name"
    )
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.persistent_store_database_exists"
    )
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.initializer_function"
    )
    @mock.patch("tethys_apps.models.logging")
    def test_create_persistent_store_database_db_doesnt_exist_force_first_time(
        self,
        mock_log,
        mock_init,
        mock_persistent_store_database_exists,
        mock_get_namespaced_name,
        mock_get_value,
        mock_db_handler,
    ):
        mock_engine = mock.MagicMock()
        mock_url = mock.MagicMock(username="test_app")
        mock_pss = mock.MagicMock(engine="postgresql")
        mock_init_param = mock.MagicMock()
        mock_get_value.side_effect = [mock_pss, mock_url, mock_engine, mock_init_param]
        mock_get_namespaced_name.return_value = "spatial_db"

        # Set up the handler mock so every new instance uses it
        mock_handler = mock.MagicMock()
        mock_db_handler.return_value = mock_handler
        mock_persistent_store_database_exists.return_value = False

        with mock.patch.dict(
            "tethys_apps.models.DB_ENGINE_HANDLERS", {"postgresql": mock_db_handler}
        ):
            ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
                name="spatial_db"
            )
            ps_ds_setting.create_persistent_store_database(
                refresh=False, force_first_time=True
            )

        mock_log_info_calls = mock_log.getLogger().info.call_args_list
        check_log1 = 'Creating database "spatial_db" for app "test_app"...'
        check_log2 = 'Enabling PostGIS on database "spatial_db" for app "test_app"...'
        check_log3 = (
            'Initializing database "spatial_db" for app "test_app" '
            'with initializer "appsettings.model.init_spatial_db"...'
        )
        self.assertEqual(check_log1, mock_log_info_calls[0][0][0])
        self.assertEqual(check_log2, mock_log_info_calls[1][0][0])
        self.assertEqual(check_log3, mock_log_info_calls[2][0][0])

        mock_handler.create_database.assert_called()
        mock_handler.enable_postgis_extension.assert_called()
        mock_init.assert_called_with(mock_init_param, True)

    @mock.patch("tethys_apps.models.PostgresDatabaseHandler")
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting.get_value")
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.get_namespaced_persistent_store_name"
    )
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.persistent_store_database_exists"
    )
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.drop_persistent_store_database"
    )
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.initializer_function"
    )
    @mock.patch("tethys_apps.models.logging")
    def test_create_persistent_store_database_db_exists_but_no_refresh_not_first_time(
        self,
        mock_log,
        mock_init,
        mock_drop_persistent_store_database,
        mock_persistent_store_database_exists,
        mock_get_namespaced_name,
        mock_get_value,
        mock_db_handler,
    ):
        mock_engine = mock.MagicMock()
        mock_url = mock.MagicMock(username="test_app")
        mock_pss = mock.MagicMock(engine="postgresql")
        mock_init_param = mock.MagicMock()
        mock_get_value.side_effect = [mock_pss, mock_url, mock_engine, mock_init_param]
        mock_get_namespaced_name.return_value = "spatial_db"

        # Set up the handler mock so every new instance uses it
        mock_handler = mock.MagicMock()
        mock_db_handler.return_value = mock_handler
        mock_persistent_store_database_exists.return_value = True

        with mock.patch.dict(
            "tethys_apps.models.DB_ENGINE_HANDLERS", {"postgresql": mock_db_handler}
        ):
            ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
                name="spatial_db"
            )
            ps_ds_setting.initialized = True
            ps_ds_setting.create_persistent_store_database(
                refresh=False, force_first_time=False
            )

        mock_log_info_calls = mock_log.getLogger().info.call_args_list
        check_log1 = 'Enabling PostGIS on database "spatial_db" for app "test_app"...'
        check_log2 = (
            'Initializing database "spatial_db" for app "test_app" '
            'with initializer "appsettings.model.init_spatial_db"...'
        )
        self.assertEqual(check_log1, mock_log_info_calls[0][0][0])
        self.assertEqual(check_log2, mock_log_info_calls[1][0][0])

        mock_drop_persistent_store_database.assert_not_called()
        mock_handler.create_database.assert_not_called()
        mock_handler.enable_postgis_extension.assert_called()
        mock_init.assert_called_with(mock_init_param, False)

    @mock.patch("tethys_apps.models.PostgresDatabaseHandler")
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting.get_value")
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.get_namespaced_persistent_store_name"
    )
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.persistent_store_database_exists"
    )
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.drop_persistent_store_database"
    )
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.initializer_function"
    )
    @mock.patch("tethys_apps.models.logging")
    def test_create_persistent_store_database_db_exists_and_refresh_no_spatial_no_initializer(
        self,
        mock_log,
        mock_init,
        mock_drop_persistent_store_database,
        mock_persistent_store_database_exists,
        mock_get_namespaced_name,
        mock_get_value,
        mock_db_handler,
    ):
        mock_engine = mock.MagicMock()
        mock_url = mock.MagicMock(username="test_app")
        mock_pss = mock.MagicMock(engine="postgresql")
        mock_init_param = mock.MagicMock()
        mock_get_value.side_effect = [mock_pss, mock_url, mock_engine, mock_init_param]
        mock_get_namespaced_name.return_value = "spatial_db"

        # Set up the handler mock so every new instance uses it
        mock_handler = mock.MagicMock()
        mock_db_handler.return_value = mock_handler
        mock_persistent_store_database_exists.return_value = True

        with mock.patch.dict(
            "tethys_apps.models.DB_ENGINE_HANDLERS", {"postgresql": mock_db_handler}
        ):
            ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
                name="spatial_db"
            )
            ps_ds_setting.spatial = False
            ps_ds_setting.initializer = False
            ps_ds_setting.create_persistent_store_database(
                refresh=True, force_first_time=False
            )

        mock_log_info_calls = mock_log.getLogger().info.call_args_list
        check_log1 = 'Creating database "spatial_db" for app "test_app"...'
        self.assertEqual(check_log1, mock_log_info_calls[0][0][0])

        mock_drop_persistent_store_database.assert_called()
        mock_handler.create_database.assert_called()
        mock_handler.enable_postgis_extension.assert_not_called()
        mock_init.assert_not_called()

    @mock.patch("tethys_apps.models.PostgresDatabaseHandler")
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting.get_value")
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.get_namespaced_persistent_store_name"
    )
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.persistent_store_database_exists"
    )
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.drop_persistent_store_database"
    )
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.initializer_function"
    )
    @mock.patch("tethys_apps.models.logging")
    def test_create_persistent_store_database_initializer_error(
        self,
        mock_log,
        mock_init,
        mock_drop_persistent_store_database,
        mock_persistent_store_database_exists,
        mock_get_namespaced_name,
        mock_get_value,
        mock_db_handler,
    ):
        mock_engine = mock.MagicMock()
        mock_url = mock.MagicMock(username="test_app")
        mock_pss = mock.MagicMock(engine="postgresql")
        mock_init_param = mock.MagicMock()
        mock_get_value.side_effect = [mock_pss, mock_url, mock_engine, mock_init_param]
        mock_get_namespaced_name.return_value = "spatial_db"
        mock_init.side_effect = Exception("Initializer Error")

        # Set up the handler mock so every new instance uses it
        mock_handler = mock.MagicMock()
        mock_db_handler.return_value = mock_handler
        mock_persistent_store_database_exists.return_value = True

        with pytest.raises(PersistentStoreInitializerError) as _:
            with mock.patch.dict(
                "tethys_apps.models.DB_ENGINE_HANDLERS", {"postgresql": mock_db_handler}
            ):
                ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
                    name="spatial_db"
                )
                ps_ds_setting.spatial = False
                ps_ds_setting.create_persistent_store_database(
                    refresh=True, force_first_time=False
                )

            mock_log_info_calls = mock_log.getLogger().info.call_args_list
            check_log1 = 'Creating database "spatial_db" for app "test_app"...'
            self.assertEqual(check_log1, mock_log_info_calls[0][0][0])

            mock_drop_persistent_store_database.assert_called()
            mock_handler.create_database.assert_called()
            mock_handler.enable_postgis_extension.assert_not_called()
            mock_init.assert_called()
