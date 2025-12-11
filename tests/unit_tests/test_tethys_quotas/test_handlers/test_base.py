from unittest import mock
from django.test import TestCase
from django.contrib.auth.models import User
from tethys_apps.models import TethysApp
from django.db import transaction
from tethys_quotas.models.user_quota import UserQuota
from tethys_quotas.models.tethys_app_quota import TethysAppQuota
from tethys_quotas.models.resource_quota import ResourceQuota
from tethys_quotas.handlers.workspace import WorkspaceQuotaHandler


class ResourceQuotaHandlerTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            username="john", email="john@gmail.com", password="pass"
        )

        self.resource_quota_handler = WorkspaceQuotaHandler(user)
        self.resource_quota_user = ResourceQuota(
            codename="test_user_codename",
            name="test_name",
            description="test_description",
            default=1.21,
            units="gb",
            applies_to="django.contrib.auth.models.User",
            impose_default=False,
            help="Exceeded quota",
            _handler="tethys_quotas.handlers.workspace.WorkspaceQuotaHandler",
        )
        self.resource_quota_user.save()
        self.entity_quota_user = UserQuota(
            resource_quota=self.resource_quota_user,
            entity=user,
            value=100,
        )
        self.entity_quota_user.save()

        self.resource_quota_app = ResourceQuota(
            codename="test_app_codename",
            name="test_name",
            description="test_description",
            default=1.21,
            units="gb",
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
        self.app_model.delete()

    @mock.patch("tethys_quotas.utilities.log")
    def test_rqh_check_rq_dne(self, _):
        bad_rqh = WorkspaceQuotaHandler("not.a.user")
        self.assertTrue(bad_rqh.check())

    @mock.patch("tethys_quotas.utilities.log")
    def test_rqh_check_eq_dne(self, _):
        with transaction.atomic():
            user = User.objects.create_user(
                username="mike", email="mike@gmail.com", password="pass"
            )
            resource_quota_handler = WorkspaceQuotaHandler(user)
            self.assertEqual("workspace_quota", resource_quota_handler.codename)
            self.assertTrue(resource_quota_handler.check())

    @mock.patch("tethys_quotas.utilities.log")
    def test_rqh_check_eq_passes(self, _):
        self.assertTrue(self.resource_quota_handler.check())

    @mock.patch("tethys_quotas.utilities.log")
    def test_rqh_check_eq_app_passes(self, _):
        resource_quota_handler = WorkspaceQuotaHandler(self.app_model)

        self.assertTrue(resource_quota_handler.check())

    def test_rqh_check_resource_unavailable(self):
        class DummyEntity:
            pass

        handler = WorkspaceQuotaHandler(DummyEntity())
        with mock.patch(
            "tethys_quotas.handlers.base.get_resource_available",
            return_value={"resource_available": 0},
        ):
            assert handler.check() is False
