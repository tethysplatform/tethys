import unittest
from unittest import mock
from tethys_portal.views.admin import clear_workspace
from tethys_apps.models import TethysApp


class TethysPortalTethysAppTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('tethys_quotas.helpers.log')
    @mock.patch('tethys_portal.views.admin.SingletonHarvester', apps=[TethysApp(name='app_name')])
    @mock.patch('tethys_portal.views.admin.TethysApp')
    @mock.patch('tethys_portal.views.admin.render')
    def test_clear_workspace_display(self, mock_render, mock_app, _, __):
        mock_request = mock.MagicMock()
        app = mock.MagicMock(TethysApp(name='app_name'))
        mock_app.objects.get.return_value = app

        expected_context = {'app_name': mock_app.objects.get().name,
                            'change_url': '/admin/tethys_apps/tethysapp/myapp/change/'}

        clear_workspace(mock_request, 'myapp')

        mock_render.assert_called_once_with(mock_request, 'tethys_portal/admin/tethys_app/clear_workspace.html',
                                            expected_context)

    @mock.patch('tethys_portal.views.admin.SingletonHarvester', apps=[TethysApp(name='app_name')])
    @mock.patch('tethys_portal.views.admin._get_app_workspace')
    @mock.patch('tethys_portal.views.admin.TethysApp')
    @mock.patch('tethys_portal.views.admin.messages.success')
    @mock.patch('tethys_portal.views.admin.redirect')
    def test_clear_workspace_successful(self, mock_redirect, mock_message, mock_app, mock_gaw, _):
        mock_request = mock.MagicMock(method='POST', POST='clear-workspace-submit')

        app = mock.MagicMock(TethysApp(name='app_name'))
        mock_app.objects.get.return_value = app
        app.pre_delete_app_workspace = mock.MagicMock()
        app.post_delete_app_workspace = mock.MagicMock()
        mock_gaw.return_value = mock.MagicMock()

        clear_workspace(mock_request, 'myapp')

        mock_message.assert_called_once_with(mock_request, 'Your workspace has been successfully cleared.')
        mock_redirect.assert_called_once_with('/admin/tethys_apps/tethysapp/myapp/change/')
