import pytest
from tethys_quotas.models import ResourceQuota, UserQuota, TethysAppQuota
from tethys_apps.models import TethysApp

from django.test import override_settings


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_resource_quotas_list(admin_client, load_quotas):
    assert ResourceQuota.objects.count() == 2
    response = admin_client.get("/admin/tethys_quotas/resourcequota/")
    assert response.status_code == 200


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_resource_quotas_change(admin_client, load_quotas):
    assert ResourceQuota.objects.count() == 2
    user_quota = ResourceQuota.objects.get(applies_to="django.contrib.auth.models.User")
    response = admin_client.get(
        f"/admin/tethys_quotas/resourcequota/{user_quota.id}/change/"
    )
    assert response.status_code == 200


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_tethys_app_quotas_inline_inactive(admin_client, load_quotas):
    assert ResourceQuota.objects.count() == 2
    arq = ResourceQuota.objects.get(applies_to="tethys_apps.models.TethysApp")
    arq.active = False
    arq.save()
    app = TethysApp.objects.get(package="test_app")
    response = admin_client.get(f"/admin/tethys_apps/tethysapp/{app.id}/change/")
    assert response.status_code == 200
    assert b"Tethys App Quotas" in response.content
    assert TethysAppQuota.objects.count() == 0


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_tethys_app_quotas_inline_active(admin_client, load_quotas):
    assert ResourceQuota.objects.count() == 2
    arq = ResourceQuota.objects.get(applies_to="tethys_apps.models.TethysApp")
    arq.active = True
    arq.save()
    app = TethysApp.objects.get(package="test_app")
    response = admin_client.get(f"/admin/tethys_apps/tethysapp/{app.id}/change/")
    assert response.status_code == 200
    assert b"Tethys App Quotas" in response.content
    assert TethysAppQuota.objects.count() == 1
    arq.active = False
    arq.save()


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_tethys_app_quotas_inline_active_impose_default(
    admin_client, load_quotas
):
    assert ResourceQuota.objects.count() == 2
    arq = ResourceQuota.objects.get(applies_to="tethys_apps.models.TethysApp")
    arq.active = True
    arq.impose_default = True
    arq.default = 37.6
    arq.save()
    app = TethysApp.objects.get(package="test_app")
    response = admin_client.get(f"/admin/tethys_apps/tethysapp/{app.id}/change/")
    assert response.status_code == 200
    assert b"Tethys App Quotas" in response.content
    assert b"<p>37.6</p>" in response.content
    assert TethysAppQuota.objects.count() == 1
    arq.active = False
    arq.impose_default = False
    arq.save()


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_tethys_app_quotas_inline_active_no_default(admin_client, load_quotas):
    assert ResourceQuota.objects.count() == 2
    app = TethysApp.objects.get(package="test_app")
    arq = ResourceQuota.objects.get(applies_to="tethys_apps.models.TethysApp")
    arq.active = True
    arq.impose_default = False
    TethysAppQuota.objects.create(resource_quota=arq, entity=app, value=None)
    arq.save()

    response = admin_client.get(f"/admin/tethys_apps/tethysapp/{app.id}/change/")
    assert response.status_code == 200
    assert b"Tethys App Quotas" in response.content
    assert b"<p>--</p>" in response.content
    assert TethysAppQuota.objects.count() == 1
    arq.active = False
    arq.impose_default = False
    arq.save()


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_user_quotas_inline_inactive(admin_client, admin_user, load_quotas):
    assert ResourceQuota.objects.count() == 2
    urq = ResourceQuota.objects.get(applies_to="django.contrib.auth.models.User")
    urq.active = False
    urq.save()
    response = admin_client.get(f"/admin/auth/user/{admin_user.id}/change/")
    assert response.status_code == 200
    assert b"User Quotas" in response.content
    assert UserQuota.objects.count() == 0  # User quota is inactive


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_user_quotas_inline_active(admin_client, admin_user, load_quotas):
    assert ResourceQuota.objects.count() == 2
    urq = ResourceQuota.objects.get(applies_to="django.contrib.auth.models.User")
    urq.active = True
    urq.save()
    response = admin_client.get(f"/admin/auth/user/{admin_user.id}/change/")
    assert response.status_code == 200
    assert b"User Quotas" in response.content
    assert UserQuota.objects.count() == 1
    urq.active = False
    urq.save()


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_user_quotas_inline_active_impose_default(
    admin_client, admin_user, load_quotas
):
    assert ResourceQuota.objects.count() == 2
    urq = ResourceQuota.objects.get(applies_to="django.contrib.auth.models.User")
    urq.active = True
    urq.impose_default = True
    urq.default = 29.5
    urq.save()
    response = admin_client.get(f"/admin/auth/user/{admin_user.id}/change/")
    assert response.status_code == 200
    assert b"User Quotas" in response.content
    assert b"<p>29.5</p>" in response.content
    assert UserQuota.objects.count() == 1
    urq.active = False
    urq.impose_default = False
    urq.save()


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_user_quotas_inline_no_default(admin_client, admin_user, load_quotas):
    assert ResourceQuota.objects.count() == 2
    urq = ResourceQuota.objects.get(applies_to="django.contrib.auth.models.User")
    UserQuota.objects.create(resource_quota=urq, entity=admin_user, value=None)
    urq.active = True
    urq.impose_default = False
    urq.save()
    response = admin_client.get(f"/admin/auth/user/{admin_user.id}/change/")
    assert response.status_code == 200
    assert b"User Quotas" in response.content
    assert b"<p>--</p>" in response.content
    urq.active = False
    urq.impose_default = True
    urq.save()


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_user_quotas_inline_add_user(admin_client, load_quotas):
    assert ResourceQuota.objects.count() == 2
    urq = ResourceQuota.objects.get(applies_to="django.contrib.auth.models.User")
    urq.active = True
    urq.save()
    response = admin_client.get("/admin/auth/user/add/")
    assert response.status_code == 200
    assert b"User Quotas" not in response.content
    assert UserQuota.objects.count() == 0
    urq.active = False
    urq.save()
