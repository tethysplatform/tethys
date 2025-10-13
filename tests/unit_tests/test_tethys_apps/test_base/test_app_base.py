from pathlib import Path
from types import FunctionType
import unittest
from unittest import mock
import uuid
from django.db.utils import ProgrammingError
from django.test import RequestFactory, override_settings
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from tethys_apps.exceptions import (
    TethysAppSettingDoesNotExist,
    TethysAppSettingNotAssigned,
)
import tethys_apps.base.app_base as tethys_app_base
from tethys_apps.base.paths import TethysPath
from tethys_apps.base.permissions import Permission, PermissionGroup
import tethys_sdk.paths as paths
from ... import UserFactory


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


class TethysBaseChild(tethys_app_base.TethysBase):
    """
    Tethys Base class for testing
    """

    package = "test_base"


class TestTethysBase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_package_namespace(self):
        base = tethys_app_base.TethysBase()

        # assertRaises needs a callable, not a property
        def get_package_namespace():
            return base.package_namespace

        self.assertRaises(NotImplementedError, get_package_namespace)

    @mock.patch("tethys_cli.cli_colors.write_error")
    def test_resolve_bokeh_handler(self, mock_write_error):
        base = tethys_app_base.TethysBase()
        with mock.patch("tethys_apps.base.app_base.has_bokeh_django", False):
            base._resolve_bokeh_handler(None, None, print, None)
            mock_write_error.assert_called_once()
            mock_write_error.assert_called_with(
                'ERROR! The the "" app has a Bokeh-type handler "print", '
                'but the "bokeh_django" package is not installed. '
                'Please install "bokeh_django" for the app to function properly.'
            )

    @mock.patch("tethys_apps.base.controller.register_controllers")
    def test_register_url_maps(self, mock_rc):
        app = tethys_app_base.TethysAppBase()
        app.package = "package"
        app.root_url = "root_url"
        app.index = "index"
        app.register_url_maps()

        kwargs = mock_rc.call_args_list[0][1]
        modules = [
            f"tethysapp.package.{name}"
            for name in tethys_app_base.DEFAULT_CONTROLLER_MODULES
        ]
        self.assertEqual(app.root_url, kwargs["root_url"])
        for m in kwargs["modules"]:
            self.assertIn(m, modules)
        self.assertIn(app.index, kwargs["index"])

    @mock.patch("tethys_apps.base.app_base.re_path")
    @mock.patch("tethys_apps.base.app_base.TethysBaseMixin")
    def test_url_patterns(self, mock_tbm, mock_re_path):
        app = tethys_app_base.TethysAppBase()
        app.root_url = "foo"
        url_map = mock.MagicMock(
            controller="test_app.controllers.home", url="test-url", protocol="http"
        )
        url_map.name = "home"
        url_map_ws = mock.MagicMock(
            controller="test_app.controllers.TestWS",
            url="test-url-ws",
            protocol="websocket",
        )
        url_map_ws.name = "ws"
        app.register_url_maps = mock.MagicMock(return_value=[url_map, url_map_ws])
        mock_tbm.return_value = mock.MagicMock(url_maps="test-app")

        # Execute
        result = app.url_patterns
        # Check url call at django_url = url...
        rts_call_args_list = mock_re_path.call_args_list
        http_url_call = rts_call_args_list[0]
        ws_url_call = rts_call_args_list[1]
        self.assertEqual("test-url", http_url_call.args[0])
        self.assertEqual("test-url-ws", ws_url_call.args[0])
        self.assertIn("name", http_url_call.kwargs)
        self.assertIn("name", ws_url_call.kwargs)
        self.assertEqual("home", http_url_call.kwargs["name"])
        self.assertEqual("ws", ws_url_call.kwargs["name"])
        self.assertIn("foo", result["http"])
        self.assertIn("foo", result["websocket"])
        self.assertIsInstance(http_url_call.args[1], FunctionType)
        self.assertIsInstance(ws_url_call.args[1], type)

    @mock.patch("tethys_apps.base.app_base.re_path")
    @mock.patch("tethys_apps.base.app_base.TethysBaseMixin")
    def test_url_patterns_no_str(self, mock_tbm, mock_re_path):
        app = tethys_app_base.TethysAppBase()

        def test_func():
            return ""

        url_map = mock.MagicMock(controller=test_func, url="test-app", protocol="http")
        url_map.name = "home"
        app.register_url_maps = mock.MagicMock(return_value=[url_map])
        mock_tbm.return_value = mock.MagicMock(url_maps="test-app")

        # Execute
        app.url_patterns

        # Check url call at django_url = url...
        rts_call_args = mock_re_path.call_args
        self.assertEqual("test-app", rts_call_args.args[0])
        self.assertIn("name", rts_call_args.kwargs)
        self.assertEqual("home", rts_call_args.kwargs["name"])
        self.assertIs(rts_call_args.args[1], test_func)

    @mock.patch("tethys_apps.base.app_base.tethys_log")
    @mock.patch("tethys_apps.base.app_base.TethysBaseMixin")
    def test_url_patterns_import_error(self, mock_tbm, mock_log):
        mock_error = mock_log.error
        app = tethys_app_base.TethysAppBase()
        url_map = mock.MagicMock(
            controller="1module.1function", url="test-app", protocol="http"
        )
        url_map.name = "home"
        app.register_url_maps = mock.MagicMock(return_value=[url_map])
        mock_tbm.return_value = mock.MagicMock(url_maps="test-app")

        # assertRaises needs a callable, not a property
        def test_url_patterns():
            return app.url_patterns

        # Check Error Message
        self.assertRaises(ImportError, test_url_patterns)
        rts_call_args = mock_error.call_args
        error_message = (
            "The following error occurred while trying to import"
            ' the controller function "1module.1function"'
        )
        self.assertIn(error_message, rts_call_args.args[0])

    @mock.patch("tethys_apps.base.app_base.tethys_log")
    @mock.patch("tethys_apps.base.app_base.TethysBaseMixin")
    def test_url_patterns_attribute_error(self, mock_tbm, mock_log):
        mock_error = mock_log.error
        app = tethys_app_base.TethysAppBase()
        url_map = mock.MagicMock(
            controller="test_app.controllers.home1", url="test-app", protocol="http"
        )
        url_map.name = "home"
        app.register_url_maps = mock.MagicMock(return_value=[url_map])
        mock_tbm.return_value = mock.MagicMock(url_maps="test-app")

        # assertRaises needs a callable, not a property
        def test_url_patterns():
            return app.url_patterns

        # Check Error Message
        self.assertRaises(AttributeError, test_url_patterns)
        rts_call_args = mock_error.call_args
        error_message = (
            "The following error occurred while trying to access"
            ' the controller function "test_app.controllers.home1"'
        )
        self.assertIn(error_message, rts_call_args.args[0])

    @mock.patch("tethys_apps.base.app_base.re_path")
    @mock.patch("tethys_apps.base.app_base.TethysBaseMixin")
    def test_handler_patterns(self, mock_tbm, mock_re_path):
        app = tethys_app_base.TethysAppBase()
        app.root_url = "test-url"
        url_map = mock.MagicMock(
            controller="test_app.controllers.home_controller",
            handler="test_app.controllers.home",
            handler_type="bokeh",
            url="",
        )
        url_map.name = "home"

        app.register_url_maps = mock.MagicMock(return_value=[url_map])
        mock_tbm.return_value = mock.MagicMock(
            url_maps=[
                "test-app",
            ]
        )

        # Execute
        result = app.handler_patterns

        # Verify format of return
        self.assertIn("http", result)
        self.assertIn("websocket", result)
        self.assertIn("test_url", result["http"])
        self.assertIn("test_url", result["websocket"])

        # Verify call of url for http endpoint
        http_url_call = mock_re_path.call_args_list[0]
        self.assertEqual(r"^basename/autoload.js$", http_url_call.args[0])
        self.assertIn("name", http_url_call.kwargs)
        self.assertEqual("home_bokeh_autoload", http_url_call.kwargs["name"])

        # Verify call of url for websocket endpoint
        ws_url_call = mock_re_path.call_args_list[1]
        self.assertEqual(r"^basename/ws$", ws_url_call.args[0])
        self.assertIn("name", ws_url_call.kwargs)
        self.assertEqual("home_bokeh_ws", ws_url_call.kwargs["name"])

    @mock.patch("tethys_apps.base.app_base.WSConsumer")
    @mock.patch("tethys_apps.base.app_base.AutoloadJsConsumer")
    @mock.patch("tethys_apps.base.app_base.re_path")
    @mock.patch("tethys_apps.base.app_base.TethysBaseMixin")
    def test_handler_patterns_from_function(
        self, mock_tbm, mock_re_path, mock_ajsc, mock_wsc
    ):
        app = tethys_app_base.TethysAppBase()
        app._namespace = "foo"
        app.root_url = "test-url"

        def test_func(mock_doc):
            return ""

        url_map = mock.MagicMock(
            controller="test_app.controllers.home",
            handler=test_func,
            handler_type="bokeh",
            url="",
        )
        url_map.name = "home"
        app.register_url_maps = mock.MagicMock(return_value=[url_map])
        mock_tbm.return_value = mock.MagicMock(
            url_maps=[
                "test-app",
            ]
        )

        app.handler_patterns

        # Verify call of url for http endpoint
        http_url_call = mock_re_path.call_args_list[0]
        self.assertEqual(r"^basename/autoload.js$", http_url_call.args[0])
        self.assertEqual(mock_ajsc.as_asgi(), http_url_call.args[1])
        self.assertIn("name", http_url_call.kwargs)
        self.assertEqual("home_bokeh_autoload", http_url_call.kwargs["name"])
        mock_ajsc.as_asgi.assert_called()

        # Verify call of url for websocket endpoint
        ws_url_call = mock_re_path.call_args_list[1]
        self.assertEqual(r"^basename/ws$", ws_url_call.args[0])
        self.assertEqual(mock_wsc.as_asgi(), ws_url_call.args[1])
        self.assertIn("name", ws_url_call.kwargs)
        self.assertEqual("home_bokeh_ws", ws_url_call.kwargs["name"])
        mock_wsc.as_asgi.assert_called()

    @mock.patch("tethys_apps.base.app_base.re_path")
    @mock.patch("tethys_apps.base.app_base.TethysBaseMixin")
    def test_handler_patterns_url_basename(self, mock_tbm, mock_re_path):
        app = tethys_app_base.TethysAppBase()
        app._namespace = "foo"
        app.root_url = "test-url"

        def test_func(mock_doc):
            return ""

        url_map = mock.MagicMock(
            controller="test_app.controllers.home",
            handler=test_func,
            handler_type="bokeh",
        )
        url_map.name = "basename"
        url_map.url = "basename/"
        app.register_url_maps = mock.MagicMock(return_value=[url_map])
        mock_tbm.return_value = mock.MagicMock(
            url_maps=[
                "basename/",
            ]
        )

        app.handler_patterns

        # Verify call of url for http endpoint
        http_url_call = mock_re_path.call_args_list[0]
        self.assertEqual(r"^basename/autoload.js$", http_url_call.args[0])
        self.assertIn("name", http_url_call.kwargs)
        self.assertEqual("basename_bokeh_autoload", http_url_call.kwargs["name"])

        # Verify call of url for websocket endpoint
        ws_url_call = mock_re_path.call_args_list[1]
        self.assertEqual(r"^basename/ws$", ws_url_call.args[0])
        self.assertIn("name", ws_url_call.kwargs)
        self.assertEqual("basename_bokeh_ws", ws_url_call.kwargs["name"])

    @mock.patch("tethys_apps.base.app_base.tethys_log")
    @mock.patch("tethys_apps.base.app_base.TethysBaseMixin")
    def test_handler_patterns_import_error(self, mock_tbm, mock_log):
        mock_error = mock_log.error
        app = tethys_app_base.TethysAppBase()
        url_map = mock.MagicMock(
            controller="test_app.controllers.home",
            handler="1module.1function",
            handler_type="bokeh",
            url="",
        )
        url_map.name = "home"
        app.register_url_maps = mock.MagicMock(return_value=[url_map])
        mock_tbm.return_value = mock.MagicMock(
            url_maps=[
                "test-app",
            ]
        )

        # assertRaises needs a callable, not a property
        def test_handler_patterns():
            return app.handler_patterns

        # Check Error Message
        self.assertRaises(ImportError, test_handler_patterns)
        rts_call_args = mock_error.call_args
        error_message = (
            "The following error occurred while trying to import "
            'the handler function "1module.1function"'
        )
        self.assertIn(error_message, rts_call_args.args[0])

    @mock.patch("tethys_apps.base.app_base.tethys_log")
    @mock.patch("tethys_apps.base.app_base.TethysBaseMixin")
    def test_handler_patterns_attribute_error(self, mock_tbm, mock_log):
        mock_error = mock_log.error
        app = tethys_app_base.TethysAppBase()
        url_map = mock.MagicMock(
            controller="test_app.controllers.home",
            handler="test_app.controllers.home_handler1",
            handler_type="bokeh",
            url="",
        )
        url_map.name = "home"
        app.register_url_maps = mock.MagicMock(return_value=[url_map])
        mock_tbm.return_value = mock.MagicMock(url_maps="test-app")

        # assertRaises needs a callable, not a property
        def test_handler_patterns():
            return app.handler_patterns

        # Check Error Message
        self.assertRaises(AttributeError, test_handler_patterns)
        rts_call_args = mock_error.call_args
        error_message = (
            "The following error occurred while trying to access "
            'the handler function "test_app.controllers.home_handler1"'
        )
        self.assertIn(error_message, rts_call_args.args[0])

    def test_sync_with_tethys_db(self):
        self.assertRaises(
            NotImplementedError, tethys_app_base.TethysBase().sync_with_tethys_db
        )

    def test_remove_from_db(self):
        self.assertRaises(
            NotImplementedError, tethys_app_base.TethysBase().remove_from_db
        )

    def test_db_model(self):
        with self.assertRaises(NotImplementedError):
            tethys_app_base.TethysBase.db_model

    def test_db_object(self):
        with self.assertRaises(NotImplementedError):
            tethys_app_base.TethysBase.db_object

    @mock.patch("tethys_apps.base.app_base.render")
    def test_render(self, mock_render):
        mock_request = mock.MagicMock()
        template = "test.html"
        TethysBaseChild.render(mock_request, template)
        self.assertEqual(
            mock_render.call_args.args,
            (mock_request, f"{TethysBaseChild.package}/{template}"),
        )

    @mock.patch("tethys_apps.base.app_base.redirect")
    def test_redirect(self, mock_redirect):
        TethysBaseChild.redirect("test")
        mock_redirect.assert_called_with(f"{TethysBaseChild.package}:test")

    @mock.patch("tethys_apps.base.app_base.redirect")
    def test_redirect_absolute(self, mock_redirect):
        TethysBaseChild.redirect("/test")
        mock_redirect.assert_called_with("/test")

    @mock.patch("tethys_apps.base.app_base.reverse")
    def test_reverse(self, mock_reverse):
        TethysBaseChild.reverse("test")
        self.assertEqual(
            mock_reverse.call_args.args, (f"{TethysBaseChild.package}:test",)
        )

    @mock.patch("tethys_apps.base.app_base.render_to_string")
    def test_render_to_string(self, mock_render):
        TethysBaseChild.render_to_string("test")
        self.assertEqual(
            mock_render.call_args.args, (f"{TethysBaseChild.package}/test",)
        )


class TestTethysExtensionBase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test__str__(self):
        result = tethys_app_base.TethysExtensionBase().__str__()
        self.assertEqual("<TethysExt: >", result)

    def test__repr__(self):
        result = tethys_app_base.TethysExtensionBase().__repr__()
        self.assertEqual("<TethysExt: >", result)

    def test_package_namespace(self):
        ret = tethys_app_base.TethysExtensionBase.package_namespace
        self.assertEqual("tethysext", ret)

    def test_db_model(self):
        from tethys_apps.models import TethysExtension

        ret = tethys_app_base.TethysExtensionBase.db_model
        self.assertIs(TethysExtension, ret)

    @mock.patch("tethys_apps.models.TethysExtension")
    def test_db_object(self, mock_TethysExtension):
        ret = tethys_app_base.TethysExtensionBase.db_object
        self.assertEqual(mock_TethysExtension.objects.get(), ret)

    @mock.patch("tethys_apps.models.TethysExtension")
    def test_id(self, mock_TethysExtension):
        ret = tethys_app_base.TethysExtensionBase.id
        self.assertEqual(mock_TethysExtension.objects.get().id, ret)

    @mock.patch("tethys_apps.base.controller.register_controllers")
    def test_url_maps(self, mock_rc):
        ext = tethys_app_base.TethysExtensionBase()
        ext.package = "package"
        ext.root_url = "root_url"
        ext.index = "index"
        ext.register_url_maps()
        kwargs = mock_rc.call_args_list[0][1]
        modules = [
            f"tethysext.package.{name}"
            for name in tethys_app_base.DEFAULT_CONTROLLER_MODULES
        ]
        self.assertEqual(ext.root_url, kwargs["root_url"])
        for m in kwargs["modules"]:
            self.assertIn(m, modules)
        self.assertIn(ext.index, kwargs["index"])

    @mock.patch("tethys_apps.models.TethysExtension")
    def test_sync_with_tethys_db(self, mock_te):
        mock_te.objects.filter().all.return_value = []

        tethys_app_base.TethysExtensionBase().sync_with_tethys_db()

        mock_te.assert_called_with(description="", name="", package="", root_url="")
        mock_te().save.assert_called()

    @mock.patch("django.conf.settings")
    @mock.patch("tethys_apps.models.TethysExtension")
    def test_sync_with_tethys_db_exists(self, mock_te, mock_ds):
        mock_ds.DEBUG = True
        ext = tethys_app_base.TethysExtensionBase()
        ext.root_url = "test_url"
        mock_te2 = mock.MagicMock()
        mock_te.objects.filter().all.return_value = [mock_te2]
        ext.sync_with_tethys_db()

        # Check_result
        self.assertTrue(mock_te2.save.call_count == 2)

    @mock.patch("tethys_apps.base.app_base.tethys_log")
    @mock.patch("tethys_apps.models.TethysExtension")
    def test_sync_with_tethys_db_exists_log_error(self, mock_te, mock_log):
        mock_error = mock_log.error
        ext = tethys_app_base.TethysExtensionBase()
        ext.root_url = "test_url"
        mock_te.objects.filter().all.side_effect = Exception("test_error")
        ext.sync_with_tethys_db()

        # Check_result
        rts_call_args = mock_error.call_args
        self.assertEqual("test_error", rts_call_args.args[0].args[0])

    @mock.patch("tethys_apps.base.app_base.tethys_log")
    @mock.patch("tethys_apps.models.TethysExtension")
    def test_sync_with_tethys_db_exists_progamming_error(self, mock_te, mock_log):
        mock_warning = mock_log.warning
        ext = tethys_app_base.TethysExtensionBase()
        ext.root_url = "test_url"
        mock_te.objects.filter().all.side_effect = ProgrammingError("test_error")
        ext.sync_with_tethys_db()

        # Check_result
        mock_warning.assert_called_with(
            "Unable to sync extension with database. "
            "tethys_apps_tethysextension table does not exist"
        )


class TestTethysAppBase(unittest.TestCase):
    def setUp(self):
        self.app = tethys_app_base.TethysAppBase()
        self.user = UserFactory()
        self.request_factory = RequestFactory()
        self.fake_name = "fake_name"

    def tearDown(self):
        pass

    def test__str__(self):
        result = tethys_app_base.TethysAppBase().__str__()
        self.assertEqual("<TethysApp: >", result)

    def test__repr__(self):
        result = tethys_app_base.TethysAppBase().__repr__()
        self.assertEqual("<TethysApp: >", result)

    def test_package_namespace(self):
        ret = tethys_app_base.TethysAppBase.package_namespace
        self.assertEqual("tethysapp", ret)

    @mock.patch("tethys_apps.base.paths.Path.mkdir")
    @mock.patch("tethys_apps.base.app_base.files")
    def test_public_path(self, mock_files, __):
        mock_files.return_value = Path("tethysapp")
        ret = tethys_app_base.TethysAppBase().public_path
        self.assertEqual(TethysPath("tethysapp/public").path, ret.path)

    def test_get_app_public(self):
        ret = paths.get_app_public(TethysAppChild)
        self.assertEqual(TethysAppChild().public_path.path, ret.path)

    @mock.patch("tethys_apps.base.paths.Path.mkdir")
    @mock.patch("tethys_apps.base.app_base.files")
    def test_resources_path(self, mock_files, __):
        mock_files.return_value = Path("tethysapp")
        ret = tethys_app_base.TethysAppBase().resources_path
        self.assertEqual(TethysPath("tethysapp/resources").path, ret.path)

    @mock.patch("tethys_apps.base.paths.Path.mkdir")
    @mock.patch("tethys_apps.base.app_base.files")
    def test_cookie_config_path(self, mock_files, __):
        mock_files.return_value = Path("tethysapp")
        ret = tethys_app_base.TethysAppBase().cookie_config_path
        self.assertEqual(TethysPath("tethysapp/resources/cookies.yaml").path, ret)

    def test_get_app_resources(self):
        ret = paths.get_app_resources(TethysAppChild)
        self.assertEqual(TethysAppChild().resources_path.path, ret.path)

    def test_db_model(self):
        from tethys_apps.models import TethysApp

        ret = tethys_app_base.TethysAppBase.db_model
        self.assertIs(TethysApp, ret)

    @mock.patch("tethys_apps.models.TethysApp")
    def test_db_object(self, mock_TethysApp):
        ret = tethys_app_base.TethysAppBase.db_object
        self.assertEqual(mock_TethysApp.objects.get(), ret)

    @mock.patch("tethys_apps.models.TethysApp")
    def test_id(self, mock_TethysApp):
        ret = tethys_app_base.TethysAppBase.id
        self.assertEqual(mock_TethysApp.objects.get().id, ret)

    def test_custom_settings(self):
        self.assertIsNone(tethys_app_base.TethysAppBase().custom_settings())

    def test_persistent_store_settings(self):
        self.assertIsNone(tethys_app_base.TethysAppBase().persistent_store_settings())

    def test_dataset_service_settings(self):
        self.assertIsNone(tethys_app_base.TethysAppBase().dataset_service_settings())

    def test_spatial_dataset_service_settings(self):
        self.assertIsNone(
            tethys_app_base.TethysAppBase().spatial_dataset_service_settings()
        )

    def test_web_processing_service_settings(self):
        self.assertIsNone(
            tethys_app_base.TethysAppBase().web_processing_service_settings()
        )

    def test_handoff_handlers(self):
        self.assertIsNone(tethys_app_base.TethysAppBase().handoff_handlers())

    def test_permissions(self):
        self.assertIsNone(tethys_app_base.TethysAppBase().permissions())

    @mock.patch("guardian.shortcuts.get_perms")
    @mock.patch("guardian.shortcuts.remove_perm")
    @mock.patch("guardian.shortcuts.assign_perm")
    @mock.patch("tethys_apps.models.TethysApp")
    @mock.patch("django.contrib.auth.models.Group")
    @mock.patch("django.contrib.auth.models.Permission")
    def test_register_app_permissions(
        self, mock_dp, mock_dg, mock_ta, mock_asg, mock_rem, mock_get
    ):
        group_name = "test_group"
        create_test_perm = Permission(name="create_test", description="test_create")
        delete_test_perm = Permission(name="delete_test", description="test_delete")
        group_perm = PermissionGroup(
            name=group_name, permissions=[create_test_perm, delete_test_perm]
        )
        self.app.permissions = mock.MagicMock(
            return_value=[create_test_perm, group_perm]
        )

        # Mock db_app_permissions
        db_app_permission = mock.MagicMock(codename="test_code")
        mock_perm_query = mock_dp.objects.filter().filter().all
        mock_perm_query.return_value = [db_app_permission]

        # Mock Group.objects.filter
        db_group = mock.MagicMock()
        db_group.name = "test_app_name:group"

        mock_group = mock_dg.objects.filter().all
        mock_group.return_value = [db_group]

        # Mock TethysApp.objects.all()
        db_app = mock.MagicMock(package="test_app_name")

        mock_toa = mock_ta.objects.all
        mock_toa.return_value = [db_app]

        # Mock TethysApp.objects.get()
        mock_ta_get = mock_ta.objects.get
        mock_ta_get.return_value = "test_get"

        # Mock Group.objects.get()
        mock_group_get = mock_dg.objects.get
        mock_group_get.return_value = group_name

        # Mock get permission get_perms(g, db_app)
        mock_get.return_value = ["create_test"]

        # Execute
        self.app.register_app_permissions()

        # Check if db_app_permission.delete() is called
        db_app_permission.delete.assert_called_with()

        # Check if p.saved is called in perm
        mock_dp.objects.get().save.assert_called_with()

        # Check if db_group.delete() is called
        db_group.delete.assert_called_with()

        # Check if remove_perm(p, g, db_app) is called
        mock_rem.assert_called_with("create_test", group_name, "test_get")

        # Check if assign_perm(p, g, db_app) is called
        mock_asg.assert_called_with(":delete_test", group_name, "test_get")

    @mock.patch("guardian.shortcuts.get_perms")
    @mock.patch("guardian.shortcuts.remove_perm")
    @mock.patch("guardian.shortcuts.assign_perm")
    @mock.patch("tethys_apps.models.TethysApp")
    @mock.patch("django.contrib.auth.models.Group")
    @mock.patch("django.contrib.auth.models.Permission")
    def test_register_app_permissions_except_permission(
        self, mock_dp, mock_dg, mock_ta, mock_asg, mock_rem, mock_get
    ):
        group_name = "test_group"
        create_test_perm = Permission(name="create_test", description="test_create")
        delete_test_perm = Permission(name="delete_test", description="test_delete")
        group_perm = PermissionGroup(
            name=group_name, permissions=[create_test_perm, delete_test_perm]
        )
        self.app.permissions = mock.MagicMock(
            return_value=[create_test_perm, group_perm]
        )

        # Mock Permission.objects.filter
        db_app_permission = mock.MagicMock(codename="test_code")
        mock_perm_query = mock_dp.objects.filter().filter().all
        mock_perm_query.return_value = [db_app_permission]

        # Mock Permission.DoesNotExist
        mock_dp.DoesNotExist = Exception
        # Mock Permission.objects.get
        mock_perm_get = mock_dp.objects.get
        mock_perm_get.side_effect = Exception

        # Mock Group.objects.filter
        db_group = mock.MagicMock()
        db_group.name = "test_app_name:group"

        mock_group = mock_dg.objects.filter().all
        mock_group.return_value = [db_group]

        # Mock TethysApp.objects.all()
        db_app = mock.MagicMock(package="test_app_name")

        mock_toa = mock_ta.objects.all
        mock_toa.return_value = [db_app]

        # Mock TethysApp.objects.get()
        mock_ta_get = mock_ta.objects.get
        mock_ta_get.return_value = "test_get"

        # Mock Permission.DoesNotExist
        mock_dg.DoesNotExist = Exception

        # Mock Permission.objects.get
        mock_group_get = mock_dg.objects.get
        mock_group_get.side_effect = Exception

        # Execute
        self.app.register_app_permissions()

        # Check if Permission in Permission.DoesNotExist is called
        rts_call_args_list = mock_dp.call_args_list

        codename_check = []
        name_check = []
        for i in range(len(rts_call_args_list)):
            codename_check.append(rts_call_args_list[i].kwargs["codename"])
            name_check.append(rts_call_args_list[i].kwargs["name"])

        self.assertIn(":create_test", codename_check)
        self.assertIn(" | test_create", name_check)

        # Check if db_group.delete() is called
        db_group.delete.assert_called_with()

        # Check if Permission is called inside DoesNotExist
        mock_dp.assert_any_call(
            codename=":create_test",
            content_type=mock_ta.get_content_type(),
            name=" | test_create",
        )

        # Check if p.save() is called inside DoesNotExist
        mock_dp().save.assert_called()

        # Check if Group in Group.DoesNotExist is called
        rts_call_args = mock_dg.call_args
        self.assertEqual(":test_group", rts_call_args.kwargs["name"])

        # Check if Group(name=group) is called
        mock_dg.assert_called_with(name=":test_group")

        # Check if g.save() is called
        mock_dg().save.assert_called()

        # Check if assign_perm(p, g, db_app) is called
        rts_call_args_list = mock_asg.call_args_list
        check_list = []
        for i in range(len(rts_call_args_list)):
            for j in [0, 2]:  # only get first and last element to check
                check_list.append(rts_call_args_list[i].args[j])

        self.assertIn(":create_test", check_list)
        self.assertIn("test_get", check_list)
        self.assertIn(":delete_test", check_list)
        self.assertIn("test_get", check_list)

    @mock.patch("tethys_apps.base.app_base.HandoffManager")
    def test_get_handoff_manager(self, mock_hom):
        mock_hom.return_value = "test_handoff"
        self.assertEqual("test_handoff", self.app.get_handoff_manager())

    @mock.patch("tethys_compute.job_manager.JobManager")
    def test_get_job_manager(self, mock_jm):
        mock_jm.return_value = "test_job_manager"
        self.assertEqual("test_job_manager", self.app.get_job_manager())

    @mock.patch("tethys_apps.base.app_base.get_user_workspace")
    def test_get_user_workspace(self, mock_guw):
        mock_user = mock.MagicMock()
        ret = TethysAppChild.get_user_workspace(mock_user)
        mock_guw.assert_called_with(TethysAppChild, mock_user)
        self.assertEqual(ret, mock_guw())

    @mock.patch("tethys_apps.base.app_base.get_user_media")
    def test_get_user_media(self, mock_gum):
        mock_user = mock.MagicMock()
        ret = TethysAppChild.get_user_media(mock_user)
        mock_gum.assert_called_with(TethysAppChild, mock_user)
        self.assertEqual(ret, mock_gum())

    @mock.patch("tethys_apps.base.app_base.get_app_workspace")
    def test_get_app_workspace(self, mock_gaw):
        ret = TethysAppChild.get_app_workspace()
        mock_gaw.assert_called_with(TethysAppChild)
        self.assertEqual(ret, mock_gaw())

    @mock.patch("tethys_apps.base.app_base.get_app_media")
    def test_get_app_media(self, mock_gam):
        ret = TethysAppChild.get_app_media()
        mock_gam.assert_called_with(TethysAppChild)
        self.assertEqual(ret, mock_gam())

    @mock.patch("tethys_apps.models.TethysApp")
    def test_get_custom_setting(self, mock_ta):
        setting_name = "fake_setting"
        result = TethysAppChild.get_custom_setting(name=setting_name)
        mock_ta.objects.get.assert_called_with(package=TethysAppChild.package)
        mock_ta.objects.get().custom_settings.get.assert_called_with(name=setting_name)
        mock_ta.objects.get().custom_settings.get().get_value.assert_called()
        self.assertEqual(
            mock_ta.objects.get().custom_settings.get().get_value(), result
        )

    @mock.patch("tethys_apps.models.TethysApp")
    def test_get_custom_setting_object_not_exist(self, mock_ta):
        mock_db_app = mock_ta.objects.get
        mock_db_app.return_value = mock.MagicMock()

        mock_custom_settings = mock_ta.objects.get().custom_settings.get
        mock_custom_settings.side_effect = ObjectDoesNotExist

        with self.assertRaises(TethysAppSettingDoesNotExist) as cm:
            TethysAppChild.get_custom_setting(name=self.fake_name)

        self.assertEqual(
            'A CustomTethysAppSetting named "fake_name" does not '
            "exist in the b'Test App' app.",
            str(cm.exception),
        )

    @mock.patch("tethys_apps.models.TethysApp")
    def test_set_custom_setting(self, mock_app):
        setting_name = "fake_setting"
        mock_save = mock.MagicMock()
        mock_app.objects.get().custom_settings.get.side_effect = [
            mock.MagicMock(type_custom_setting="SIMPLE", type="STRING", save=mock_save),
            mock.MagicMock(
                type_custom_setting="SIMPLE", type="INTEGER", save=mock_save
            ),
            mock.MagicMock(type_custom_setting="SIMPLE", type="FLOAT", save=mock_save),
            mock.MagicMock(
                type_custom_setting="SIMPLE", type="BOOLEAN", save=mock_save
            ),
            mock.MagicMock(type_custom_setting="SIMPLE", type="UUID", save=mock_save),
            mock.MagicMock(type_custom_setting="SECRET", required=True, save=mock_save),
            mock.MagicMock(type_custom_setting="SECRET", save=mock_save),
            mock.MagicMock(type_custom_setting="JSON", required=True, save=mock_save),
            mock.MagicMock(type_custom_setting="JSON", save=mock_save),
        ]

        test_json_1 = {"name": "John", "age": 30, "city": "New York"}
        test_json_2 = {"key1": 2.5, "key2": 30, "key3": "2"}

        TethysAppChild.set_custom_setting(name=setting_name, value="test")
        TethysAppChild.set_custom_setting(name=setting_name, value=1)
        TethysAppChild.set_custom_setting(name=setting_name, value=1.0)
        TethysAppChild.set_custom_setting(name=setting_name, value=True)
        TethysAppChild.set_custom_setting(name=setting_name, value=uuid.uuid4())
        TethysAppChild.set_custom_setting(
            name=setting_name, value="7QcS5r5D16krm8SnkS3OeBiQjjkCT0C8"
        )
        TethysAppChild.set_custom_setting(
            name=setting_name, value="82F8735AF65A399CA39859E8DBC49"
        )
        TethysAppChild.set_custom_setting(name=setting_name, value=test_json_1)
        TethysAppChild.set_custom_setting(name=setting_name, value=test_json_2)

        self.assertEqual(9, mock_save.call_count)

    @mock.patch("tethys_apps.models.TethysApp")
    def test_set_custom_setting_object_not_exist(self, mock_app):
        setting_name = "fake_setting"
        mock_db_app = mock_app.objects.get
        mock_db_app.return_value = mock.MagicMock()

        mock_app.objects.get().custom_settings.get.side_effect = [ObjectDoesNotExist]

        with self.assertRaises(TethysAppSettingDoesNotExist) as cm:
            TethysAppChild.set_custom_setting(name=setting_name, value=True)

        self.assertEqual(
            'A CustomTethysAppSetting named "fake_setting" does not '
            "exist in the b'Test App' app.",
            str(cm.exception),
        )

    @mock.patch("tethys_apps.models.TethysApp")
    def test_set_custom_setting_type_not_match(self, mock_app):
        setting_name = "fake_setting"

        mock_app.objects.get().custom_settings.get.side_effect = [
            mock.MagicMock(type="UUID", type_custom_setting="SIMPLE"),
            mock.MagicMock(type_custom_setting="JSON"),
            mock.MagicMock(type_custom_setting="SECRET"),
        ]

        with self.assertRaises(ValidationError) as ret:
            self.app.set_custom_setting(name=setting_name, value=1)

        self.assertEqual("Value must be of type UUID.", ret.exception.message)

        with self.assertRaises(ValidationError) as ret:
            self.app.set_custom_setting(name=setting_name, value=1)

        self.assertEqual("Value must be a valid JSON string.", ret.exception.message)

        with self.assertRaises(ValidationError) as ret:
            self.app.set_custom_setting(name=setting_name, value=2)

        self.assertEqual(
            "Validation Error: Secret Custom Setting should be a String",
            ret.exception.message,
        )

    @mock.patch("tethys_apps.models.TethysApp")
    def test_get_dataset_service(self, mock_ta):
        TethysAppChild.get_dataset_service(name=self.fake_name)
        mock_ta.objects.get.assert_called_with(package=TethysAppChild.package)
        mock_ta.objects.get().dataset_services_settings.get.assert_called_with(
            name=self.fake_name
        )
        mock_ta.objects.get().dataset_services_settings.get().get_value.assert_called_with(
            as_endpoint=False, as_engine=False, as_public_endpoint=False
        )

    @mock.patch("tethys_apps.models.TethysApp")
    def test_get_dataset_service_object_not_exist(self, mock_ta):
        mock_dss = mock_ta.objects.get().dataset_services_settings.get
        mock_dss.side_effect = ObjectDoesNotExist

        with self.assertRaises(TethysAppSettingDoesNotExist) as cm:
            TethysAppChild.get_dataset_service(name=self.fake_name)

        self.assertEqual(
            'A DatasetServiceSetting named "fake_name" does not '
            "exist in the b'Test App' app.",
            str(cm.exception),
        )

    @mock.patch("tethys_apps.models.TethysApp")
    def test_get_spatial_dataset_service(self, mock_ta):
        TethysAppChild.get_spatial_dataset_service(name=self.fake_name)
        mock_ta.objects.get.assert_called_with(package=TethysAppChild.package)
        mock_ta.objects.get().spatial_dataset_service_settings.get.assert_called_with(
            name=self.fake_name
        )
        mock_ta.objects.get().spatial_dataset_service_settings.get().get_value.assert_called_with(
            as_endpoint=False,
            as_engine=False,
            as_public_endpoint=False,
            as_wfs=False,
            as_wms=False,
        )

    @mock.patch("tethys_apps.models.TethysApp")
    def test_get_spatial_dataset_service_object_not_exist(self, mock_ta):
        mock_sdss = mock_ta.objects.get().spatial_dataset_service_settings.get
        mock_sdss.side_effect = ObjectDoesNotExist

        with self.assertRaises(TethysAppSettingDoesNotExist) as cm:
            TethysAppChild.get_spatial_dataset_service(name=self.fake_name)

        self.assertEqual(
            'A SpatialDatasetServiceSetting named "fake_name" does not '
            "exist in the b'Test App' app.",
            str(cm.exception),
        )

    @mock.patch("tethys_apps.models.TethysApp")
    def test_get_web_processing_service(self, mock_ta):
        TethysAppChild.get_web_processing_service(name=self.fake_name)
        mock_ta.objects.get.assert_called_with(package=TethysAppChild.package)
        mock_ta.objects.get().wps_services_settings.objects.get.assert_called_with(
            name=self.fake_name
        )
        mock_ta.objects.get().wps_services_settings.objects.get().get_value.assert_called_with(
            as_public_endpoint=False, as_endpoint=False, as_engine=False
        )

    @mock.patch("tethys_apps.models.TethysApp")
    def test_get_web_processing_service_object_not_exist(self, mock_ta):
        mock_wss = mock_ta.objects.get().wps_services_settings.objects.get
        mock_wss.side_effect = ObjectDoesNotExist

        with self.assertRaises(TethysAppSettingDoesNotExist) as cm:
            TethysAppChild.get_web_processing_service(name=self.fake_name)

        self.assertEqual(
            'A WebProcessingServiceSetting named "fake_name" does not '
            "exist in the b'Test App' app.",
            str(cm.exception),
        )

    @mock.patch("tethys_apps.models.TethysApp")
    def test_get_scheduler(self, mock_ta):
        TethysAppChild.get_scheduler(name=self.fake_name)
        mock_ta.objects.get.assert_called_with(package=TethysAppChild.package)
        mock_ta.objects.get().scheduler_settings.get.assert_called_with(
            name=self.fake_name
        )
        mock_ta.objects.get().scheduler_settings.get().get_value.assert_called()

    @mock.patch("tethys_apps.models.TethysApp")
    def test_get_scheduler_object_not_exist(self, mock_ta):
        mock_ss = mock_ta.objects.get().scheduler_settings.get
        mock_ss.side_effect = ObjectDoesNotExist

        with self.assertRaises(TethysAppSettingDoesNotExist) as cm:
            TethysAppChild.get_scheduler(name=self.fake_name)

        self.assertEqual(
            'A SchedulerSetting named "fake_name" does not '
            "exist in the b'Test App' app.",
            str(cm.exception),
        )

    @mock.patch("tethys_apps.models.TethysApp")
    def test_get_persistent_store_connection(self, mock_ta):
        TethysAppChild.get_persistent_store_connection(name=self.fake_name)
        mock_ta.objects.get.assert_called_with(package=TethysAppChild.package)
        mock_ta.objects.get().persistent_store_connection_settings.get.assert_called_with(
            name=self.fake_name
        )
        mock_ta.objects.get().persistent_store_connection_settings.get().get_value.assert_called_with(
            as_engine=True, as_sessionmaker=False, as_url=False
        )

    @mock.patch("tethys_apps.models.TethysApp")
    def test_get_persistent_store_connection_object_not_exist(self, mock_ta):
        mock_sdss = mock_ta.objects.get().persistent_store_connection_settings.get
        mock_sdss.side_effect = ObjectDoesNotExist

        with self.assertRaises(TethysAppSettingDoesNotExist) as cm:
            TethysAppChild.get_persistent_store_connection(name=self.fake_name)

        self.assertEqual(
            'A PersistentStoreConnectionSetting named "fake_name" does not '
            "exist in the b'Test App' app.",
            str(cm.exception),
        )

    @mock.patch("tethys_apps.base.app_base.tethys_log")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_get_persistent_store_connection_not_assign(self, mock_ta, mock_log):
        mock_sdss = mock_ta.objects.get().persistent_store_connection_settings.get
        mock_sdss.side_effect = TethysAppSettingNotAssigned

        # Execute
        TethysAppChild.get_persistent_store_connection(name=self.fake_name)

        # Check log
        rts_call_args = mock_log.warning.call_args
        self.assertIn("Tethys app setting is not assigned.", rts_call_args.args[0])
        check_string = (
            'PersistentStoreConnectionSetting named "{}" has not been assigned'.format(
                self.fake_name
            )
        )
        self.assertIn(check_string, rts_call_args.args[0])

    @mock.patch("tethys_apps.base.app_base.is_testing_environment")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_get_persistent_store_database(self, mock_ta, mock_ite):
        mock_ite.return_value = False
        TethysAppChild.get_persistent_store_database(name=self.fake_name)
        mock_ta.objects.get.assert_called_with(package=TethysAppChild.package)

        # Check ps_database_settings.get(name=verified_name) is called
        mock_ta.objects.get().persistent_store_database_settings.get.assert_called_with(
            name=self.fake_name
        )
        mock_ta.objects.get().persistent_store_database_settings.get().get_value.assert_called_with(
            as_engine=True, as_sessionmaker=False, as_url=False, with_db=True
        )

    @mock.patch("tethys_apps.base.app_base.is_testing_environment")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_get_persistent_store_database_object_does_not_exist(
        self, mock_ta, mock_ite
    ):
        mock_ite.return_value = False
        mock_ta.objects.get().persistent_store_database_settings.get.side_effect = (
            ObjectDoesNotExist
        )

        # Check Raise
        self.assertRaises(
            TethysAppSettingDoesNotExist,
            TethysAppChild.get_persistent_store_database,
            name=self.fake_name,
        )

    @mock.patch("tethys_apps.base.app_base.tethys_log")
    @mock.patch("tethys_apps.base.app_base.is_testing_environment")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_get_persistent_store_database_not_assigned(
        self, mock_ta, mock_ite, mock_log
    ):
        mock_ite.return_value = False
        mock_ta.objects.get().persistent_store_database_settings.get.side_effect = (
            TethysAppSettingNotAssigned
        )

        TethysAppChild.get_persistent_store_database(name=self.fake_name)

        # Check log
        rts_call_args = mock_log.warning.call_args
        self.assertIn("Tethys app setting is not assigned.", rts_call_args.args[0])
        check_string = (
            'PersistentStoreDatabaseSetting named "{}" has not been assigned'.format(
                self.fake_name
            )
        )
        self.assertIn(check_string, rts_call_args.args[0])

    @mock.patch("tethys_apps.base.app_base.is_testing_environment")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_create_persistent_store(self, mock_ta, mock_ite):
        mock_ite.return_value = False
        result = TethysAppChild.create_persistent_store(
            db_name="example_db", connection_name="primary"
        )

        # Check ps_connection_settings.get(name=connection_name) is called
        mock_ta.objects.get().persistent_store_connection_settings.get.assert_called_with(
            name="primary"
        )

        # Check db_app.persistent_store_database_settings.get(name=verified_db_name) is called
        mock_ta.objects.get().persistent_store_database_settings.get.assert_called_with(
            name="example_db"
        )

        # Check db_setting.save() is called
        mock_ta.objects.get().persistent_store_database_settings.get().save.assert_called()

        # Check Create the new database is called
        mock_ta.objects.get().persistent_store_database_settings.get().create_persistent_store_database.assert_called_with(
            force_first_time=False, refresh=False
        )

        # Check result is true
        self.assertTrue(result)

    @mock.patch("tethys_apps.base.app_base.get_test_db_name")
    @mock.patch("tethys_apps.base.app_base.is_testing_environment")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_create_persistent_store_testing_env(self, mock_ta, mock_ite, mock_tdn):
        mock_ite.return_value = True
        mock_tdn.return_value = "verified_db_name"
        TethysAppChild.create_persistent_store(
            db_name="example_db", connection_name=None
        )

        # Check get_test_db_name(db_name) is called
        mock_tdn.assert_called_with("example_db")

        rts_call_args_list = (
            mock_ta.objects.get().persistent_store_database_settings.get.call_args_list
        )
        # Check ps_connection_settings.get(name=connection_name) is called
        self.assertEqual({"name": "example_db"}, rts_call_args_list[0].kwargs)

        # Check db_app.persistent_store_database_settings.get(name=verified_db_name) is called
        self.assertEqual({"name": "verified_db_name"}, rts_call_args_list[1].kwargs)

        # Check db_setting.save() is called
        mock_ta.objects.get().persistent_store_database_settings.get().save.assert_called()

        # Check Create the new database is called
        mock_ta.objects.get().persistent_store_database_settings.get().create_persistent_store_database.assert_called_with(
            force_first_time=False, refresh=False
        )

    @mock.patch("tethys_apps.base.app_base.is_testing_environment")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_create_persistent_store_no_connection_name(self, _, mock_ite):
        mock_ite.return_value = False
        self.assertRaises(
            ValueError,
            TethysAppChild.create_persistent_store,
            db_name="example_db",
            connection_name=None,
        )

    @mock.patch("tethys_apps.base.app_base.is_testing_environment")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_create_persistent_store_no_connection_object_not_exist_testing_env(
        self, mock_ta, mock_ite
    ):
        # Need to test in testing env to test the connection_name is None case
        mock_ite.return_value = True
        mock_ta.objects.get().persistent_store_database_settings.get.side_effect = (
            ObjectDoesNotExist
        )

        self.assertRaises(
            TethysAppSettingDoesNotExist,
            TethysAppChild.create_persistent_store,
            db_name="example_db",
            connection_name=None,
        )

    @mock.patch("tethys_apps.base.app_base.is_testing_environment")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_create_persistent_store_connection_object_not_exist_testing_env(
        self, mock_ta, mock_ite
    ):
        # Need to test in testing env to test the connection_name is None case
        mock_ite.return_value = True
        mock_ta.objects.get().persistent_store_connection_settings.get.side_effect = (
            ObjectDoesNotExist
        )

        self.assertRaises(
            TethysAppSettingDoesNotExist,
            TethysAppChild.create_persistent_store,
            db_name="example_db",
            connection_name="test_con",
        )

    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting")
    @mock.patch("tethys_apps.base.app_base.is_testing_environment")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_create_persistent_store_object_not_exist(
        self, mock_ta, mock_ite, mock_psd
    ):
        # Need to test in testing env to test the connection_name is None case
        mock_ite.return_value = False
        mock_ta.objects.get().persistent_store_database_settings.get.side_effect = (
            ObjectDoesNotExist
        )

        # Execute
        TethysAppChild.create_persistent_store(
            db_name="example_db", connection_name="test_con"
        )

        # Check if PersistentStoreDatabaseSetting is called
        mock_psd.assert_called_with(
            description="",
            dynamic=True,
            initializer="",
            name="example_db",
            required=False,
            spatial=False,
        )

        # Check if db_setting is called
        db_setting = mock_psd()
        mock_ta.objects.get().add_settings.assert_called_with((db_setting,))

        # Check if save is called
        mock_ta.objects.get().save.assert_called()

    @mock.patch("tethys_apps.base.app_base.is_testing_environment")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_drop_persistent_store(self, mock_ta, mock_ite):
        mock_ite.return_value = False
        result = TethysAppChild.drop_persistent_store(name="example_store")

        # Check if TethysApp.objects.get(package=cls.package) is called
        mock_ta.objects.get.assert_called_with(package="test_app")

        # Check if ps_database_settings.get(name=verified_name) is called
        mock_ta.objects.get().persistent_store_database_settings.get.assert_called_with(
            name="example_store"
        )

        # Check if drop the persistent store is called
        mock_ta.objects.get().persistent_store_database_settings.get().drop_persistent_store_database.assert_called()

        # Check if remove the database setting is called
        mock_ta.objects.get().persistent_store_database_settings.get().delete.assert_called()

        # Check result return True
        self.assertTrue(result)

    @mock.patch("tethys_apps.base.app_base.is_testing_environment")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_drop_persistent_store_object_does_not_exist(self, mock_ta, mock_ite):
        mock_ite.return_value = False
        mock_ta.objects.get().persistent_store_database_settings.get.side_effect = (
            ObjectDoesNotExist
        )
        result = TethysAppChild.drop_persistent_store(name="example_store")

        # Check result return True
        self.assertTrue(result)

    @mock.patch("tethys_apps.models.TethysApp")
    def test_list_persistent_store_databases_dynamic(self, mock_ta):
        mock_settings = mock_ta.objects.get().persistent_store_database_settings.filter
        setting1 = mock.MagicMock()
        setting1.name = "test1"
        setting2 = mock.MagicMock()
        setting2.name = "test2"
        mock_settings.return_value = [setting1, setting2]

        result = TethysAppChild.list_persistent_store_databases(dynamic_only=True)

        # Check TethysApp.objects.get is called
        mock_ta.objects.get.assert_called_with(package=TethysAppChild.package)

        # Check filter is called
        mock_ta.objects.get().persistent_store_database_settings.filter.assert_called_with(
            persistentstoredatabasesetting__dynamic=True
        )

        # Check result
        self.assertEqual(["test1", "test2"], result)

    @mock.patch("tethys_apps.models.TethysApp")
    def test_list_persistent_store_databases_static(self, mock_ta):
        mock_settings = mock_ta.objects.get().persistent_store_database_settings.filter
        setting1 = mock.MagicMock()
        setting1.name = "test1"
        setting2 = mock.MagicMock()
        setting2.name = "test2"
        mock_settings.return_value = [setting1, setting2]

        result = TethysAppChild.list_persistent_store_databases(static_only=True)

        # Check TethysApp.objects.get is called
        mock_ta.objects.get.assert_called_with(package=TethysAppChild.package)

        # Check filter is called
        mock_ta.objects.get().persistent_store_database_settings.filter.assert_called_with(
            persistentstoredatabasesetting__dynamic=False
        )

        # Check result
        self.assertEqual(["test1", "test2"], result)

    @mock.patch("tethys_apps.models.TethysApp")
    def test_list_persistent_store_connections(self, mock_ta):
        setting1 = mock.MagicMock()
        setting1.name = "test1"
        setting2 = mock.MagicMock()
        setting2.name = "test2"
        mock_ta.objects.get().persistent_store_connection_settings = [
            setting1,
            setting2,
        ]

        result = TethysAppChild.list_persistent_store_connections()

        # Check TethysApp.objects.get is called
        mock_ta.objects.get.assert_called_with(package=TethysAppChild.package)

        # Check result
        self.assertEqual(["test1", "test2"], result)

    @mock.patch("tethys_apps.base.app_base.is_testing_environment")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_persistent_store_exists(self, mock_ta, mock_ite):
        mock_ite.return_value = False
        result = TethysAppChild.persistent_store_exists(name="test_store")

        # Check TethysApp.objects.get is called
        mock_ta.objects.get.assert_called_with(package=TethysAppChild.package)

        # Check if ps_database_settings.get is called
        mock_ta.objects.get().persistent_store_database_settings.get.assert_called_with(
            name="test_store"
        )

        # Check if database exists is called
        mock_ta.objects.get().persistent_store_database_settings.get().persistent_store_database_exists.assert_called()

        # Check if result True
        self.assertTrue(result)

    @mock.patch("tethys_apps.base.app_base.is_testing_environment")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_persistent_store_exists_object_does_not_exist(self, mock_ta, mock_ite):
        mock_ite.return_value = False
        mock_ta.objects.get().persistent_store_database_settings.get.side_effect = (
            ObjectDoesNotExist
        )
        result = TethysAppChild.persistent_store_exists(name="test_store")

        # Check TethysApp.objects.get is called
        mock_ta.objects.get.assert_called_with(package=TethysAppChild.package)

        # Check if ps_database_settings.get is called
        mock_ta.objects.get().persistent_store_database_settings.get.assert_called_with(
            name="test_store"
        )

        # Check if result False
        self.assertFalse(result)

    @mock.patch("tethys_apps.base.app_base.files")
    @mock.patch("tethys_apps.base.app_base.TethysPath")
    @mock.patch("tethys_apps.base.app_base.sync_cookies_from_yaml")
    @mock.patch("tethys_apps.base.app_base.has_module", return_value=True)
    @mock.patch("django.conf.settings")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_sync_with_tethys_db(
        self, mock_ta, _, __, mock_sync_cookies, mock_path, ____
    ):
        mock_ta.objects.filter().all.return_value = []
        self.app.name = "n"
        self.app.package = "p"
        self.app.description = "d"
        self.app.enable_feedback = "e"
        self.app.feedback_emails = "f"
        self.app.index = "in"
        self.app.icon = "ic"
        self.app.root_url = "r"
        self.app.color = "c"
        self.app.tags = "t"
        self.app.show_in_apps_library = False
        self.app.enabled = False

        self.app.sync_with_tethys_db()

        # Check if TethysApp.objects.filter is called
        mock_ta.objects.filter().all.assert_called()

        # Check if TethysApp is called
        mock_ta.assert_called_with(
            color="c",
            description="d",
            enable_feedback="e",
            feedback_emails="f",
            icon="ic",
            index="in",
            name="n",
            package="p",
            root_url="r",
            tags="t",
            enabled=False,
            show_in_apps_library=False,
        )

        # Check if save is called 2 times
        self.assertTrue(mock_ta().save.call_count == 2)

        # Check if add_settings is called 6 times
        self.assertTrue(mock_ta().sync_settings.call_count == 6)
        mock_sync_cookies.assert_called_once_with(
            mock_path().path.__truediv__(), "p", "n"
        )

    @mock.patch("django.conf.settings")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_sync_with_tethys_db_in_db(self, mock_ta, mock_ds):
        mock_ds.DEBUG = True
        mock_app = mock.MagicMock()
        mock_ta.objects.filter().all.return_value = [mock_app]
        self.app.sync_with_tethys_db()

        # Check if TethysApp.objects.filter is called
        mock_ta.objects.filter().all.assert_called()

        # Check if save is called 2 times
        self.assertTrue(mock_app.save.call_count == 2)

        # Check if add_settings is called 6 times
        self.assertTrue(mock_app.sync_settings.call_count == 6)

    @mock.patch("django.conf.settings")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_sync_with_tethys_db_more_than_one(self, mock_ta, mock_ds):
        mock_ds.DEBUG = True
        mock_app = mock.MagicMock()
        mock_ta.objects.filter().all.return_value = [mock_app, mock_app]
        self.app.sync_with_tethys_db()

        # Check if TethysApp.objects.filter is called
        mock_ta.objects.filter().all.assert_called()

        # Check if is not called
        mock_app.save.assert_not_called()

        # Check if is not called
        mock_app.add_settings.assert_not_called()

    @mock.patch("tethys_apps.base.app_base.tethys_log")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_sync_with_tethys_db_exception(self, mock_ta, mock_log):
        mock_ta.objects.filter().all.side_effect = Exception
        self.app.sync_with_tethys_db()

        mock_log.error.assert_called()

    @mock.patch("tethys_apps.base.app_base.tethys_log")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_sync_with_tethys_db_programming_error(self, mock_ta, mock_log):
        mock_ta.objects.filter().all.side_effect = ProgrammingError
        self.app.sync_with_tethys_db()

        mock_log.warning.assert_called_with(
            "Unable to sync app with database. "
            "tethys_apps_tethysapp table does not exist"
        )

    @mock.patch("tethys_apps.models.TethysApp")
    def test_remove_from_db(self, mock_ta):
        self.app.remove_from_db()

        # Check if delete is called
        mock_ta.objects.filter().delete.assert_called()

    @override_settings(DEBUG=True)
    @mock.patch("tethys_cli.cli_colors.write_error")
    @mock.patch("tethys_apps.base.app_base.input")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_remove_from_db_prompt_yes(self, mock_ta, mock_input, mock_write_error):
        mock_input.side_effect = "y"
        self.app.remove_from_db()

        # Check if delete is called
        mock_ta.objects.filter().delete.assert_called()
        mock_write_error.assert_called_once()

    @override_settings(DEBUG=True)
    @mock.patch("tethys_cli.cli_colors.write_error")
    @mock.patch("tethys_apps.base.app_base.input")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_remove_from_db_prompt_no(self, mock_ta, mock_input, mock_write_error):
        mock_input.side_effect = "n"
        self.app.remove_from_db()

        # Check if delete is called
        mock_ta.objects.filter().delete.assert_not_called()
        mock_write_error.assert_called_once()

    @mock.patch("tethys_apps.base.app_base.tethys_log")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_remove_from_db_2(self, mock_ta, mock_log):
        mock_ta.objects.filter().delete.side_effect = Exception
        self.app.remove_from_db()

        # Check tethys log error
        mock_log.error.assert_called()
