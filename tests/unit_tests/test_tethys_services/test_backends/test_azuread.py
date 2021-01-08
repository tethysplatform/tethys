from django import test
from tethys_services.backends.azuread import AzureADB2COAuth2MultiTenant, AzureADTenantOAuth2MultiTenant
from tethys_services.backends.multi_tenant_mixin import MultiTenantMixin


class AzureADB2COAuth2MultiTenantBackendTest(test.SimpleTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_is_mtm(self):
        inst = AzureADB2COAuth2MultiTenant()
        self.assertIsInstance(inst, MultiTenantMixin)


class AzureADTenantOAuth2MultiTenantBackendTest(test.SimpleTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_is_mtm(self):
        inst = AzureADTenantOAuth2MultiTenant()
        self.assertIsInstance(inst, MultiTenantMixin)
