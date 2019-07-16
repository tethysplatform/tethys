import unittest
from unittest import mock

from tethys_portal.views.developer import is_staff, home


class TethysPortalDeveloperTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_is_staff(self):
        mock_user = mock.MagicMock()
        mock_user.is_staff = 'foo'
        self.assertEqual('foo', is_staff(mock_user))

    @mock.patch('tethys_portal.views.developer.render')
    def test_home(self, mock_render):
        mock_request = mock.MagicMock()
        context = {}
        mock_render.return_value = 'foo'
        self.assertEqual('foo', home(mock_request))
        mock_render.assert_called_once_with(mock_request, 'tethys_portal/developer/home.html', context)
