import unittest
from unittest import mock

from django.http import HttpResponseBadRequest
from django.test import override_settings

from .mock_decorator import mock_decorator

# Fixes the Cache-Control error in tests. Must appear before view imports.
mock.patch('django.views.decorators.cache.never_cache', lambda x: x).start()
mock.patch('social_django.utils.psa', side_effect=mock_decorator).start()

from tethys_portal.views.psa import tenant  # noqa: E402


class TethysPortalViewsAccountsTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @override_settings(SSO_TENANT_ALIAS='foo bar')
    @mock.patch('tethys_portal.views.psa.SsoTenantForm')
    @mock.patch('tethys_portal.views.psa.render')
    def test_tenant_get(self, mock_render, mock_tenant_form):
        mock_request = mock.MagicMock(method='GET', POST=dict())  # GET request
        backend = 'foo'

        ret = tenant(mock_request, backend=backend)

        mock_tenant_form.assert_called()

        mock_render.assert_called_with(
            mock_request,
            'tethys_portal/accounts/sso_tenant.html',
            {
                'form': mock_tenant_form(),
                'form_title': 'Foo Bar',
                'page_title': 'Foo Bar'
            }
        )
        self.assertEqual(mock_render(), ret)

    @override_settings(SSO_TENANT_ALIAS='foo bar')
    @mock.patch('tethys_portal.forms.SsoTenantForm')
    def test_tenant_view_post_no_submit(self, mock_tenant_form):
        mock_request = mock.MagicMock(method='POST', POST=dict())  # Empty POST dict
        backend = 'foo'

        ret = tenant(mock_request, backend)

        mock_tenant_form.assert_not_called()

        self.assertIsInstance(ret, HttpResponseBadRequest)

    @override_settings(SSO_TENANT_ALIAS='foo bar')
    @mock.patch('tethys_portal.views.psa.SsoTenantForm')
    @mock.patch('tethys_portal.views.psa.render')
    def test_tenant_view_post_valid(self, mock_render, mock_tenant_form):
        post_params = {
            'sso-tenant-submit': 'submit',
            'tenant': 'GitHub',
            'remember': False
        }
        mock_request = mock.MagicMock(method='POST', POST=post_params)  # valid POST request
        backend = 'foo'

        ret = tenant(mock_request, backend)

        # Make sure form is bound to POST data
        mock_tenant_form.assert_called_with(mock_request.POST)

        self.assertEqual(mock_render(), ret)
