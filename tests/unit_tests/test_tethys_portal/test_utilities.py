import unittest
from unittest import mock

from tethys_portal import utilities


class TethysPortalUtilitiesTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_utilities_no_user_or_username(self):
        mock_request = mock.MagicMock()
        mock_request.method = 'POST'
        mock_request.POST = 'login-submit'
        mock_request.user.is_anonymous = True
        mock_request.user.username = 'sam'
        mock_request.GET = ''

        with self.assertRaises(ValueError) as context:
            utilities.log_user_in(mock_request)

        self.assertTrue('You must provide either the "user" or the "username" arguments.' in str(context.exception))

    @mock.patch('tethys_portal.utilities.redirect')
    def test_utilities_no_user_username_does_not_exist(self, mock_redirect):
        mock_request = mock.MagicMock()
        mock_request.method = 'POST'
        mock_request.POST = 'login-submit'
        mock_request.user.is_anonymous = True
        mock_request.user.username = 'sam'
        mock_request.GET = ''

        utilities.log_user_in(mock_request, username='sam')

        # mock redirect after logged in using next parameter or default to user profile
        mock_redirect.assert_called_once_with('accounts:login')

    @mock.patch('tethys_portal.utilities.login')
    @mock.patch('tethys_portal.utilities.redirect')
    def test_utilities_no_user_exist(self, mock_redirect, mock_authenticate):
        mock_request = mock.MagicMock()
        mock_request.method = 'POST'
        mock_request.POST = 'login-submit'
        mock_request.user.is_anonymous = True
        mock_request.user.username = 'sam'
        mock_request.GET = ''

        # mock authenticate
        mock_user = mock.MagicMock()
        mock_authenticate.return_value = mock_user

        # mock the password has been verified for the user
        mock_user.is_active = True

        utilities.log_user_in(mock_request, user=mock_user)

        # mock redirect after logged in using next parameter or default to user profile
        mock_redirect.assert_called_once_with('app_library')

    @mock.patch('tethys_portal.utilities.login')
    @mock.patch('tethys_portal.utilities.redirect')
    def test_utilities_no_user_exist_next(self, mock_redirect, mock_authenticate):
        mock_request = mock.MagicMock()
        mock_request.method = 'POST'
        mock_request.POST = 'login-submit'
        mock_request.user.is_anonymous = True
        mock_request.user.username = 'sam'
        mock_request.GET = {'next': 'foo'}

        # mock authenticate
        mock_user = mock.MagicMock()
        mock_authenticate.return_value = mock_user

        # mock the password has been verified for the user
        mock_user.is_active = True

        utilities.log_user_in(mock_request, user=mock_user)

        # mock redirect after logged in using next parameter or default to user profile
        mock_redirect.assert_called_once_with('foo')
