from django.conf import settings
from django.core.checks import Warning, register


@register()
def tenant_engine_check(app_configs, **kwargs):
    if getattr(settings, "TENANTS_ENABLED", False):
        engine = settings.DATABASES["default"]["ENGINE"]

        if engine != "django_tenants.postgresql_backend":
            return [
                Warning(
                    "Tethys Tenants is enabled, but the default database engine "
                    "is not 'django_tenants.postgresql_backend'.\n"
                    "This can result in errors involving the database. "
                    "Please update your portal_config.yml file.\n"
                    "You can use the following command to do so:\n\n"
                    "tethys settings --set DATABASES.default.ENGINE django_tenants.postgresql_backend\n",
                    id="tethys.tenants",
                )
            ]

    return []
