import unittest
from unittest import mock

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.test.utils import override_settings
from django.http import HttpResponseRedirect

from tethys_sdk.permissions import permission_required
from tethys_sdk.permissions import login_required
from .. import UserFactory


class DecoratorsTest(unittest.TestCase):

    def setUp(self):
        self.request_factory = RequestFactory()
        self.user = UserFactory()

    def tearDown(self):
        pass

    @override_settings(ENABLE_OPEN_PORTAL=True)
    def test_login_required_open_portal_True(self):
        request = self.request_factory.get('/apps/test-app')
        request.user = AnonymousUser()

        @login_required()
        def create_projects(request, *args, **kwargs):
            return "expected_result"

        ret = create_projects(request)

        self.assertEqual('expected_result', ret)

    @override_settings(ENABLE_OPEN_PORTAL=False)
    def test_login_required_open_portal_False_Fail(self):
        request = self.request_factory.get('/apps/test-app')
        request.user = AnonymousUser()

        @login_required()
        def create_projects(request, *args, **kwargs):
            return "expected_result"

        ret = create_projects(request)

        self.assertIsInstance(ret, HttpResponseRedirect)
        self.assertIn('/accounts/login/', ret.url)

    @override_settings(ENABLE_OPEN_PORTAL=False)
    def test_login_required_open_portal_False_Pass(self):
        request = self.request_factory.get('/apps/test-app')
        request.user = self.user

        @login_required()
        def create_projects(request, *args, **kwargs):
            return "expected_result"

        ret = create_projects(request)

        self.assertEqual('expected_result', ret)

    @mock.patch('tethys_apps.decorators.messages')
    @mock.patch('tethys_apps.decorators.has_permission', return_value=False)
    def test_permission_required_no_pass_authenticated(self, _, mock_messages):
        request = self.request_factory.get('/apps/test-app')
        request.user = self.user

        @permission_required('create_projects')
        def create_projects(request, *args, **kwargs):
            return "expected_result"

        ret = create_projects(request)

        mock_messages.add_message.assert_called()
        self.assertIsInstance(ret, HttpResponseRedirect)
        self.assertEqual('/apps/', ret.url)

    @mock.patch('tethys_apps.decorators.messages')
    @mock.patch('tethys_apps.decorators.has_permission', return_value=False)
    def test_permission_required_no_pass_authenticated_with_referrer(self, _, mock_messages):
        request = self.request_factory.get('/apps/test-app')
        request.user = self.user
        request.META['HTTP_REFERER'] = 'http://testserver/foo/bar'

        @permission_required('create_projects')
        def create_projects(request, *args, **kwargs):
            return "expected_result"

        ret = create_projects(request)

        mock_messages.add_message.assert_called()
        self.assertIsInstance(ret, HttpResponseRedirect)
        self.assertEqual('/foo/bar', ret.url)

    @mock.patch('tethys_apps.decorators.messages')
    @mock.patch('tethys_apps.decorators.has_permission', return_value=False)
    def test_permission_required_no_pass_not_authenticated(self, _, mock_messages):
        request = self.request_factory.get('/apps/test-app')
        request.user = AnonymousUser()

        @permission_required('create_projects')
        def create_projects(request, *args, **kwargs):
            return "expected_result"

        ret = create_projects(request)

        mock_messages.add_message.assert_called()
        self.assertIsInstance(ret, HttpResponseRedirect)
        self.assertIn('/accounts/login/', ret.url)

    @mock.patch('tethys_apps.decorators.messages')
    @mock.patch('tethys_apps.decorators.has_permission', return_value=False)
    def test_permission_required_message(self, _, mock_messages):
        request = self.request_factory.get('/apps/test-app')
        request.user = self.user
        msg = 'A different message.'

        @permission_required('create_projects', message=msg)
        def create_projects(request, *args, **kwargs):
            return "expected_result"

        ret = create_projects(request)

        mock_messages.add_message.assert_called_with(request, mock_messages.WARNING, msg)
        self.assertIsInstance(ret, HttpResponseRedirect)
        self.assertEqual('/apps/', ret.url)

    def test_blank_permissions(self):
        self.assertRaises(ValueError, permission_required)

    @mock.patch('tethys_apps.decorators.has_permission', return_value=True)
    def test_multiple_permissions(self, mock_has_permission):
        request = self.request_factory.get('/apps/test-app')
        request.user = self.user

        @permission_required('create_projects', 'delete_projects')
        def multiple_permissions(request, *args, **kwargs):
            return "expected_result"

        ret = multiple_permissions(request)
        self.assertEqual(ret, "expected_result")
        hp_call_args = mock_has_permission.call_args_list
        self.assertEqual(2, len(hp_call_args))
        self.assertEqual('create_projects', hp_call_args[0][0][1])
        self.assertEqual('delete_projects', hp_call_args[1][0][1])

    @mock.patch('tethys_apps.decorators.has_permission', return_value=True)
    def test_multiple_permissions_OR(self, _):
        request = self.request_factory.get('/apps/test-app')
        request.user = self.user

        @permission_required('create_projects', 'delete_projects', use_or=True)
        def multiple_permissions_or(request, *args, **kwargs):
            return "expected_result"

        self.assertEqual(multiple_permissions_or(request), "expected_result")

    @mock.patch('tethys_apps.decorators.tethys_portal_error', return_value=False)
    @mock.patch('tethys_apps.decorators.has_permission', return_value=False)
    @override_settings(DEBUG=True)
    def test_permission_required_exception_403(self, _, mock_tp_error):
        request = self.request_factory.get('/apps/test-app')
        request.user = self.user

        @permission_required('create_projects', raise_exception=True)
        def exception_403(request, *args, **kwargs):
            return "expected_result"

        exception_403(request)
        mock_tp_error.handler_403.assert_called_with(request)

    @mock.patch('tethys_apps.decorators.tethys_portal_error', return_value=False)
    @mock.patch('tethys_apps.decorators.has_permission', return_value=False)
    @override_settings(DEBUG=False)
    def test_permission_required_exception_404(self, _, mock_tp_error):
        request = self.request_factory.get('/apps/test-app')
        request.user = self.user

        @permission_required('create_projects', raise_exception=True)
        def exception_404(request, *args, **kwargs):
            return "expected_result"

        exception_404(request)
        mock_tp_error.handler_404.assert_called_with(request)

    def test_permission_required_no_request(self):
        @permission_required('create_projects')
        def no_request(request, *args, **kwargs):
            return "expected_result"

        self.assertRaises(ValueError, no_request)

    @mock.patch('tethys_apps.decorators.has_permission', return_value=True)
    def test_multiple_permissions_class_method(self, _):
        request = self.request_factory.get('/apps/test-app')
        request.user = self.user

        class Foo:
            @permission_required('create_projects')
            def method(self, request, *args, **kwargs):
                return "expected_result"

        f = Foo()

        self.assertEqual(f.method(request), "expected_result")
