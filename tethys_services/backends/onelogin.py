from social_core.backends.open_id_connect import OpenIdConnectAuth


from tethys_services.backends.multi_tenant_mixin import MultiTenantMixin


class OneLoginOIDC(OpenIdConnectAuth):
    """OneLogin OpenIDConnect authentication backend."""

    name = "onelogin-oidc"

    @property
    def OIDC_ENDPOINT(self):
        subdomain = self.setting("SUBDOMAIN")
        if not subdomain:
            raise ValueError(
                'You must specify your OneLogin subdomain via the "SOCIAL_AUTH_ONELOGIN_OIDC_SUBDOMAIN" '
                "setting (e.g. https://my-org.onelogin.com)."
            )

        if subdomain[-1] == "/":
            subdomain = subdomain[0:-1]

        return subdomain + "/oidc/2"


class OneLoginOIDCMultiTenant(MultiTenantMixin, OneLoginOIDC):
    pass
