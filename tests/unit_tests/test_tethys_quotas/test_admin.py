import pytest
from unittest import mock
from tethys_quotas.admin import (
    TethysAppQuotasSettingInline,
    ResourceQuotaAdmin,
    UserQuotasSettingInline,
    TethysQuotasSettingInline,
)
from tethys_quotas.models import ResourceQuota, UserQuota, TethysAppQuota


@pytest.fixture
def resource_quota_admin():
    return ResourceQuotaAdmin(mock.MagicMock(), mock.MagicMock())


def test_ResourceQuotaAdmin_fields(resource_quota_admin):
    expected_fields = (
        "name",
        "description",
        "default",
        "units",
        "codename",
        "applies_to",
        "help",
        "active",
        "impose_default",
    )
    expected_readonly_fields = (
        "codename",
        "name",
        "description",
        "units",
        "applies_to",
    )
    assert resource_quota_admin.fields == expected_fields
    assert resource_quota_admin.readonly_fields == expected_readonly_fields


def test_ResourceQuotaAdmin_has_delete_permission(resource_quota_admin):
    mock_request = mock.MagicMock()
    assert resource_quota_admin.has_delete_permission(mock_request) is False


def test_ResourceQuotaAdmin_has_delete_permission_obj(resource_quota_admin):
    mock_request = mock.MagicMock()
    mock_obj = mock.MagicMock()
    assert resource_quota_admin.has_delete_permission(mock_request, mock_obj) is False


def test_ResourceQuotaAdmin_has_add_permission(resource_quota_admin):
    mock_request = mock.MagicMock()
    assert resource_quota_admin.has_add_permission(mock_request) is False

    def test_ResourceQuotaAdmin_has_add_permission_obj(resource_quota_admin):
        mock_request = mock.MagicMock()
        mock_obj = mock.MagicMock()
        assert resource_quota_admin.has_add_permission(mock_request, mock_obj) is False


@pytest.fixture
def user_quotas_setting_inline():
    return UserQuotasSettingInline(mock.MagicMock(), mock.MagicMock())


def test_UserQuotasSettingInline_fields(user_quotas_setting_inline):
    expected_readonly_fields = ("name", "description", "default", "units")
    expected_fields = ("name", "description", "value", "default", "units")
    expected_model = UserQuota
    assert user_quotas_setting_inline.readonly_fields == expected_readonly_fields
    assert user_quotas_setting_inline.fields == expected_fields
    assert user_quotas_setting_inline.model == expected_model

    def test_TethysQuotasSettingInline_has_delete_permission():
        inline = TethysQuotasSettingInline(mock.MagicMock(), mock.MagicMock())
        mock_request = mock.MagicMock()
        assert inline.has_delete_permission(mock_request) is False
        assert inline.has_delete_permission(mock_request, mock.MagicMock()) is False

    def test_TethysQuotasSettingInline_has_add_permission():
        inline = TethysQuotasSettingInline(mock.MagicMock(), mock.MagicMock())
        mock_request = mock.MagicMock()
        assert inline.has_add_permission(mock_request) is False
        assert inline.has_add_permission(mock_request, mock.MagicMock()) is False


@pytest.fixture
def mock_request():
    req = mock.MagicMock()
    req.resolver_match.kwargs = {"object_id": 1}
    return req


def make_user_quota(resource_quota=None, user=None):
    uq = mock.MagicMock(spec=UserQuota)
    uq.resource_quota = resource_quota
    uq.entity = user
    return uq


def make_resource_quota(
    active=True,
    impose_default=False,
    applies_to="django.contrib.auth.models.User",
    default=42,
    units="MB",
):
    rq = mock.MagicMock(spec=ResourceQuota)
    rq.active = active
    rq.impose_default = impose_default
    rq.applies_to = applies_to
    rq.default = default
    rq.units = units
    rq.name = "RQName"
    rq.description = "RQDesc"
    rq.id = 99
    return rq


def test_UserQuotasSettingInline_get_queryset_no_resource_quota(
    monkeypatch, user_quotas_setting_inline, mock_request
):
    # No resource quota exists
    monkeypatch.setattr(
        ResourceQuota.objects,
        "filter",
        lambda **kwargs: mock.MagicMock(exists=lambda: False),
    )
    result = user_quotas_setting_inline.get_queryset(mock_request)
    assert result is not None  # Should be the super's qs


def test_UserQuotasSettingInline_get_queryset_inactive_resource_quota(
    monkeypatch, user_quotas_setting_inline, mock_request
):
    # Resource quota exists but inactive
    rq = make_resource_quota(active=False)
    qs_mock = mock.MagicMock()
    qs_mock.exists.return_value = True
    qs_mock.first.return_value = rq
    monkeypatch.setattr(ResourceQuota.objects, "filter", lambda **kwargs: qs_mock)
    result = user_quotas_setting_inline.get_queryset(mock_request)
    assert result is None


def test_UserQuotasSettingInline_get_queryset_new_user(
    monkeypatch, user_quotas_setting_inline
):
    # No user_id in request
    rq = make_resource_quota(active=True)
    qs_mock = mock.MagicMock()
    qs_mock.exists.return_value = True
    qs_mock.first.return_value = rq
    monkeypatch.setattr(ResourceQuota.objects, "filter", lambda **kwargs: qs_mock)
    req = mock.MagicMock()
    req.resolver_match.kwargs = {}
    result = user_quotas_setting_inline.get_queryset(req)
    assert result is None


def test_UserQuotasSettingInline_get_queryset_impose_default(
    monkeypatch, user_quotas_setting_inline, mock_request
):
    # Resource quota exists, active, impose_default, no qs exists
    rq = make_resource_quota(active=True, impose_default=True)
    qs_mock = mock.MagicMock()
    qs_mock.exists.return_value = True
    qs_mock.first.return_value = rq
    # Patch User.objects.get
    user = mock.MagicMock()
    monkeypatch.setattr(ResourceQuota.objects, "filter", lambda **kwargs: qs_mock)
    monkeypatch.setattr("django.contrib.auth.models.User.objects.get", lambda id: user)
    # Patch qs.filter().exists() to False
    qs = mock.MagicMock()
    qs.filter.return_value.exists.return_value = False
    monkeypatch.setattr(user_quotas_setting_inline, "get_queryset", lambda req: qs)
    # Patch UserQuota.save
    monkeypatch.setattr(UserQuota, "save", lambda self: None)
    # Should not raise
    user_quotas_setting_inline.get_queryset(mock_request)


def test_UserQuotasSettingInline_name():
    rq = make_resource_quota()
    uq = make_user_quota(resource_quota=rq)
    # Patch ContentType and reverse
    with (
        mock.patch(
            "django.contrib.contenttypes.models.ContentType.objects.get_for_model",
            return_value=mock.MagicMock(
                app_label="tethys_quotas", model="resourcequota"
            ),
        ),
        mock.patch(
            "django.urls.reverse",
            return_value="/admin/tethys_quotas/resourcequota/99/change/",
        ),
    ):
        result = UserQuotasSettingInline.name(uq)
        assert '<a href="/admin/tethys_quotas/resourcequota/99/change/"' in result


def test_UserQuotasSettingInline_description():
    rq = make_resource_quota()
    uq = make_user_quota(resource_quota=rq)
    result = UserQuotasSettingInline.description(uq)
    assert result == rq.description


def test_UserQuotasSettingInline_default():
    rq = make_resource_quota(impose_default=True, default=123)
    uq = make_user_quota(resource_quota=rq)
    result = UserQuotasSettingInline.default(uq)
    assert result == 123
    rq2 = make_resource_quota(impose_default=False)
    uq2 = make_user_quota(resource_quota=rq2)
    result2 = UserQuotasSettingInline.default(uq2)
    assert result2 == "--"

    def test_UserQuotasSettingInline_default_fallback():
        # Pass a non-UserQuota argument, should not raise, should return None
        result = UserQuotasSettingInline.default("not_a_quota")
        assert result is None


def test_UserQuotasSettingInline_units():
    rq = make_resource_quota(units="GB")
    uq = make_user_quota(resource_quota=rq)
    result = UserQuotasSettingInline.units(uq)
    assert result == "GB"

    def test_UserQuotasSettingInline_units_fallback():
        # Pass a non-UserQuota argument, should not raise, should return None
        result = UserQuotasSettingInline.units("not_a_quota")
        assert result is None


# --- Additional coverage for TethysAppQuotasSettingInline ---
def make_app_quota(resource_quota=None, app=None):
    aq = mock.MagicMock(spec=TethysAppQuota)
    aq.resource_quota = resource_quota
    aq.entity = app
    return aq


def test_TethysAppQuotasSettingInline_get_queryset_no_resource_quota(monkeypatch):
    inline = TethysAppQuotasSettingInline(mock.MagicMock(), mock.MagicMock())
    monkeypatch.setattr(
        ResourceQuota.objects,
        "filter",
        lambda **kwargs: mock.MagicMock(exists=lambda: False),
    )
    req = mock.MagicMock()
    req.resolver_match.kwargs = {"object_id": 1}
    result = inline.get_queryset(req)
    assert result is not None


def test_TethysAppQuotasSettingInline_get_queryset_inactive_resource_quota(monkeypatch):
    inline = TethysAppQuotasSettingInline(mock.MagicMock(), mock.MagicMock())
    rq = make_resource_quota(active=False, applies_to="tethys_apps.models.TethysApp")
    qs_mock = mock.MagicMock()
    qs_mock.exists.return_value = True
    qs_mock.first.return_value = rq
    monkeypatch.setattr(ResourceQuota.objects, "filter", lambda **kwargs: qs_mock)
    req = mock.MagicMock()
    req.resolver_match.kwargs = {"object_id": 1}
    result = inline.get_queryset(req)
    assert result is None


def test_TethysAppQuotasSettingInline_get_queryset_impose_default(monkeypatch):
    inline = TethysAppQuotasSettingInline(mock.MagicMock(), mock.MagicMock())
    rq = make_resource_quota(
        active=True, impose_default=True, applies_to="tethys_apps.models.TethysApp"
    )
    qs_mock = mock.MagicMock()
    qs_mock.exists.return_value = True
    qs_mock.first.return_value = rq
    app = mock.MagicMock()
    monkeypatch.setattr(ResourceQuota.objects, "filter", lambda **kwargs: qs_mock)
    monkeypatch.setattr("tethys_apps.models.TethysApp.objects.get", lambda id: app)
    qs = mock.MagicMock()
    qs.filter.return_value.exists.return_value = False
    monkeypatch.setattr(inline, "get_queryset", lambda req: qs)
    monkeypatch.setattr(TethysAppQuota, "save", lambda self: None)
    req = mock.MagicMock()
    req.resolver_match.kwargs = {"object_id": 1}
    inline.get_queryset(req)


def test_TethysAppQuotasSettingInline_name():
    rq = make_resource_quota(applies_to="tethys_apps.models.TethysApp")
    aq = make_app_quota(resource_quota=rq)
    with (
        mock.patch(
            "django.contrib.contenttypes.models.ContentType.objects.get_for_model",
            return_value=mock.MagicMock(
                app_label="tethys_quotas", model="tethysappquota"
            ),
        ),
        mock.patch(
            "django.urls.reverse",
            return_value="/admin/tethys_quotas/tethysappquota/99/change/",
        ),
    ):
        result = TethysAppQuotasSettingInline.name(aq)
        assert '<a href="/admin/tethys_quotas/tethysappquota/99/change/"' in result


def test_TethysAppQuotasSettingInline_description():
    rq = make_resource_quota(applies_to="tethys_apps.models.TethysApp")
    aq = make_app_quota(resource_quota=rq)
    result = TethysAppQuotasSettingInline.description(aq)
    assert result == rq.description


def test_TethysAppQuotasSettingInline_default():
    rq = make_resource_quota(
        impose_default=True, default=321, applies_to="tethys_apps.models.TethysApp"
    )
    aq = make_app_quota(resource_quota=rq)
    result = TethysAppQuotasSettingInline.default(aq)
    assert result == 321
    rq2 = make_resource_quota(
        impose_default=False, applies_to="tethys_apps.models.TethysApp"
    )
    aq2 = make_app_quota(resource_quota=rq2)
    result2 = TethysAppQuotasSettingInline.default(aq2)
    assert result2 == "--"

    def test_TethysAppQuotasSettingInline_default_fallback():
        # Pass a non-TethysAppQuota argument, should not raise, should return None
        result = TethysAppQuotasSettingInline.default("not_an_app_quota")
        assert result is None


def test_TethysAppQuotasSettingInline_units():
    rq = make_resource_quota(units="TB", applies_to="tethys_apps.models.TethysApp")
    aq = make_app_quota(resource_quota=rq)
    result = TethysAppQuotasSettingInline.units(aq)
    assert result == "TB"

    def test_TethysAppQuotasSettingInline_units_fallback():
        # Pass a non-TethysAppQuota argument, should not raise, should return None
        result = TethysAppQuotasSettingInline.units("not_an_app_quota")
        assert result is None
