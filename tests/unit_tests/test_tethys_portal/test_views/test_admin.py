import unittest
from unittest import mock
from tethys_portal.views.admin import clear_workspace
from tethys_apps.models import TethysApp


class TethysPortalTethysAppTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch("tethys_quotas.utilities.log")
    @mock.patch("tethys_portal.views.admin.get_app_class")
    @mock.patch("tethys_portal.views.admin.TethysApp")
    @mock.patch("tethys_portal.views.admin.render")
    def test_clear_workspace_display(
        self, mock_render, mock_app, mock_get_app_class, _
    ):
        mock_request = mock.MagicMock()
        app = TethysApp(name="app_name")
        mock_get_app_class.return_value = app
        mock_app.objects.get.return_value = app
        # reload_urlconf()

        expected_context = {
            "app_name": mock_app.objects.get().name,
            "change_url": "/admin/tethys_apps/tethysapp/app_name/change/",
        }

        clear_workspace(mock_request, "app_name")

        mock_render.assert_called_once_with(
            mock_request,
            "tethys_portal/admin/tethys_app/clear_workspace.html",
            expected_context,
        )

    @mock.patch("tethys_portal.views.admin._get_app_media")
    @mock.patch("tethys_apps.base.paths._get_app_workspace")
    @mock.patch("tethys_apps.base.paths._resolve_app_class")
    @mock.patch("tethys_portal.views.admin.get_app_class")
    @mock.patch("tethys_portal.views.admin.TethysApp")
    @mock.patch("tethys_portal.views.admin.messages.success")
    @mock.patch("tethys_portal.views.admin.redirect")
    def test_clear_workspace_successful(
        self,
        mock_redirect,
        mock_message,
        mock_app,
        mock_get_app_class,
        mock_resolve_app_class,
        _,
        __,
    ):
        mock_request = mock.MagicMock(method="POST", POST="clear-workspace-submit")
        app_class = mock.MagicMock()
        app_class.name = "app_name"
        app = TethysApp(name="app_name", package="myapp")

        mock_get_app_class.return_value = app_class
        mock_resolve_app_class.return_value = app
        mock_app.objects.get.return_value = app

        clear_workspace(mock_request, "myapp")

        mock_message.assert_called_once_with(
            mock_request,
            "The workspace and media directory for the app_name app have been successfully cleared.",
        )
        mock_redirect.assert_called_once_with(
            "/admin/tethys_apps/tethysapp/myapp/change/"
        )
