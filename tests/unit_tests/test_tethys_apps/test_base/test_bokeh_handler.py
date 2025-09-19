from pathlib import Path
import unittest
from unittest import mock

import bokeh.application.application as baa
from bokeh.document import Document

from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import override_settings
from tethys_apps.base.bokeh_handler import (
    with_request,
    with_workspaces,
    with_paths,
    _get_bokeh_controller,
)
from tethys_apps.base.paths import TethysPath


class TestBokehHandler(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.app = baa.Application()
        self.doc = self.app.create_document()
        self.doc._session_context = self.make_session_context(self.doc)

    def make_session_context(self, doc):
        mock_session_context = mock.MagicMock(
            return_value=mock.MagicMock(
                _document=doc,
                status=None,
                counter=0,
                request=dict(user=mock.MagicMock(spec=User), scheme="http"),
            )
        )
        return mock_session_context

    def test_with_request_decorator(self):
        @with_request
        def with_request_decorated(doc: Document):
            return doc

        ret_doc = with_request_decorated(self.doc)

        self.assertIsNotNone(getattr(ret_doc, "request", None))
        self.assertIsNotNone(getattr(ret_doc.request, "user", None))
        self.assertIsInstance(ret_doc.request, HttpRequest)

    async def test_with_request_decorator_async(self):
        @with_request
        async def with_request_decorated(doc: Document):
            return doc

        ret_doc = await with_request_decorated(self.doc)

        self.assertIsNotNone(getattr(ret_doc, "request", None))
        self.assertIsNotNone(getattr(ret_doc.request, "user", None))
        self.assertIsInstance(ret_doc.request, HttpRequest)

    @mock.patch("tethys_apps.base.bokeh_handler.deprecation_warning")
    @mock.patch("tethys_quotas.utilities.log")
    @mock.patch("tethys_apps.base.workspace.log")
    @mock.patch("tethys_apps.utilities.get_active_app")
    @mock.patch("tethys_apps.base.bokeh_handler._get_user_workspace_old")
    @mock.patch("tethys_apps.base.bokeh_handler._get_app_workspace_old")
    def test_with_workspaces_decorator(self, mock_gaw, mock_guw, _, __, ___, ____):
        mock_guw.return_value = "user-workspace"
        mock_gaw.return_value = "app-workspace"

        @with_workspaces
        def with_workspaces_decorated(doc: Document):
            return doc

        ret_doc = with_workspaces_decorated(self.doc)
        self.assertIsNotNone(getattr(ret_doc, "user_workspace", None))
        self.assertIsNotNone(getattr(ret_doc, "app_workspace", None))
        self.assertEqual("user-workspace", ret_doc.user_workspace)
        self.assertEqual("app-workspace", ret_doc.app_workspace)

    @mock.patch("tethys_apps.base.paths._check_app_quota")
    @mock.patch("tethys_apps.base.paths._check_user_quota")
    @mock.patch("tethys_apps.base.paths.Path.mkdir")
    @mock.patch("tethys_quotas.utilities.log")
    @mock.patch("tethys_apps.base.workspace.log")
    @mock.patch("tethys_apps.utilities.get_active_app")
    @mock.patch("tethys_apps.base.paths._get_app_workspace_root")
    @mock.patch("tethys_apps.base.paths._get_app_media_root")
    @mock.patch("tethys_apps.base.paths._resolve_app_class")
    @mock.patch("tethys_apps.base.paths._resolve_user")
    @override_settings(USE_OLD_WORKSPACES_API=False)
    def test_with_paths_decorator(
        self, mock_ru, rac, mock_gamr, mock_gaw, _, __, ___, ____, _____, ______
    ):
        mock_gaw.return_value = Path("workspaces")
        mock_gamr.return_value = Path("app-media-root/media")

        mock_app = mock.MagicMock()
        mock_app.package = "mock-app-package"
        mock_app.resources_path = TethysPath("resources")
        mock_app.public_path = TethysPath("public")
        rac.return_value = mock_app

        User = get_user_model()
        user = User(username="test_user")
        mock_ru.return_value = user
        mock_ru.return_value.username = "mock-username"

        @with_paths
        def with_paths_decorated(doc: Document):
            return doc

        ret_doc = with_paths_decorated(self.doc)
        self.assertIsNotNone(getattr(ret_doc, "user_workspace", None))
        self.assertIsNotNone(getattr(ret_doc, "app_workspace", None))
        self.assertIsNotNone(getattr(ret_doc, "app_media_path", None))
        self.assertIsNotNone(getattr(ret_doc, "user_media_path", None))
        self.assertIsNotNone(getattr(ret_doc, "app_resources_path", None))

        self.assertEqual(
            TethysPath("workspaces/user_workspaces/mock-username").path,
            ret_doc.user_workspace.path,
        )
        self.assertEqual(
            TethysPath("workspaces/app_workspace").path, ret_doc.app_workspace.path
        )
        self.assertEqual(
            TethysPath("app-media-root/media/app").path,
            ret_doc.app_media_path.path,
        )
        self.assertEqual(
            TethysPath("app-media-root/media/user/mock-username").path,
            ret_doc.user_media_path.path,
        )
        self.assertEqual(TethysPath("resources").path, ret_doc.app_resources_path.path)
        self.assertEqual(TethysPath("public").path, ret_doc.app_public_path.path)

    @mock.patch("tethys_apps.base.paths._check_app_quota")
    @mock.patch("tethys_apps.base.paths._check_user_quota")
    @mock.patch("tethys_apps.base.paths.Path.mkdir")
    @mock.patch("tethys_quotas.utilities.log")
    @mock.patch("tethys_apps.base.workspace.log")
    @mock.patch("tethys_apps.utilities.get_active_app")
    @mock.patch("tethys_apps.base.paths._get_app_workspace_root")
    @mock.patch("tethys_apps.base.paths._get_app_media_root")
    @mock.patch("tethys_apps.base.paths._resolve_app_class")
    @mock.patch("tethys_apps.base.paths._resolve_user")
    @override_settings(USE_OLD_WORKSPACES_API=False)
    async def test_with_paths_decorator_async(
        self, mock_ru, rac, mock_gamr, mock_gaw, _, __, ___, ____, _____, ______
    ):
        mock_gaw.return_value = Path("workspaces")
        mock_gamr.return_value = Path("app-media-root/media")

        mock_app = mock.MagicMock()
        mock_app.package = "mock-app-package"
        mock_app.resources_path = TethysPath("resources")
        mock_app.public_path = TethysPath("public")
        rac.return_value = mock_app

        User = get_user_model()
        user = User(username="test_user")
        mock_ru.return_value = user
        mock_ru.return_value.username = "mock-username"

        @with_paths
        async def with_paths_decorated(doc: Document):
            return doc

        ret_doc = await with_paths_decorated(self.doc)
        self.assertIsNotNone(getattr(ret_doc, "user_workspace", None))
        self.assertIsNotNone(getattr(ret_doc, "app_workspace", None))
        self.assertIsNotNone(getattr(ret_doc, "app_media_path", None))
        self.assertIsNotNone(getattr(ret_doc, "user_media_path", None))
        self.assertIsNotNone(getattr(ret_doc, "app_resources_path", None))

        self.assertEqual(
            TethysPath("workspaces/user_workspaces/mock-username").path,
            ret_doc.user_workspace.path,
        )
        self.assertEqual(
            TethysPath("workspaces/app_workspace").path, ret_doc.app_workspace.path
        )
        self.assertEqual(
            TethysPath("app-media-root/media/app").path,
            ret_doc.app_media_path.path,
        )
        self.assertEqual(
            TethysPath("app-media-root/media/user/mock-username").path,
            ret_doc.user_media_path.path,
        )
        self.assertEqual(TethysPath("resources").path, ret_doc.app_resources_path.path)
        self.assertEqual(TethysPath("public").path, ret_doc.app_public_path.path)

    @mock.patch("tethys_apps.base.bokeh_handler.render")
    @mock.patch("tethys_apps.base.bokeh_handler.server_document")
    def test_get_bokeh_controller(self, mock_server_doc, mock_render):
        controller = _get_bokeh_controller()
        mock_request = mock.MagicMock()
        controller(mock_request)
        mock_server_doc.assert_called_once()
        args = mock_render.call_args_list[0][0]
        template = args[1]
        self.assertEqual(template, "tethys_apps/bokeh_default.html")

    @mock.patch("tethys_apps.base.bokeh_handler.render")
    @mock.patch("tethys_apps.base.bokeh_handler.server_document")
    def test_get_bokeh_controller_template(self, mock_server_doc, mock_render):
        controller = _get_bokeh_controller(template="template")
        mock_request = mock.MagicMock()
        controller(mock_request)
        mock_server_doc.assert_called_once()
        args = mock_render.call_args_list[0][0]
        template = args[1]
        self.assertEqual(template, "template")

    @mock.patch("tethys_apps.base.bokeh_handler.render")
    @mock.patch("tethys_apps.base.bokeh_handler.server_document")
    def test_get_bokeh_controller_app_package(self, mock_server_doc, mock_render):
        controller = _get_bokeh_controller(app_package="app_package")
        mock_request = mock.MagicMock()
        controller(mock_request)
        mock_server_doc.assert_called_once()
        args = mock_render.call_args_list[0][0]
        template = args[1]
        self.assertEqual(template, "tethys_apps/bokeh_base.html")
        context = args[2]
        self.assertEqual(context["extends_template"], "app_package/base.html")
