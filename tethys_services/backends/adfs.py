from social_core.backends.open_id_connect import OpenIdConnectAuth

from tethys_services.backends.multi_tenant_mixin import MultiTenantMixin


class ADFSOpenIdConnect(MultiTenantMixin, OpenIdConnectAuth):
    """AD FS 4.0+ OpenIDConnect authentication backend."""
    name = 'adfs-oidc'

    @property
    def OIDC_ENDPOINT(self):
        subdomain = self.setting('DOMAIN')
        if not subdomain:
            raise ValueError('You must specify the domain of your AD FS service via the "SOCIAL_AUTH_ADFS_OIDC_DOMAIN" '
                             'setting (e.g. https://adfs.my-org.com).')

        if subdomain[-1] == '/':
            subdomain = subdomain[0:-1]

        return subdomain + '/adfs'
