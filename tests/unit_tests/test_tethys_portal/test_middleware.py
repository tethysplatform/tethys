import unittest
import mock

from tethys_portal.middleware import TethysSocialAuthExceptionMiddleware


class TethysPortalMiddlewareTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('tethys_portal.middleware.isinstance')
    @mock.patch('tethys_portal.middleware.hasattr')
    @mock.patch('tethys_portal.middleware.redirect')
    def test_process_exception_anonymous_user(self, mock_redirect, mock_hasattr, mock_isinstance):
        mock_request = mock.MagicMock()
        mock_exception = mock.MagicMock()
        mock_hasattr.return_value = True
        mock_isinstance.return_value = True
        mock_request.user.is_anonymous = True

        obj = TethysSocialAuthExceptionMiddleware()
        obj.process_exception(mock_request, mock_exception)

        mock_redirect.assert_called_once_with('accounts:login')

    @mock.patch('tethys_portal.middleware.isinstance')
    @mock.patch('tethys_portal.middleware.hasattr')
    @mock.patch('tethys_portal.middleware.redirect')
    def test_process_exception_user(self, mock_redirect, mock_hasattr, mock_isinstance):
        mock_request = mock.MagicMock()
        mock_exception = mock.MagicMock()
        mock_hasattr.return_value = True
        mock_isinstance.return_value = True
        mock_request.user.is_anonymous = False
        mock_request.user.username = 'foo'

        obj = TethysSocialAuthExceptionMiddleware()
        obj.process_exception(mock_request, mock_exception)

        mock_redirect.assert_called_once_with('user:settings', username='foo')

    @mock.patch('tethys_portal.middleware.pretty_output')
    @mock.patch('tethys_portal.middleware.messages.success')
    @mock.patch('tethys_portal.middleware.isinstance')
    @mock.patch('tethys_portal.middleware.hasattr')
    @mock.patch('tethys_portal.middleware.redirect')
    def test_process_exception_isinstance_google(self, mock_redirect, mock_hasattr, mock_isinstance, mock_success,
                                                 mock_pretty_output):
        mock_request = mock.MagicMock()
        mock_request.user.is_anonymous = True

        mock_exception = mock.MagicMock()
        mock_exception.backend.name = 'google'

        mock_hasattr.return_value = True
        mock_isinstance.side_effect = False, True

        obj = TethysSocialAuthExceptionMiddleware()

        obj.process_exception(mock_request, mock_exception)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('google', po_call_args[0][0][0])

        call_args = mock_success.call_args_list

        self.assertEquals(mock_request, call_args[0][0][0])

        self.assertEquals('The Google account you tried to connect to has already been associated with another '
                          'account.', call_args[0][0][1])

        mock_redirect.assert_called_once_with('accounts:login')

    @mock.patch('tethys_portal.middleware.pretty_output')
    @mock.patch('tethys_portal.middleware.messages.success')
    @mock.patch('tethys_portal.middleware.isinstance')
    @mock.patch('tethys_portal.middleware.hasattr')
    @mock.patch('tethys_portal.middleware.redirect')
    def test_process_exception_isinstance_linkedin(self, mock_redirect, mock_hasattr, mock_isinstance,
                                                   mock_success, mock_pretty_output):
        mock_request = mock.MagicMock()
        mock_request.user.is_anonymous = True

        mock_exception = mock.MagicMock()
        mock_exception.backend.name = 'linkedin'

        mock_hasattr.return_value = True
        mock_isinstance.side_effect = False, True

        obj = TethysSocialAuthExceptionMiddleware()

        obj.process_exception(mock_request, mock_exception)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('linkedin', po_call_args[0][0][0])

        call_args = mock_success.call_args_list

        self.assertEquals(mock_request, call_args[0][0][0])

        self.assertEquals('The LinkedIn account you tried to connect to has already been associated with another '
                          'account.', call_args[0][0][1])

        mock_redirect.assert_called_once_with('accounts:login')

    @mock.patch('tethys_portal.middleware.pretty_output')
    @mock.patch('tethys_portal.middleware.messages.success')
    @mock.patch('tethys_portal.middleware.isinstance')
    @mock.patch('tethys_portal.middleware.hasattr')
    @mock.patch('tethys_portal.middleware.redirect')
    def test_process_exception_isinstance_hydroshare(self, mock_redirect, mock_hasattr, mock_isinstance,
                                                     mock_success,
                                                     mock_pretty_output):
        mock_request = mock.MagicMock()
        mock_request.user.is_anonymous = True

        mock_exception = mock.MagicMock()
        mock_exception.backend.name = 'hydroshare'

        mock_hasattr.return_value = True
        mock_isinstance.side_effect = False, True

        obj = TethysSocialAuthExceptionMiddleware()

        obj.process_exception(mock_request, mock_exception)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('hydroshare', po_call_args[0][0][0])

        call_args = mock_success.call_args_list

        self.assertEquals(mock_request, call_args[0][0][0])

        self.assertEquals('The HydroShare account you tried to connect to has already been associated with '
                          'another account.', call_args[0][0][1])

        mock_redirect.assert_called_once_with('accounts:login')

    @mock.patch('tethys_portal.middleware.pretty_output')
    @mock.patch('tethys_portal.middleware.messages.success')
    @mock.patch('tethys_portal.middleware.isinstance')
    @mock.patch('tethys_portal.middleware.hasattr')
    @mock.patch('tethys_portal.middleware.redirect')
    def test_process_exception_isinstance_facebook(self, mock_redirect, mock_hasattr, mock_isinstance, mock_success,
                                                   mock_pretty_output):
        mock_request = mock.MagicMock()
        mock_request.user.is_anonymous = True

        mock_exception = mock.MagicMock()
        mock_exception.backend.name = 'facebook'

        mock_hasattr.return_value = True
        mock_isinstance.side_effect = False, True

        obj = TethysSocialAuthExceptionMiddleware()

        obj.process_exception(mock_request, mock_exception)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('facebook', po_call_args[0][0][0])

        call_args = mock_success.call_args_list

        self.assertEquals(mock_request, call_args[0][0][0])

        self.assertEquals('The Facebook account you tried to connect to has already been associated with '
                          'another account.', call_args[0][0][1])

        mock_redirect.assert_called_once_with('accounts:login')

    @mock.patch('tethys_portal.middleware.pretty_output')
    @mock.patch('tethys_portal.middleware.messages.success')
    @mock.patch('tethys_portal.middleware.isinstance')
    @mock.patch('tethys_portal.middleware.hasattr')
    @mock.patch('tethys_portal.middleware.redirect')
    def test_process_exception_isinstance_social(self, mock_redirect, mock_hasattr, mock_isinstance,
                                                 mock_success,
                                                 mock_pretty_output):
        mock_request = mock.MagicMock()
        mock_request.user.is_anonymous = False
        mock_request.user.username = 'foo'

        mock_exception = mock.MagicMock()
        mock_exception.backend.name = 'social'

        mock_hasattr.return_value = True
        mock_isinstance.side_effect = False, True

        obj = TethysSocialAuthExceptionMiddleware()

        obj.process_exception(mock_request, mock_exception)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('social', po_call_args[0][0][0])

        call_args = mock_success.call_args_list

        self.assertEquals(mock_request, call_args[0][0][0])

        self.assertEquals('The social account you tried to connect to has already been associated with '
                          'another account.', call_args[0][0][1])

        mock_redirect.assert_called_once_with('user:settings', username='foo')

    @mock.patch('tethys_portal.middleware.messages.success')
    @mock.patch('tethys_portal.middleware.isinstance')
    @mock.patch('tethys_portal.middleware.hasattr')
    @mock.patch('tethys_portal.middleware.redirect')
    def test_process_exception_isinstance_exception_with_anonymous_user(self, mock_redirect, mock_hasattr,
                                                                        mock_isinstance, mock_success):
        mock_request = mock.MagicMock()
        mock_request.user.is_anonymous = False
        mock_request.user.username = 'foo'

        mock_exception = mock.MagicMock()
        mock_exception.backend.name = 'social'

        mock_hasattr.return_value = True
        mock_isinstance.side_effect = False, False, True

        obj = TethysSocialAuthExceptionMiddleware()

        obj.process_exception(mock_request, mock_exception)

        call_args = mock_success.call_args_list

        self.assertEquals(mock_request, call_args[0][0][0])

        self.assertEquals('Unable to disconnect from this social account.', call_args[0][0][1])

        mock_redirect.assert_called_once_with('user:settings', username='foo')

    @mock.patch('tethys_portal.middleware.messages.success')
    @mock.patch('tethys_portal.middleware.isinstance')
    @mock.patch('tethys_portal.middleware.hasattr')
    @mock.patch('tethys_portal.middleware.redirect')
    def test_process_exception_isinstance_exception_user(self, mock_redirect, mock_hasattr, mock_isinstance,
                                                         mock_success):
        mock_request = mock.MagicMock()
        mock_request.user.is_anonymous = True

        mock_exception = mock.MagicMock()
        mock_exception.backend.name = 'social'

        mock_hasattr.return_value = True
        mock_isinstance.side_effect = False, False, True

        obj = TethysSocialAuthExceptionMiddleware()

        obj.process_exception(mock_request, mock_exception)

        call_args = mock_success.call_args_list

        self.assertEquals(mock_request, call_args[0][0][0])

        self.assertEquals('Unable to disconnect from this social account.', call_args[0][0][1])

        mock_redirect.assert_called_once_with('accounts:login')
