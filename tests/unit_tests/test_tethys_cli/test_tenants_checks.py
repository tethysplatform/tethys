from django.core import checks
from django.test import override_settings
from tethys_tenants.checks import tenant_engine_check
from tethys_utils import DOCS_BASE_URL


@override_settings(
    TENANTS_ENABLED=True,
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3"}},
)
def test_tenant_engine_check_warning():
    warnings = tenant_engine_check(None)
    assert len(warnings) == 1
    warning = warnings[0]
    assert isinstance(warning, checks.Warning)
    assert (
        warning.msg
        == "Tethys Tenants is enabled, but the default database engine is not 'django_tenants.postgresql_backend'.\nThis can result in errors involving the database. Please update your portal_config.yml file.\nYou can use the following command to do so:\n\ntethys settings --set DATABASES.default.ENGINE django_tenants.postgresql_backend\nFor more information, see the documentation at "
        f"{DOCS_BASE_URL}tethys_portal/multi_tenancy.html"
    )


@override_settings(
    TENANTS_ENABLED=True,
    DATABASES={"default": {"ENGINE": "django_tenants.postgresql_backend"}},
)
def test_tenant_engine_check_no_warning():
    warnings = tenant_engine_check(None)
    assert len(warnings) == 0


@override_settings(TENANTS_ENABLED=False)
def test_tenant_engine_check_disabled_no_warning():
    warnings = tenant_engine_check(None)
    assert len(warnings) == 0
