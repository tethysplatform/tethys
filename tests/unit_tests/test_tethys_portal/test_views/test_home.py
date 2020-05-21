import unittest
from unittest import mock

from tethys_portal.views.home import home


class TethysPortalHomeTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('tethys_portal.views.home.hasattr')
    @mock.patch('tethys_portal.views.home.render')
    @mock.patch('tethys_portal.views.home.redirect')
    @mock.patch('tethys_portal.views.home.settings')
    def test_home(self, mock_settings, mock_redirect, mock_render, mock_hasattr):
        mock_request = mock.MagicMock()
        mock_hasattr.return_value = True
        mock_settings.BYPASS_TETHYS_HOME_PAGE = True
        mock_redirect.return_value = 'foo'
        mock_render.return_value = 'bar'
        self.assertEqual('foo', home(mock_request))
        mock_render.assert_not_called()
        mock_redirect.assert_called_once_with('app_library')

    @mock.patch('tethys_portal.views.home.hasattr')
    @mock.patch('tethys_portal.views.home.render')
    @mock.patch('tethys_portal.views.home.redirect')
    @mock.patch('tethys_portal.views.home.settings')
    def test_home_with_no_attribute(self, mock_settings, mock_redirect, mock_render, mock_hasattr):
        mock_request = mock.MagicMock()
        mock_hasattr.return_value = False
        mock_settings.ENABLE_OPEN_SIGNUP = True
        mock_settings.ENABLE_OPEN_PORTAL = True
        mock_redirect.return_value = 'foo'
        mock_render.return_value = 'bar'
        self.assertEqual('bar', home(mock_request))
        mock_redirect.assert_not_called()
        mock_render.assert_called_once_with(mock_request, 'tethys_portal/home.html',
                                            {"ENABLE_OPEN_SIGNUP": mock_settings.ENABLE_OPEN_SIGNUP,
                                             "ENABLE_OPEN_PORTAL": mock_settings.ENABLE_OPEN_PORTAL})

    @mock.patch('tethys_portal.views.home.Setting.objects.get')
    @mock.patch('tethys_portal.views.home.hasattr')
    @mock.patch('tethys_portal.views.home.render')
    @mock.patch('tethys_portal.views.home.settings')
    def test_home_with_custom_template(self, mock_settings, mock_render, mock_hasattr, mock_custom_template):
        mock_request = mock.MagicMock()
        mock_hasattr.return_value = False
        mock_settings.ENABLE_OPEN_SIGNUP = True
        mock_settings.ENABLE_OPEN_PORTAL = True
        mock_custom_template.return_value = mock.MagicMock(content='custom_templates/test.html')

        home(mock_request)
        mock_render.assert_called_once_with(mock_request, 'custom_templates/test.html',
                                            {"ENABLE_OPEN_SIGNUP": mock_settings.ENABLE_OPEN_SIGNUP,
                                             "ENABLE_OPEN_PORTAL": mock_settings.ENABLE_OPEN_PORTAL})
