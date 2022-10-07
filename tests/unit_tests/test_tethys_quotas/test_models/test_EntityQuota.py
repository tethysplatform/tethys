from django.test import TestCase
from django.contrib.auth.models import User
from tethys_apps.models import TethysApp
from tethys_quotas.models import UserQuota, TethysAppQuota
from tethys_quotas.models import ResourceQuota
from tethys_quotas.handlers.base import ResourceQuotaHandler


class EntityQuotaTest(TestCase):
    def setUp(self):
        self.resource_quota_user = ResourceQuota(
            codename="test_user_codename",
            name="test_name",
            description="test_description",
            default=1.21,
            units="GW",
            applies_to="django.contrib.auth.models.User",
            impose_default=True,
            help="Exceeded quota",
            _handler="tethys_quotas.handlers.workspace.WorkspaceQuotaHandler",
        )
        self.resource_quota_user.save()
        self.user = User.objects.create_user(
            username="john", email="john@gmail.com", password="pass"
        )
        self.user.save()
        self.entity_quota_user = UserQuota(
            resource_quota=self.resource_quota_user,
            entity=self.user,
            value=100,
        )
        self.entity_quota_user.save()

        self.resource_quota_app = ResourceQuota(
            codename="test_app_codename",
            name="test_name",
            description="test_description",
            default=1.21,
            units="GW",
            applies_to="tethys_apps.models.TethysApp",
            impose_default=True,
            help="Exceeded quota",
            _handler="tethys_quotas.handlers.workspace.WorkspaceQuotaHandler",
        )
        self.resource_quota_app.save()
        self.app_model = TethysApp(name="Test App")
        self.app_model.save()
        self.entity_quota_app = TethysAppQuota(
            resource_quota=self.resource_quota_app,
            entity=self.app_model,
            value=200,
        )
        self.entity_quota_app.save()

    def tearDown(self):
        self.resource_quota_user.delete()
        self.entity_quota_user.delete()
        self.resource_quota_app.delete()
        self.entity_quota_app.delete()

    def test_query(self):
        eq_user = UserQuota.objects.get(value=100)
        self.assertEqual("john", eq_user.entity.username)

        eq_app = TethysAppQuota.objects.get(value=200)
        self.assertEqual("Test App", eq_app.entity.name)

    def test_rqh_get_current_use(self):
        resource_quota_handler = ResourceQuotaHandler("entity")
        self.assertEqual(None, resource_quota_handler.get_current_use())
