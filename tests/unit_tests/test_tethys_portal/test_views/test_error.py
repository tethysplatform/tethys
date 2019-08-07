import unittest
from unittest import mock
from tethys_portal.views.error import handler_400, handler_403, handler_404, handler_500


class TethysPortalViewsErrorTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('tethys_portal.views.error.render')
    def test_handler_400(self, mock_render):
        mock_request = mock.MagicMock()
        mock_exception = mock.MagicMock()
        mock_render.return_value = '400'
        context = {'error_code': '400',
                   'error_title': 'Bad Request',
                   'error_message': "Sorry, but we can't process your request. Try something different.",
                   'error_image': '/static/tethys_portal/images/error_500.png'}

        self.assertEqual('400', handler_400(mock_request, mock_exception))
        mock_render.assert_called_once_with(mock_request, 'tethys_portal/error.html', context, status=400)

    @mock.patch('tethys_portal.views.error.render')
    def test_handler_403(self, mock_render):
        mock_request = mock.MagicMock()
        mock_render.return_value = '403'
        context = {'error_code': '403',
                   'error_title': 'Sorry, you are unable to access this page right now.',
                   'error_message': 'error message',
                   'error_image': '/static/tethys_portal/images/data.png'}

        self.assertEqual('403', handler_403(mock_request, exception="error message"))
        mock_render.assert_called_once_with(mock_request, 'tethys_portal/403error.html', context, status=403)

    @mock.patch('tethys_portal.views.error.render')
    def test_handler_404(self, mock_render):
        mock_request = mock.MagicMock()
        mock_exception = mock.MagicMock()
        mock_render.return_value = '404'
        context = {'error_code': '404',
                   'error_title': 'Page Not Found',
                   'error_message': "We are unable to find the page you requested. Please, check the address and "
                                    "try again.",
                   'error_image': '/static/tethys_portal/images/error_404.png'}

        self.assertEqual('404', handler_404(mock_request, mock_exception))
        mock_render.assert_called_once_with(mock_request, 'tethys_portal/error.html', context, status=404)

    @mock.patch('tethys_portal.views.error.render')
    def test_handler_500(self, mock_render):
        mock_request = mock.MagicMock()
        mock_render.return_value = '500'
        context = {'error_code': '500',
                   'error_title': 'Internal Server Error',
                   'error_message': "We're sorry, but we seem to have a problem. "
                                    "Please, come back later and try again.",
                   'error_image': '/static/tethys_portal/images/error_500.png'}

        self.assertEqual('500', handler_500(mock_request))
        mock_render.assert_called_once_with(mock_request, 'tethys_portal/error.html', context, status=500)
