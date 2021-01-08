from social_core.backends.okta import OktaOAuth2
from social_core.backends.okta_openidconnect import OktaOpenIdConnect

from tethys_services.backends.multi_tenant_mixin import MultiTenantMixin


class OktaOauth2MultiTenant(MultiTenantMixin, OktaOAuth2):
    pass


class OktaOpenIdConnectMultiTenant(MultiTenantMixin, OktaOpenIdConnect):
    pass
