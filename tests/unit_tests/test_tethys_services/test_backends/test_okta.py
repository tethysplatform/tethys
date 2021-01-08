from django import test
from tethys_services.backends.okta import OktaOpenIdConnectMultiTenant, OktaOauth2MultiTenant
from tethys_services.backends.multi_tenant_mixin import MultiTenantMixin


class OktaOpenIdConnectMultiTenantBackendTest(test.SimpleTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_is_mtm(self):
        inst = OktaOpenIdConnectMultiTenant()
        self.assertIsInstance(inst, MultiTenantMixin)


class OktaOauth2MultiTenantBackendTest(test.SimpleTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_is_mtm(self):
        inst = OktaOauth2MultiTenant()
        self.assertIsInstance(inst, MultiTenantMixin)
