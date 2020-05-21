import unittest
from unittest import mock

from tethys_portal.middleware import TethysSocialAuthExceptionMiddleware, TethysAppAccessMiddleware
from django.core.exceptions import PermissionDenied


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

        self.assertEqual(mock_request, call_args[0][0][0])

        self.assertEqual('The Google account you tried to connect to has already been associated with another '
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

        self.assertEqual(mock_request, call_args[0][0][0])

        self.assertEqual('The LinkedIn account you tried to connect to has already been associated with another '
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

        self.assertEqual(mock_request, call_args[0][0][0])

        self.assertEqual('The HydroShare account you tried to connect to has already been associated with '
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

        self.assertEqual(mock_request, call_args[0][0][0])

        self.assertEqual('The Facebook account you tried to connect to has already been associated with '
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

        self.assertEqual(mock_request, call_args[0][0][0])

        self.assertEqual('The social account you tried to connect to has already been associated with '
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

        self.assertEqual(mock_request, call_args[0][0][0])

        self.assertEqual('Unable to disconnect from this social account.', call_args[0][0][1])

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

        self.assertEqual(mock_request, call_args[0][0][0])

        self.assertEqual('Unable to disconnect from this social account.', call_args[0][0][1])

        mock_redirect.assert_called_once_with('accounts:login')

    @mock.patch('tethys_portal.middleware.get_active_app')
    def test_app_access_app_none(self, mock_app):
        mock_app.return_value = None
        mock_request = mock.MagicMock()
        mock_request.return_value = True

        obj = TethysAppAccessMiddleware(mock_request)
        result = obj.__call__(mock_request)

        self.assertTrue(result)

    @mock.patch('tethys_portal.middleware.handler_404')
    @mock.patch('tethys_portal.middleware.get_active_app')
    def test_app_access_disabled(self, mock_app, mock_404):
        mock_app.return_value = mock.MagicMock(enabled=False)
        mock_request1 = mock.MagicMock()

        obj1 = TethysAppAccessMiddleware(mock_request1)
        obj1.__call__(mock_request1)

        self.assertEqual(mock_404.call_args_list[0][0][2], "This app is disabled. A user with admin permissions can "
                                                           "enable this app from the app settings page.")

        mock_request2 = mock.MagicMock()
        mock_request2.user.is_staff = False

        obj2 = TethysAppAccessMiddleware(mock_request2)
        obj2.__call__(mock_request2)

        self.assertEqual(mock_404.call_args_list[0][0][1], PermissionDenied)

    @mock.patch('tethys_portal.middleware.user_can_access_app')
    @mock.patch('tethys_portal.middleware.get_active_app')
    def test_app_access_has_permission(self, mock_app, mock_has_perm):
        mock_app.return_value = mock.MagicMock(enabled=True)
        mock_request = mock.MagicMock()

        obj = TethysAppAccessMiddleware(mock_request)
        obj.__call__(mock_request)

        self.assertEqual(mock_has_perm.call_args_list[0][0][1], mock_app())

    @mock.patch('tethys_portal.middleware.handler_404')
    @mock.patch('tethys_portal.middleware.user_can_access_app')
    @mock.patch('tethys_portal.middleware.get_active_app')
    def test_app_access_no_permission(self, mock_app, mock_has_perm, mock_404):
        mock_app.return_value = mock.MagicMock(enabled=True)
        mock_request = mock.MagicMock()
        mock_has_perm.return_value = False

        obj = TethysAppAccessMiddleware(mock_request)
        obj.__call__(mock_request)

        self.assertEqual(mock_404.call_args_list[0][0][1], PermissionDenied)
