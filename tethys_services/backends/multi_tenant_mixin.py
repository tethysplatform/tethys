from django.core.exceptions import ImproperlyConfigured
from social_core.utils import setting_name


class MultiTenantMixin:
    """Mixin class that adds support for multi-tenant use. Note must be used with BaseAuth class."""
    _tenant = None
    _tenant_settings = None

    def setting(self, name, default=None):
        """Return setting from tenant_settings if found there, otherwise default behavior."""
        # If the setting is in the MULTI_TENANT settings, return that value
        expanded_setting_name = setting_name(self.name, name)
        if name != 'MULTI_TENANT' and self.tenant_settings and expanded_setting_name in self.tenant_settings:
            return self.tenant_settings.get(expanded_setting_name)
        return super().setting(name, default)

    @property
    def tenant_settings(self):
        """
        Lazy loading getter for _tenant_settings.
        Returns:
            dict: the settings for self._tenant. Returns None if no MULTI_TENANT settings, tenant not set, or tenant can't be found in MULTI_TENANT settings.
        """  # noqa: E501
        if not self.tenant:
            return None

        if self._tenant_settings is None:
            multi_tenant_settings = self.setting('MULTI_TENANT')
            if not multi_tenant_settings:
                return None

            try:
                self._tenant_settings = multi_tenant_settings.get(self._tenant)
            except KeyError:
                return None
        return self._tenant_settings

    @property
    def tenant(self):
        """
        Getter for the _tenant property.

        Returns:
            str: value of self._tenant or None if not set.
        """
        return self._tenant

    @tenant.setter
    def tenant(self, val):
        """
        Normalize and validate the tenant name provided by user and set _tenant (e.g.: "GitHub" -> "github"). Validation includes verifying that the tenant is included in the MULTI_TENANT settings.

        Args:
            val (str): the raw tenant name (e.g.: GitHub).

        Raises:
            ImproperlyConfigured: if the backend-namespaced MULTI_TENANT setting cannot be found for validation.
            ValueError: if the normalized tenant string con't be found in the backend-namespaced MULTI_TENANT setting.
        """  # noqa: E501
        # Normalize before saving
        normalized_tenant = val.lower()

        # Validate tenant before saving
        multi_tenant_setting_name = setting_name(self.name, 'MULTI_TENANT')
        multi_tenant_settings = self.setting('MULTI_TENANT')
        if not multi_tenant_settings:
            raise ImproperlyConfigured(f'Backend "{type(self)}" not configured for multi-tenant: '
                                       f'{multi_tenant_setting_name} setting not found.')
        if normalized_tenant not in multi_tenant_settings:
            raise ValueError(f'Tenant "{normalized_tenant}" not found in {multi_tenant_setting_name}.')

        self._tenant = normalized_tenant
