from unittest import mock
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.db import transaction
from django.test import TestCase
from tethys_quotas.models.resource_quota import ResourceQuota
from tethys_quotas.handlers.base import ResourceQuotaHandlerSub


class ResourceQuotaTest(TestCase):
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

    def tearDown(self):
        self.resource_quota_user.delete()
        self.resource_quota_app.delete()

    def test_query(self):
        resource_quotas = ResourceQuota.objects.all()
        self.assertEqual(2, len(resource_quotas))

        rq_app = ResourceQuota.objects.get(codename="test_app_codename")
        self.assertEqual("tethys_apps.models.TethysApp", rq_app.applies_to)

    def test_codename_unique(self):
        duplicate_rq = ResourceQuota(
            codename="test_user_codename",
            name="test_name",
            description="test_description",
            default=1.21,
            units="GW",
            applies_to="django.contrib.auth.models.User",
            impose_default=True,
            help="Exceeded quota",
            _handler="tethys_quotas.handlers.WorkspaceQuotaHandler",
        )

        with transaction.atomic():
            self.assertRaises(IntegrityError, duplicate_rq.save)

    def test_handler_str_nonexistant_class(self):
        with self.assertRaises(ValueError) as context:
            self.resource_quota_user.handler = "Pizza.is.good"
        self.assertTrue(
            "must be a subclass of ResourceQuotaHandler" in str(context.exception)
        )

    def test_handler_str_valid(self):
        self.resource_quota_user.handler = (
            "tethys_quotas.handlers.base.ResourceQuotaHandlerSub"
        )
        self.assertEqual(ResourceQuotaHandlerSub, self.resource_quota_user.handler)

    def test_handler_str_not_subclass(self):
        with self.assertRaises(ValueError) as context:
            self.resource_quota_user.handler = (
                "tethys_quotas.models.resource_quota.ResourceQuota"
            )
        self.assertTrue(
            "must be a subclass of ResourceQuotaHandler" in str(context.exception)
        )

    def test_handler_class_valid(self):
        self.resource_quota_user.handler = ResourceQuotaHandlerSub
        self.assertEqual(ResourceQuotaHandlerSub, self.resource_quota_user.handler)

    def test_handler_class_not_subclass(self):
        with self.assertRaises(ValueError) as context:
            self.resource_quota_user.handler = ResourceQuota
        self.assertTrue(
            "must be a subclass of ResourceQuotaHandler" in str(context.exception)
        )

    @mock.patch("tethys_quotas.utilities.log")
    def test_check_quota_valid(self, _):
        self.resource_quota_user.handler = ResourceQuotaHandlerSub
        self.assertTrue(self.resource_quota_user.check_quota(User()))

    def test_check_quota_invalid_entity(self):
        with self.assertRaises(ValueError) as context:
            self.resource_quota_user.check_quota("not a valid entity")
        self.assertTrue("must be a django User or TethysApp" in str(context.exception))
