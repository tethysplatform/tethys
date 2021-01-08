from unittest import mock

from django import test
from django.core.exceptions import ImproperlyConfigured

from tethys_services.backends.multi_tenant_mixin import MultiTenantMixin


class FakeOAuth:

    def setting(self, name, default=None):
        """Provide fake super().setting() method."""
        return 'super-setting-call'


class TestMtmBackend(MultiTenantMixin, FakeOAuth):
    name = 'test-mtm'


class MultiTenantMixinTests(test.SimpleTestCase):

    def setUp(self):
        self.backend = TestMtmBackend()
        self.test_key = '182f8cb0-b8b2-0138-3936-0647e35409d7171986'
        self.test_secret = '032f86d0f5f367171fd6270f7f5fa383fa27604fake9c5f1a0a5d5d2b4227ace'
        self.test_domain = 'https://adfs.my-org.mok'
        self.foo_bar_settings = {
            'SOCIAL_AUTH_TEST_MTM_KEY': self.test_key,
            'SOCIAL_AUTH_TEST_MTM_SECRET': self.test_secret,
            'SOCIAL_AUTH_TEST_MTM_DOMAIN': self.test_domain
        }
        self.multi_tenant_setting = {'foo bar': self.foo_bar_settings}

    def test_tenant_getter_not_set(self):
        ret = self.backend.tenant

        self.assertIsNone(ret)

    def test_tenant_getter_set(self):
        self.backend._tenant = 'foo'

        ret = self.backend.tenant

        self.assertEqual('foo', ret)

    def test_tenant_setter_valid(self):
        tenant_in = 'Foo Bar'
        self.backend.setting = mock.MagicMock(return_value=self.multi_tenant_setting)

        self.backend.tenant = tenant_in

        self.assertEqual('foo bar', self.backend._tenant)

    def test_tenant_setter_improperly_configured(self):
        tenant_in = 'Foo Bar'
        self.backend.setting = mock.MagicMock(return_value=None)

        with self.assertRaises(ImproperlyConfigured) as cm:
            self.backend.tenant = tenant_in

        self.assertEqual('Backend "test-mtm" not configured for multi-tenant: '
                         'SOCIAL_AUTH_TEST_MTM_MULTI_TENANT setting not found.',
                         str(cm.exception))

    def test_tenant_setter_value_error(self):
        tenant_in = 'Foo Bar'
        self.backend.setting = mock.MagicMock(return_value={'some other tenant': {}})

        with self.assertRaises(ValueError) as cm:
            self.backend.tenant = tenant_in

        self.assertEqual('Tenant "foo bar" not found in SOCIAL_AUTH_TEST_MTM_MULTI_TENANT.',
                         str(cm.exception))

    def test_tenant_settings_not_loaded(self):
        self.backend._tenant = 'foo bar'
        self.backend.setting = mock.MagicMock(return_value=self.multi_tenant_setting)

        ret = self.backend.tenant_settings

        self.assertDictEqual(self.foo_bar_settings, ret)
        self.assertDictEqual(self.foo_bar_settings, self.backend._tenant_settings)

    def test_tenant_settings_loaded(self):
        self.backend._tenant = 'foo bar'
        self.backend._tenant_settings = self.foo_bar_settings
        mock_multi_tenant_settings = mock.MagicMock()
        self.backend.setting = mock_multi_tenant_settings

        ret = self.backend.tenant_settings

        self.assertDictEqual(self.foo_bar_settings, ret)
        mock_multi_tenant_settings.assert_not_called()

    def test_tenant_settings_no_tenant(self):
        ret = self.backend.tenant_settings

        self.assertIsNone(ret)

    def test_tenant_settings_no_mutli_tenant_setting(self):
        self.backend._tenant = 'foo bar'
        self.backend.setting = mock.MagicMock(return_value=None)

        ret = self.backend.tenant_settings

        self.assertIsNone(ret)

    def test_tenant_settings_tenant_not_in_multi_tenant_settings(self):
        self.backend._tenant = 'foo bar'
        self.backend.setting = mock.MagicMock(return_value={'some other tenant': {}})

        ret = self.backend.tenant_settings

        self.assertIsNone(ret)

    def test_setting_name_is_multi_tenant(self):
        ret = self.backend.setting('MULTI_TENANT')

        self.assertEqual('super-setting-call', ret)

    @mock.patch('tethys_services.backends.multi_tenant_mixin.MultiTenantMixin.tenant_settings',
                new_callable=mock.PropertyMock)
    def test_setting_no_tenant_settings(self, mock_tenant_settings):
        backend = TestMtmBackend()
        mock_tenant_settings.return_value = None

        ret = backend.setting('KEY')

        self.assertEqual('super-setting-call', ret)

    @mock.patch('tethys_services.backends.multi_tenant_mixin.MultiTenantMixin.tenant_settings',
                new_callable=mock.PropertyMock)
    def test_setting_not_in_tenant_settings(self, mock_tenant_settings):
        backend = TestMtmBackend()
        mock_tenant_settings.return_value = self.foo_bar_settings

        ret = backend.setting('FOO')

        self.assertEqual('super-setting-call', ret)

    @mock.patch('tethys_services.backends.multi_tenant_mixin.MultiTenantMixin.tenant_settings',
                new_callable=mock.PropertyMock)
    def test_setting_in_tenant_settings(self, mock_tenant_settings):
        backend = TestMtmBackend()
        mock_tenant_settings.return_value = self.foo_bar_settings
        self.assertDictEqual(self.foo_bar_settings, backend.tenant_settings)
        ret = backend.setting('KEY')

        self.assertEqual(self.test_key, ret)
