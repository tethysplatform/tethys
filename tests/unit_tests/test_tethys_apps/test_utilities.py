import pytest
import unittest
from pathlib import Path
from unittest import mock
from guardian.shortcuts import assign_perm
from tethys_sdk.testing import TethysTestCase
from tethys_apps import utilities
from django.core.signing import Signer
from django.test import override_settings
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer

import tethys_apps.base.app_base as tethys_app_base


class TethysAppChild(tethys_app_base.TethysAppBase):
    """
    Tethys app class for Test App.
    """

    name = "Test App"
    index = "home"
    icon = "test_app/images/icon.gif"
    package = "test_app"
    root_url = "test-app"
    color = "#2c3e50"
    description = "Place a brief description of your app here."


class TethysAppsUtilitiesTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @pytest.mark.django_db
    def test_get_directories_in_tethys_templates(self):
        # Get the templates directories for the test_app and test_extension
        result = utilities.get_directories_in_tethys(("templates",))
        self.assertGreaterEqual(len(result), 2)

        test_app = False
        test_ext = False

        for r in result:
            if str(Path("/") / "tethysapp" / "test_app" / "templates") in r:
                test_app = True
            if str(Path("/") / "tethysext" / "test_extension" / "templates") in r:
                test_ext = True

        self.assertTrue(test_app)
        self.assertTrue(test_ext)

    @pytest.mark.django_db
    def test_get_directories_in_tethys_templates_with_app_name(self):
        # Get the templates directories for the test_app and test_extension
        # Use the with_app_name argument, so that the app and extension names appear in the result
        result = utilities.get_directories_in_tethys(("templates",), with_app_name=True)
        self.assertGreaterEqual(len(result), 2)
        self.assertEqual(2, len(result[0]))
        self.assertEqual(2, len(result[1]))

        test_app = False
        test_ext = False

        for r in result:
            if (
                "test_app" in r
                and str(Path("/") / "tethysapp" / "test_app" / "templates") in r[1]
            ):
                test_app = True
            if (
                "test_extension" in r
                and str(Path("/") / "tethysext" / "test_extension" / "templates")
                in r[1]
            ):
                test_ext = True

        self.assertTrue(test_app)
        self.assertTrue(test_ext)

    @mock.patch("tethys_apps.utilities.SingletonHarvester")
    def test_get_directories_in_tethys_templates_extension_import_error(
        self, mock_harvester
    ):
        # Mock the extension_modules variable with bad data, to throw an ImportError
        mock_harvester().extension_modules = {
            "foo_invalid_foo": "tethysext.foo_invalid_foo"
        }
        mock_harvester().app_modules = {"test_app": "tethysapp.test_app"}

        result = utilities.get_directories_in_tethys(("templates",))
        self.assertGreaterEqual(len(result), 1)

        test_app = False
        test_ext = False

        for r in result:
            if str(Path("/") / "tethysapp" / "test_app" / "templates") in r:
                test_app = True
            if str(Path("/") / "tethysext" / "test_extension" / "templates") in r:
                test_ext = True

        self.assertTrue(test_app)
        self.assertFalse(test_ext)

    @mock.patch("tethys_apps.utilities.SingletonHarvester")
    def test_get_directories_in_tethys_templates_apps_import_error(
        self, mock_harvester
    ):
        # Mock the extension_modules variable with bad data, to throw an ImportError
        mock_harvester().app_modules = {"foo_invalid_foo": "tethys_app.foo_invalid_foo"}

        result = utilities.get_directories_in_tethys(("templates",))
        self.assertGreaterEqual(len(result), 0)

        test_app = False

        for r in result:
            if "/tethysapp/foo_invalid_foo/templates" in r:
                test_app = True

        self.assertFalse(test_app)

    def test_get_directories_in_tethys_foo(self):
        # Get the foo directories for the test_app and test_extension
        # foo doesn't exist
        result = utilities.get_directories_in_tethys(("foo",))
        self.assertEqual(0, len(result))

    @pytest.mark.django_db
    def test_get_directories_in_tethys_foo_public(self):
        # Get the foo and public directories for the test_app and test_extension
        # foo doesn't exist, but public will
        result = utilities.get_directories_in_tethys(("foo", "public"))
        self.assertGreaterEqual(len(result), 2)

        test_app = False
        test_ext = False

        for r in result:
            if str(Path("/") / "tethysapp" / "test_app" / "public") in r:
                test_app = True
            if str(Path("/") / "tethysext" / "test_extension" / "public") in r:
                test_ext = True

        self.assertTrue(test_app)
        self.assertTrue(test_ext)

    @override_settings(MULTIPLE_APP_MODE=True)
    def test_get_active_app_none_none(self):
        # Get the active TethysApp object, with a request of None and url of None
        result = utilities.get_active_app(request=None, url=None)
        self.assertEqual(None, result)

        # Try again with the defaults, which are a request of None and url of None
        result = utilities.get_active_app()
        self.assertEqual(None, result)

    @override_settings(MULTIPLE_APP_MODE=True)
    @pytest.mark.django_db
    def test_get_app_model_request_app_base(self):
        from tethys_apps.models import TethysApp

        app = TethysApp.objects.create(
            package="app_model_test_app",
            name="App Model Test App",
            root_url="app-model-test-app",
        )
        app_base_instance = TethysAppChild()
        app_base_instance.package = "app_model_test_app"
        app_base_instance.root_url = "app-model-test-app"
        app_base_instance.name = "App Model Test App"
        app_model = utilities.get_app_model(app_base_instance)
        self.assertIsNotNone(app_model)
        self.assertEqual(app_model, app)

    @override_settings(MULTIPLE_APP_MODE=True)
    @mock.patch("tethys_apps.models.TethysApp")
    def test_get_active_app_request(self, mock_app):
        # Mock up for TethysApp, and request
        mock_app.objects.get.return_value = mock.MagicMock()
        mock_request = mock.MagicMock()
        mock_request.path = "/apps/foo/bar"

        # Result should be mock for mock_app.objects.get.return_value
        result = utilities.get_active_app(request=mock_request)
        self.assertEqual(mock_app.objects.get(), result)

    @override_settings(MULTIPLE_APP_MODE=False)
    @mock.patch("tethys_apps.utilities.get_configured_standalone_app")
    def test_get_active_app_request_standalone_app(self, mock_first_app):
        # Mock up for TethysApp, and request
        mock_tethysapp = mock.MagicMock(root_url="test-app")
        mock_first_app.return_value = mock_tethysapp
        mock_request = mock.MagicMock()
        mock_request.path = "/test-app/"

        result = utilities.get_active_app(request=mock_request)
        self.assertEqual(mock_tethysapp, result)

    @override_settings(MULTIPLE_APP_MODE=True)
    @mock.patch("tethys_apps.models.TethysApp")
    def test_get_active_app_url(self, mock_app):
        # Mock up for TethysApp
        mock_app.objects.get.return_value = mock.MagicMock()

        # Result should be mock for mock_app.objects.get.return_value
        result = utilities.get_active_app(url="/apps/foo/bar")
        self.assertEqual(mock_app.objects.get(), result)

    @override_settings(MULTIPLE_APP_MODE=True)
    def test_get_active_app_no_app(self):
        # check apps with /
        result = utilities.get_active_app(url="/apps/")
        self.assertEqual(None, result)
        # check apps without /
        result = utilities.get_active_app(url="/apps")
        self.assertEqual(None, result)

    @override_settings(MULTIPLE_APP_MODE=True)
    @mock.patch("tethys_apps.utilities.SingletonHarvester")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_get_active_app_class(self, mock_app, mock_harvester):
        # Mock up for TethysApp
        app = mock.MagicMock()
        mock_app.objects.get.return_value = app

        mock_harvester().apps = [app]

        # Result should be mock for mock_app.objects.get.return_value
        result = utilities.get_active_app(url="/apps/foo/bar", get_class=True)
        self.assertEqual(mock_app.objects.get(), result)

    @override_settings(MULTIPLE_APP_MODE=True)
    @mock.patch("tethys_apps.models.TethysApp")
    def test_get_active_app_request_bad_path(self, mock_app):
        # Mock up for TethysApp
        mock_app.objects.get.return_value = mock.MagicMock()
        mock_request = mock.MagicMock()
        # Path does not contain apps
        mock_request.path = "/foo/bar"

        # Because 'app' not in request path, return None
        result = utilities.get_active_app(request=mock_request)
        self.assertEqual(None, result)

    @override_settings(MULTIPLE_APP_MODE=True)
    @mock.patch("tethys_apps.utilities.tethys_log.warning")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_get_active_app_request_exception1(self, mock_app, mock_log_warning):
        from django.core.exceptions import ObjectDoesNotExist

        # Mock up for TethysApp to raise exception, and request
        mock_app.objects.get.side_effect = ObjectDoesNotExist
        mock_request = mock.MagicMock()
        mock_request.path = "/apps/foo/bar"

        # Result should be None due to the exception
        result = utilities.get_active_app(request=mock_request)
        self.assertEqual(None, result)
        mock_log_warning.assert_called_once_with(
            'Could not locate app with root url "foo".'
        )

    @override_settings(MULTIPLE_APP_MODE=True)
    @mock.patch("tethys_apps.utilities.tethys_log.warning")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_get_active_app_request_exception2(self, mock_app, mock_log_warning):
        from django.core.exceptions import MultipleObjectsReturned

        # Mock up for TethysApp to raise exception, and request
        mock_app.objects.get.side_effect = MultipleObjectsReturned
        mock_request = mock.MagicMock()
        mock_request.path = "/apps/foo/bar"

        # Result should be None due to the exception
        result = utilities.get_active_app(request=mock_request)
        self.assertEqual(None, result)
        mock_log_warning.assert_called_once_with(
            'Multiple apps found with root url "foo".'
        )

    @mock.patch("tethys_cli.cli_colors.pretty_output")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_create_ps_database_setting_app_does_not_exist(
        self, mock_app, mock_pretty_output
    ):
        from django.core.exceptions import ObjectDoesNotExist

        # Mock up for TethysApp to not exist
        mock_app.objects.get.side_effect = ObjectDoesNotExist
        mock_app_package = mock.MagicMock()
        mock_name = mock.MagicMock()

        # ObjectDoesNotExist should be thrown, and False returned
        result = utilities.create_ps_database_setting(
            app_package=mock_app_package, name=mock_name
        )

        self.assertEqual(False, result)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn("A Tethys App with the name", po_call_args[0][0][0])
        self.assertIn("does not exist. Aborted.", po_call_args[0][0][0])

    @mock.patch("tethys_cli.cli_colors.pretty_output")
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_create_ps_database_setting_ps_database_setting_exists(
        self, mock_app, mock_ps_db_setting, mock_pretty_output
    ):
        # Mock up for TethysApp and PersistentStoreDatabaseSetting to exist
        mock_app.objects.get.return_value = mock.MagicMock()
        mock_ps_db_setting.objects.get.return_value = mock.MagicMock()
        mock_app_package = mock.MagicMock()
        mock_name = mock.MagicMock()

        # PersistentStoreDatabaseSetting should exist, and False returned
        result = utilities.create_ps_database_setting(
            app_package=mock_app_package, name=mock_name
        )

        self.assertEqual(False, result)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "A PersistentStoreDatabaseSetting with name", po_call_args[0][0][0]
        )
        self.assertIn("already exists. Aborted.", po_call_args[0][0][0])

    @mock.patch("tethys_apps.utilities.print")
    @mock.patch("tethys_cli.cli_colors.pretty_output")
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_create_ps_database_setting_ps_database_setting_exceptions(
        self, mock_app, mock_ps_db_setting, mock_pretty_output, mock_print
    ):
        from django.core.exceptions import ObjectDoesNotExist

        # Mock up for TethysApp to exist and PersistentStoreDatabaseSetting to throw exceptions
        mock_app.objects.get.return_value = mock.MagicMock()
        mock_ps_db_setting.objects.get.side_effect = ObjectDoesNotExist
        mock_ps_db_setting().save.side_effect = Exception("foo exception")
        mock_app_package = mock.MagicMock()
        mock_name = mock.MagicMock()

        # PersistentStoreDatabaseSetting should exist, and False returned
        result = utilities.create_ps_database_setting(
            app_package=mock_app_package, name=mock_name
        )

        self.assertEqual(False, result)
        mock_ps_db_setting.assert_called()
        mock_ps_db_setting().save.assert_called()
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "The above error was encountered. Aborted.", po_call_args[0][0][0]
        )
        rts_call_args = mock_print.call_args_list
        self.assertIn("foo exception", rts_call_args[0][0][0].args[0])

    @mock.patch("tethys_cli.cli_colors.pretty_output")
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_create_ps_database_setting_ps_database_savess(
        self, mock_app, mock_ps_db_setting, mock_pretty_output
    ):
        # Mock up for TethysApp to exist and PersistentStoreDatabaseSetting to not
        mock_app.objects.get.return_value = mock.MagicMock()
        mock_ps_db_setting.objects.get.return_value = False
        mock_ps_db_setting().save.return_value = True
        mock_app_package = mock.MagicMock()
        mock_name = mock.MagicMock()

        # True should be returned
        result = utilities.create_ps_database_setting(
            app_package=mock_app_package, name=mock_name
        )

        self.assertEqual(True, result)
        mock_ps_db_setting.assert_called()
        mock_ps_db_setting().save.assert_called()
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn("PersistentStoreDatabaseSetting named", po_call_args[0][0][0])
        self.assertIn("created successfully!", po_call_args[0][0][0])

    @mock.patch("tethys_cli.cli_colors.pretty_output")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_remove_ps_database_setting_app_not_exist(
        self, mock_app, mock_pretty_output
    ):
        from django.core.exceptions import ObjectDoesNotExist

        # Mock up for TethysApp to throw an exception
        mock_app.objects.get.side_effect = ObjectDoesNotExist
        mock_app_package = mock.MagicMock()
        mock_name = mock.MagicMock()

        # An exception will be thrown and false returned
        result = utilities.remove_ps_database_setting(
            app_package=mock_app_package, name=mock_name
        )

        self.assertEqual(False, result)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn("A Tethys App with the name", po_call_args[0][0][0])
        self.assertIn("does not exist. Aborted.", po_call_args[0][0][0])

    @mock.patch("tethys_cli.cli_colors.pretty_output")
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_remove_ps_database_setting_psdbs_not_exist(
        self, mock_app, mock_ps_db_setting, mock_pretty_output
    ):
        from django.core.exceptions import ObjectDoesNotExist

        # Mock up for TethysApp and PersistentStoreDatabaseSetting to throw an exception
        mock_app.objects.get.return_value = mock.MagicMock()
        mock_ps_db_setting.objects.get.side_effect = ObjectDoesNotExist
        mock_app_package = mock.MagicMock()
        mock_name = mock.MagicMock()

        # An exception will be thrown and false returned
        result = utilities.remove_ps_database_setting(
            app_package=mock_app_package, name=mock_name
        )

        self.assertEqual(False, result)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "An PersistentStoreDatabaseSetting with the name", po_call_args[0][0][0]
        )
        self.assertIn(" for app ", po_call_args[0][0][0])
        self.assertIn("does not exist. Aborted.", po_call_args[0][0][0])

    @mock.patch("tethys_cli.cli_colors.pretty_output")
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_remove_ps_database_setting_force_delete(
        self, mock_app, mock_ps_db_setting, mock_pretty_output
    ):
        # Mock up for TethysApp and PersistentStoreDatabaseSetting
        mock_app.objects.get.return_value = mock.MagicMock()
        mock_ps_db_setting.objects.get.return_value = mock.MagicMock()
        mock_ps_db_setting.objects.get().delete.return_value = True
        mock_app_package = mock.MagicMock()
        mock_name = mock.MagicMock()

        # Delete will be called and True returned
        result = utilities.remove_ps_database_setting(
            app_package=mock_app_package, name=mock_name, force=True
        )

        self.assertEqual(True, result)
        mock_ps_db_setting.objects.get().delete.assert_called_once()
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "Successfully removed PersistentStoreDatabaseSetting with name",
            po_call_args[0][0][0],
        )

    @mock.patch("tethys_apps.utilities.input")
    @mock.patch("tethys_cli.cli_colors.pretty_output")
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_remove_ps_database_setting_proceed_delete(
        self, mock_app, mock_ps_db_setting, mock_pretty_output, mock_input
    ):
        # Mock up for TethysApp and PersistentStoreDatabaseSetting
        mock_app.objects.get.return_value = mock.MagicMock()
        mock_ps_db_setting.objects.get.return_value = mock.MagicMock()
        mock_ps_db_setting.objects.get().delete.return_value = True
        mock_input.side_effect = ["Y"]
        mock_app_package = mock.MagicMock()
        mock_name = mock.MagicMock()

        # Based on the raw_input, delete not called and None returned
        result = utilities.remove_ps_database_setting(
            app_package=mock_app_package, name=mock_name
        )

        self.assertEqual(True, result)
        mock_ps_db_setting.objects.get().delete.assert_called()
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "Successfully removed PersistentStoreDatabaseSetting with name",
            po_call_args[0][0][0],
        )

    @mock.patch("tethys_apps.utilities.input")
    @mock.patch("tethys_cli.cli_colors.pretty_output")
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_remove_ps_database_setting_do_not_proceed(
        self, mock_app, mock_ps_db_setting, mock_pretty_output, mock_input
    ):
        # Mock up for TethysApp and PersistentStoreDatabaseSetting
        mock_app.objects.get.return_value = mock.MagicMock()
        mock_ps_db_setting.objects.get.return_value = mock.MagicMock()
        mock_ps_db_setting.objects.get().delete.return_value = True
        mock_input.side_effect = ["foo", "N"]
        mock_app_package = mock.MagicMock()
        mock_name = mock.MagicMock()

        # Based on the raw_input, delete not called and None returned
        result = utilities.remove_ps_database_setting(
            app_package=mock_app_package, name=mock_name
        )

        self.assertEqual(None, result)
        mock_ps_db_setting.objects.get().delete.assert_not_called()
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual(
            "Aborted. PersistentStoreDatabaseSetting not removed.",
            po_call_args[0][0][0],
        )

    @mock.patch("tethys_services.models.SpatialDatasetService")
    @mock.patch("tethys_services.models.DatasetService")
    @mock.patch("tethys_services.models.PersistentStoreService")
    @mock.patch("tethys_services.models.WebProcessingService")
    @mock.patch("tethys_compute.models.CondorScheduler")
    @mock.patch("tethys_compute.models.DaskScheduler")
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting")
    @mock.patch("tethys_apps.models.PersistentStoreConnectionSetting")
    @mock.patch("tethys_apps.models.SpatialDatasetServiceSetting")
    @mock.patch("tethys_apps.models.DatasetServiceSetting")
    @mock.patch("tethys_apps.models.SchedulerSetting")
    @mock.patch("tethys_apps.models.WebProcessingServiceSetting")
    @mock.patch("tethys_apps.models.TethysApp")
    @mock.patch("tethys_cli.cli_colors.pretty_output")
    def test_link_service_to_app_valid_keywords(self, mock_pretty_output, *args):
        service_setting_keywords = [
            ("condor", "ss_scheduler"),
            ("dask", "ss_scheduler"),
            ("dataset", "ds_dataset"),
            ("persistent", "ps_database"),
            ("persistent", "ps_connection"),
            ("spatial", "ds_spatial"),
            ("wps", "wps"),
        ]

        for service_type, setting_type in service_setting_keywords:
            result = utilities.link_service_to_app_setting(
                service_type=service_type,
                service_uid="123",
                app_package="foo_app",
                setting_type=setting_type,
                setting_uid="456",
            )
            self.assertTrue(result)

    @mock.patch("tethys_cli.cli_colors.pretty_output")
    @mock.patch("tethys_services.models.SpatialDatasetService")
    def test_link_service_to_app_setting_spatial_dss_does_not_exist(
        self, mock_service, mock_pretty_output
    ):
        from django.core.exceptions import ObjectDoesNotExist

        # Mock up the SpatialDatasetService to throw ObjectDoesNotExist
        mock_service.objects.get.side_effect = ObjectDoesNotExist

        # Based on exception, False will be returned
        result = utilities.link_service_to_app_setting(
            service_type="spatial",
            service_uid="123",
            app_package="foo_app",
            setting_type="ds_spatial",
            setting_uid="456",
        )

        self.assertEqual(False, result)
        mock_service.objects.get.assert_called_once_with(pk=123)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn("with ID/Name", po_call_args[0][0][0])
        self.assertIn("does not exist.", po_call_args[0][0][0])

    @mock.patch("tethys_cli.cli_colors.pretty_output")
    @mock.patch("tethys_services.models.SpatialDatasetService")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_link_service_to_app_setting_spatial_dss_value_error(
        self, mock_app, mock_service, mock_pretty_output
    ):
        from django.core.exceptions import ObjectDoesNotExist

        # Mock up TethysApp to throw ObjectDoesNotExist
        mock_app.objects.get.side_effect = ObjectDoesNotExist
        # Mock up the SpatialDatasetService to MagicMock
        mock_service.objects.get.return_value = mock.MagicMock()

        # Based on ValueError exception casting to int, then TethysApp ObjectDoesNotExist False will be returned
        result = utilities.link_service_to_app_setting(
            service_type="spatial",
            service_uid="foo_spatial_service",
            app_package="foo_app",
            setting_type="ds_spatial",
            setting_uid="456",
        )

        self.assertEqual(False, result)
        mock_service.objects.get.assert_called_once_with(name="foo_spatial_service")
        mock_app.objects.get.assert_called_once_with(package="foo_app")
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn("A Tethys App with the name", po_call_args[0][0][0])
        self.assertIn("does not exist. Aborted.", po_call_args[0][0][0])

    @mock.patch("tethys_cli.cli_colors.pretty_output")
    @mock.patch("tethys_services.models.SpatialDatasetService")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_link_service_to_app_setting_spatial_link_key_error(
        self, mock_app, mock_service, mock_pretty_output
    ):
        # Mock up TethysApp to MagicMock
        mock_app.objects.get.return_value = mock.MagicMock()
        # Mock up the SpatialDatasetService to MagicMock
        mock_service.objects.get.return_value = mock.MagicMock()

        # Based on KeyError for invalid setting_type False will be returned
        result = utilities.link_service_to_app_setting(
            service_type="spatial",
            service_uid="foo_spatial_service",
            app_package="foo_app",
            setting_type="foo_invalid",
            setting_uid="456",
        )

        self.assertEqual(False, result)
        mock_service.objects.get.assert_called_once_with(name="foo_spatial_service")
        mock_app.objects.get.assert_called_once_with(package="foo_app")
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            'The setting_type you specified ("foo_invalid") does not exist.',
            po_call_args[0][0][0],
        )
        self.assertIn(
            'Choose from: "ps_database|ps_connection|ds_spatial"', po_call_args[0][0][0]
        )

    @mock.patch("tethys_cli.cli_colors.pretty_output")
    @mock.patch("tethys_apps.models.SpatialDatasetServiceSetting")
    @mock.patch("tethys_services.models.SpatialDatasetService")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_link_service_to_app_setting_spatial_link_value_error_save(
        self, mock_app, mock_service, mock_setting, mock_pretty_output
    ):
        # Mock up TethysApp to MagicMock
        mock_app.objects.get.return_value = mock.MagicMock()
        # Mock up the SpatialDatasetService to MagicMock
        mock_service.objects.get.return_value = mock.MagicMock()
        # Mock up the SpatialDatasetServiceSetting to MagicMock
        mock_setting.objects.get.return_value = mock.MagicMock()
        mock_setting.objects.get().save.return_value = True

        # True will be returned, mocked save will be called
        result = utilities.link_service_to_app_setting(
            service_type="spatial",
            service_uid="foo_spatial_service",
            app_package="foo_app",
            setting_type="ds_spatial",
            setting_uid="foo_456",
        )

        self.assertEqual(True, result)
        mock_service.objects.get.assert_called_once_with(name="foo_spatial_service")
        mock_app.objects.get.assert_called_once_with(package="foo_app")
        mock_setting.objects.get.assert_called()
        mock_setting.objects.get().save.assert_called_once()
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn("was successfully linked to", po_call_args[0][0][0])

    @mock.patch("tethys_cli.cli_colors.pretty_output")
    @mock.patch(
        "tethys_apps.models.SpatialDatasetServiceSetting",
        __name__="SpatialDatasetServiceSetting",
    )
    @mock.patch("tethys_services.models.SpatialDatasetService")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_link_service_to_app_setting_spatial_link_does_not_exist(
        self, mock_app, mock_service, mock_setting, mock_pretty_output
    ):
        from django.core.exceptions import ObjectDoesNotExist

        # Mock up TethysApp to MagicMock
        mock_app.objects.get.return_value = mock.MagicMock()
        # Mock up the SpatialDatasetService to MagicMock
        mock_service.objects.get.return_value = mock.MagicMock()
        # Mock up the SpatialDatasetServiceSetting to MagicMock
        mock_setting.objects.get.side_effect = ObjectDoesNotExist

        # Based on KeyError for invalid setting_type False will be returned
        result = utilities.link_service_to_app_setting(
            service_type="spatial",
            service_uid="foo_spatial_service",
            app_package="foo_app",
            setting_type="ds_spatial",
            setting_uid="456",
        )

        self.assertEqual(False, result)
        mock_service.objects.get.assert_called_once_with(name="foo_spatial_service")
        mock_app.objects.get.assert_called_once_with(package="foo_app")
        mock_setting.objects.get.assert_called()
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "A SpatialDatasetServiceSetting with ID/Name", po_call_args[0][0][0]
        )
        self.assertIn("does not exist.", po_call_args[0][0][0])

    @mock.patch("tethys_apps.utilities.environ")
    @mock.patch("tethys_apps.utilities.Path.home")
    def test_get_tethys_home_dir__default_env_name__tethys_home_not_defined(
        self, mock_home, mock_environ
    ):
        env_tethys_home = None
        active_conda_env = "tethys"  # Default Tethys environment name
        expand_user_path = "/home/tethys"
        active_venv = "(test)"

        mock_environ.get.side_effect = [
            env_tethys_home,
            active_conda_env,
            active_venv,
        ]  # [TETHYS_HOME, CONDA_DEFAULT_ENV, VIRTUAL_ENV_PROMPT]
        mock_home.return_value = Path(expand_user_path)

        ret = utilities.get_tethys_home_dir()

        self.assertEqual(mock_environ.get.call_count, 3)
        mock_environ.get.assert_any_call("TETHYS_HOME")
        mock_environ.get.assert_any_call("CONDA_DEFAULT_ENV")
        mock_environ.get.assert_any_call("VIRTUAL_ENV_PROMPT", "")

        # Returns default tethys home environment
        self.assertEqual(str(Path(expand_user_path) / ".tethys"), ret)

    @mock.patch("tethys_apps.utilities.environ")
    @mock.patch("tethys_apps.utilities.Path.home")
    def test_get_tethys_home_dir__non_default_env_name__tethys_home_not_defined(
        self, mock_home, mock_environ
    ):
        env_tethys_home = None
        active_conda_env = "foo"  # Non-default Tethys environment name
        expand_user_path = "/home/tethys"
        active_venv = ""

        mock_environ.get.side_effect = [
            env_tethys_home,
            active_conda_env,
            active_venv,
        ]  # [TETHYS_HOME, CONDA_DEFAULT_ENV, VIRTUAL_ENV_PROMPT]
        mock_home.return_value = Path(expand_user_path)

        ret = utilities.get_tethys_home_dir()

        mock_environ.get.assert_any_call("TETHYS_HOME")
        mock_environ.get.assert_any_call("CONDA_DEFAULT_ENV")
        mock_environ.get.assert_any_call("VIRTUAL_ENV_PROMPT", "")

        # Returns joined path of default tethys home path and environment name
        self.assertEqual(
            str(Path(expand_user_path) / ".tethys" / active_conda_env), ret
        )

    @mock.patch("tethys_apps.utilities.environ")
    @mock.patch("tethys_apps.utilities.Path.home")
    def test_get_tethys_home_dir__tethys_home_defined(self, mock_home, mock_environ):
        env_tethys_home = "/foo/.bar"
        active_conda_env = "foo"
        active_venv = ""
        mock_environ.get.side_effect = [
            env_tethys_home,
            active_conda_env,
            active_venv,
        ]  # [TETHYS_HOME, CONDA_DEFAULT_ENV, VIRTUAL_ENV_PROMPT]

        ret = utilities.get_tethys_home_dir()

        mock_environ.get.assert_called_once_with("TETHYS_HOME")
        mock_home.assert_not_called()

        # Returns path defined by TETHYS_HOME environment variable
        self.assertEqual(env_tethys_home, ret)

    @mock.patch("tethys_apps.utilities.tethys_log")
    @mock.patch("tethys_apps.utilities.environ")
    @mock.patch("tethys_apps.utilities.Path.home")
    def test_get_tethys_home_dir__print_warning(
        self, mock_home, mock_environ, mock_tethys_log
    ):
        env_tethys_home = None
        active_conda_env = None
        active_venv = ""

        mock_environ.get.side_effect = [
            env_tethys_home,
            active_conda_env,
            active_venv,
        ]  # [TETHYS_HOME, CONDA_DEFAULT_ENV, VIRTUAL_ENV_PROMPT]
        mock_home_path = mock.MagicMock()
        mock_home_path.__truediv__.side_effect = ["good_path", Exception]
        mock_home.return_value = mock_home_path

        ret = utilities.get_tethys_home_dir()

        self.assertEqual(mock_environ.get.call_count, 3)
        mock_environ.get.assert_any_call("TETHYS_HOME")
        mock_environ.get.assert_any_call("CONDA_DEFAULT_ENV")
        mock_environ.get.assert_any_call("VIRTUAL_ENV_PROMPT", "")
        mock_tethys_log.warning.assert_called()

        # Returns default tethys home environment path
        self.assertEqual("good_path", ret)

    @mock.patch("tethys_apps.utilities.SingletonHarvester")
    def test_get_app_class(self, mock_harvester):
        """"""
        from tethysapp.test_app.app import App

        test_app = App()
        mock_harvester().apps = [test_app]

        mock_db_app = mock.MagicMock()
        mock_db_app.name = App.name  # This should match the name of App
        mock_db_app.package = App.package  # This should match the package of App

        ret = utilities.get_app_class(mock_db_app)

        # Should work because package is used to find the class, not the name
        self.assertTrue(ret is test_app)

    @mock.patch("tethys_apps.utilities.SingletonHarvester")
    def test_get_app_class__different_name(self, mock_harvester):
        """Test case when user changes name of app in DB (from app settings)."""
        from tethysapp.test_app.app import App

        test_app = App()
        mock_harvester().apps = [test_app]

        mock_db_app = mock.MagicMock()
        mock_db_app.name = "Different Name"  # This shouldn't match the name of App
        mock_db_app.package = "test_app"  # This should match the package of App

        ret = utilities.get_app_class(mock_db_app)

        # Should work because package is used to find the class, not the name
        self.assertTrue(ret is test_app)

    @mock.patch("tethys_apps.utilities.SingletonHarvester")
    def test_get_app_class__no_matching_class(self, mock_harvester):
        """Test case when no app class can be found for the app."""
        from tethysapp.test_app.app import App

        mock_harvester().apps = [App()]

        mock_db_app = mock.MagicMock()
        mock_db_app.name = App.name  # This should match the name of App
        mock_db_app.package = (
            "does_not_exist"  # This shouldn't match the package of App
        )

        ret = utilities.get_app_class(mock_db_app)

        # Should not work because package is used to find the class
        self.assertIsNone(ret)


class TestTethysAppsUtilitiesTethysTestCase(TethysTestCase):
    def set_up(self):
        self.c = self.get_test_client()
        self.user = self.create_test_user(
            username="joe", password="secret", email="joe@some_site.com"
        )

    def tear_down(self):
        self.user.delete()

    @mock.patch("django.conf.settings")
    def test_user_can_access_app(self, mock_settings):
        mock_settings.ENABLE_RESTRICTED_APP_ACCESS = False
        mock_settings.ENABLE_OPEN_PORTAL = False
        user = self.user
        app = utilities.get_active_app(url="/apps/test-app")

        result0 = utilities.user_can_access_app(user, app)
        self.assertTrue(result0)

        # test restricted access no permission
        mock_settings.ENABLE_RESTRICTED_APP_ACCESS = True
        result1 = utilities.user_can_access_app(user, app)
        self.assertFalse(result1)

        # test restricted access with restricted apps list
        mock_settings.ENABLE_RESTRICTED_APP_ACCESS = [app.package]
        result2 = utilities.user_can_access_app(user, app)
        self.assertFalse(result2)

        # test restricted access with no restricted apps list
        mock_settings.ENABLE_RESTRICTED_APP_ACCESS = []
        result3 = utilities.user_can_access_app(user, app)
        self.assertTrue(result3)

        # test restricted access with restricted apps list of a different app
        mock_settings.ENABLE_RESTRICTED_APP_ACCESS = ["some_other_app"]
        result4 = utilities.user_can_access_app(user, app)
        self.assertTrue(result4)

        # test with permission
        assign_perm(f"{app.package}:access_app", user, app)

        result5 = utilities.user_can_access_app(user, app)
        self.assertTrue(result5)

        # test open portal mode case
        mock_settings.ENABLE_OPEN_PORTAL = True
        result6 = utilities.user_can_access_app(user, app)
        self.assertTrue(result6)

        # test restricted access with restricted apps list
        mock_settings.ENABLE_RESTRICTED_APP_ACCESS = [app.package]
        result7 = utilities.user_can_access_app(user, app)
        self.assertTrue(result7)

    def test_get_installed_tethys_items_apps(self):
        # Get list of apps installed in the tethysapp directory
        result = utilities.get_installed_tethys_items(apps=True)
        self.assertIn("test_app", result)

    def test_get_installed_tethys_items_extensions(self):
        # Get list of apps installed in the tethysapp directory
        result = utilities.get_installed_tethys_items(extensions=True)
        self.assertIn("test_extension", result)

    def test_get_installed_tethys_items_both(self):
        # Get list of apps installed in the tethysapp directory
        result = utilities.get_installed_tethys_items(apps=True, extensions=True)
        self.assertIn("test_app", result)
        self.assertIn("test_extension", result)

    @mock.patch("tethys_apps.utilities.SingletonHarvester")
    def test_get_installed_tethys_items_exception(self, mock_harvester):
        mock_harvester().app_modules = {"foo_invalid_foo": "tethys_app.foo_invalid_foo"}

        result = utilities.get_installed_tethys_items(apps=True)
        self.assertEqual({}, result)

    @mock.patch("tethys_apps.utilities.get_installed_tethys_items")
    def test_get_installed_tethys_apps(self, mock_get_items):
        # Get a list of installed extensions
        utilities.get_installed_tethys_apps()
        mock_get_items.assert_called_with(apps=True)

    @mock.patch("tethys_apps.utilities.get_installed_tethys_items")
    def test_get_installed_tethys_extensions(self, mock_get_items):
        # Get a list of installed extensions
        utilities.get_installed_tethys_extensions()
        mock_get_items.assert_called_with(extensions=True)

    @mock.patch("tethys_apps.utilities.importlib.import_module")
    @mock.patch("tethys_apps.utilities.pkgutil.iter_modules")
    def test_get_all_submodules(self, mock_iter_modules, mock_import):
        mock_sub_module = mock.MagicMock()
        mock_sub_module.ispkg.return_value = True
        mock_iter_modules.side_effect = [[mock_sub_module], []]

        m = mock.MagicMock(__path__="path", __name__="name")
        mock_import.return_value = m
        result = utilities.get_all_submodules(m)
        self.assertEqual([m] * 3, result)

    @mock.patch("tethys_apps.utilities.yaml.dump")
    @mock.patch("tethys_apps.utilities.yaml.safe_load")
    @mock.patch.object(
        Path, "open", new_callable=lambda: mock.mock_open(read_data='{"secrets": "{}"}')
    )
    @mock.patch("tethys_apps.utilities.Path.exists", return_value=True)
    def test_delete_secrets(
        self, mock_exists, mock_open_file, mock_yaml_safe_load, mock_yaml_dumps
    ):
        app_target_name = "test_app"
        before_content = {
            "secrets": {
                app_target_name: {
                    "custom_settings_salt_strings": {
                        "Secret_Test2_without_required": "my_first_fake_string"
                    }
                },
                "version": "1.0",
            }
        }

        after_content = {
            "secrets": {
                app_target_name: {"custom_settings_salt_strings": {}},
                "version": "1.0",
            }
        }

        mock_yaml_safe_load.return_value = before_content
        utilities.delete_secrets(app_target_name)

        mock_yaml_dumps.assert_called_once_with(
            after_content, mock_open_file.return_value
        )

    @mock.patch("tethys_apps.utilities.yaml.dump")
    @mock.patch("tethys_apps.utilities.yaml.safe_load")
    @mock.patch.object(
        Path, "open", new_callable=lambda: mock.mock_open(read_data='{"secrets": "{}"}')
    )
    @mock.patch("tethys_apps.utilities.Path.exists", return_value=True)
    def test_delete_secrets_without_app_in_secrets_yml(
        self, mock_path, mock_open_file, mock_yaml_safe_load, mock_yaml_dumps
    ):
        app_target_name = "test_app"
        before_content = {"secrets": {"version": "1.0"}}

        after_content = {"secrets": {app_target_name: {}, "version": "1.0"}}

        mock_yaml_safe_load.return_value = before_content
        utilities.delete_secrets(app_target_name)

        mock_yaml_dumps.assert_called_once_with(
            after_content, mock_open_file.return_value
        )

    def test_get_secret_custom_settings(self):
        app_target_name = "test_app"

        secret_settings = utilities.get_secret_custom_settings(app_target_name)

        self.assertEqual(len(secret_settings), 2)

    def test_get_secret_custom_settings_without_app(self):
        app_target_name = "test_app2"
        return_val = utilities.get_secret_custom_settings(app_target_name)
        self.assertEqual(return_val, None)

    @mock.patch(
        "tethys_apps.utilities.Path.read_text", return_value='{"secrets": "{}"}'
    )
    @mock.patch("tethys_apps.utilities.Path.exists")
    @mock.patch("tethys_apps.utilities.yaml.safe_load")
    def test_secrets_signed_unsigned_value_with_secrets(
        self, mock_yaml_safe_load, mock_path_exists, _
    ):
        app_target_name = "test_app"

        before_content = {
            "secrets": {
                app_target_name: {
                    "custom_settings_salt_strings": {
                        "Secret_Test2_without_required": "my_first_fake_string"
                    }
                },
                "version": "1.0",
            }
        }
        mock_yaml_safe_load.return_value = before_content

        mock_path_exists.side_effect = [True, True, False, False]

        signer = Signer(salt="my_first_fake_string")
        mock_val = "SECRETXX1Y"

        secret_signed_mock = signer.sign_object("SECRETXX1Y")

        custom_secret_setting = mock.MagicMock(
            name="Secret_Test2_without_required",
            value=secret_signed_mock,
            type_custom_setting="SECRET",
        )
        custom_secret_setting.name.return_value = "Secret_Test2_without_required"

        # with secrets.yml

        # signing
        signed_secret = utilities.secrets_signed_unsigned_value(
            custom_secret_setting.name(), mock_val, app_target_name, True
        )
        self.assertEqual(signed_secret, secret_signed_mock)

        # unsigning
        unsigned_secret = utilities.secrets_signed_unsigned_value(
            custom_secret_setting.name(), secret_signed_mock, app_target_name, False
        )
        self.assertEqual(unsigned_secret, mock_val)

        # with no secrets.yml

        signer = Signer()
        secret_signed_mock = signer.sign_object("SECRETXX1Y")

        # signing
        signed_secret = utilities.secrets_signed_unsigned_value(
            custom_secret_setting.name(), mock_val, app_target_name, True
        )
        self.assertEqual(signed_secret, secret_signed_mock)

        # unsinging
        unsigned_secret = utilities.secrets_signed_unsigned_value(
            custom_secret_setting.name(), secret_signed_mock, app_target_name, False
        )
        self.assertEqual(unsigned_secret, mock_val)

    @override_settings(MULTIPLE_APP_MODE=False)
    def test_get_configured_standalone_app_no_app_name(self):
        from tethys_apps.models import TethysApp

        with mock.patch(
            "tethys_apps.models.TethysApp", wraps=TethysApp
        ) as mock_tethysapp:
            result = utilities.get_configured_standalone_app()

            self.assertEqual(result.package, "test_app")
            mock_tethysapp.objects.first.assert_called_once()

    @override_settings(MULTIPLE_APP_MODE=False, STANDALONE_APP="test_app")
    def test_get_configured_standalone_app_given_app_name(self):
        from tethys_apps.models import TethysApp

        with mock.patch(
            "tethys_apps.models.TethysApp", wraps=TethysApp
        ) as mock_tethysapp:
            result = utilities.get_configured_standalone_app()

            self.assertEqual(result.package, "test_app")
            mock_tethysapp.objects.get.assert_called_with(package="test_app")

    @override_settings(MULTIPLE_APP_MODE=False)
    def test_get_configured_standalone_app_no_app_name_no_installed(self):
        from tethys_apps.models import TethysApp

        with mock.patch(
            "tethys_apps.models.TethysApp", wraps=TethysApp
        ) as mock_tethysapp:
            mock_tethysapp.objects.first.return_value = []
            app = utilities.get_configured_standalone_app()

            self.assertTrue(app == [])
            mock_tethysapp.objects.first.assert_called_once()

    @override_settings(MULTIPLE_APP_MODE=False)
    def test_get_configured_standalone_app_db_not_ready(self):
        from tethys_apps.models import TethysApp
        from django.db.utils import ProgrammingError

        with mock.patch(
            "tethys_apps.models.TethysApp", wraps=TethysApp
        ) as mock_tethysapp:
            mock_tethysapp.DoesNotExist = TethysApp.DoesNotExist
            mock_tethysapp.objects.first.side_effect = [ProgrammingError]
            app = utilities.get_configured_standalone_app()

            self.assertIsNone(app)

            mock_tethysapp.objects.first.assert_called_once()

    def test_update_decorated_websocket_consumer_class(self):
        class TestConsumer(WebsocketConsumer):
            def authorized_connect(self):
                """Connects to the websocket consumer and adds a notifications group to the channel"""
                return "authorized_connect_run"

        permissions_required = ["test_permission"]
        permissions_use_or = True
        login_required = False
        with_paths = False
        updated_class = utilities.update_decorated_websocket_consumer_class(
            TestConsumer,
            permissions_required,
            permissions_use_or,
            login_required,
            with_paths,
        )

        self.assertTrue(updated_class.permissions == permissions_required)
        self.assertTrue(updated_class.permissions_use_or == permissions_use_or)
        self.assertTrue(updated_class.login_required == login_required)
        self.assertTrue(
            updated_class().authorized_connect() == "authorized_connect_run"
        )


class TestAsyncUtilities(unittest.IsolatedAsyncioTestCase):
    def set_up(self):
        pass

    def tear_down(self):
        pass

    async def test_update_decorated_websocket_consumer_class_async(self):
        class TestConsumer(AsyncWebsocketConsumer):
            async def authorized_connect(self):
                """Connects to the websocket consumer and adds a notifications group to the channel"""
                return "authorized_connect_run"

        permissions_required = ["test_permission"]
        permissions_use_or = True
        login_required = False
        with_paths = False
        updated_class = utilities.update_decorated_websocket_consumer_class(
            TestConsumer,
            permissions_required,
            permissions_use_or,
            login_required,
            with_paths,
        )

        self.assertTrue(updated_class.permissions == permissions_required)
        self.assertTrue(updated_class.permissions_use_or == permissions_use_or)
        self.assertTrue(updated_class.login_required == login_required)
        self.assertTrue(
            await updated_class().authorized_connect() == "authorized_connect_run"
        )
