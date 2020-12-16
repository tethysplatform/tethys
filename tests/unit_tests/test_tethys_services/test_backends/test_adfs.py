from django import test
from tethys_services.backends.adfs import ADFSOpenIdConnect
from tethys_services.backends.multi_tenant_mixin import MultiTenantMixin


@test.override_settings(
    SOCIAL_AUTH_ADFS_OIDC_KEY='182f8cb0-b8b2-0138-3936-0647e35409d7171986',
    SOCIAL_AUTH_ADFS_OIDC_SECRET='032f86d0f5f367171fd6270f7f5fa383fa27604fake9c5f1a0a5d5d2b4227ace',
    SOCIAL_AUTH_ADFS_OIDC_DOMAIN='https://adfs.my-org.mok'
)
class ADFSOpenIdConnectBackendTest(test.SimpleTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_is_mtm(self):
        inst = ADFSOpenIdConnect()
        self.assertIsInstance(inst, MultiTenantMixin)

    def test_oidc_endpoint(self):
        inst = ADFSOpenIdConnect()

        ret = inst.OIDC_ENDPOINT

        self.assertEqual('https://adfs.my-org.mok/adfs', ret)

    @test.override_settings(SOCIAL_AUTH_ADFS_OIDC_DOMAIN='')
    def test_oidc_endpoint__no_subdomain(self):
        inst = ADFSOpenIdConnect()

        with self.assertRaises(ValueError) as exc:
            inst.OIDC_ENDPOINT
            self.assertEqual('You must specify the domain of your AD FS service via the "SOCIAL_AUTH_ADFS_OIDC_DOMAIN" '
                             'setting (e.g. https://adfs.my-org.com).', str(exc))

    @test.override_settings(SOCIAL_AUTH_ADFS_OIDC_DOMAIN='https://adfs.my-org.mok/')
    def test_oidc_endpoint__subdomain_end_slash(self):
        inst = ADFSOpenIdConnect()

        ret = inst.OIDC_ENDPOINT

        self.assertEqual('https://adfs.my-org.mok/adfs', ret)

    @test.override_settings(SOCIAL_AUTH_ADFS_OIDC_DOMAIN='https://adfs.my-org.mok')
    def test_oidc_endpoint__subdomain_no_end_slash(self):
        inst = ADFSOpenIdConnect()

        ret = inst.OIDC_ENDPOINT

        self.assertEqual('https://adfs.my-org.mok/adfs', ret)
