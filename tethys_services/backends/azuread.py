from social_core.backends.azuread_tenant import AzureADTenantOAuth2
from social_core.backends.azuread_b2c import AzureADB2COAuth2

from tethys_services.backends.multi_tenant_mixin import MultiTenantMixin


class AzureADTenantOAuth2MultiTenant(MultiTenantMixin, AzureADTenantOAuth2):
    pass


class AzureADB2COAuth2MultiTenant(MultiTenantMixin, AzureADB2COAuth2):
    pass
