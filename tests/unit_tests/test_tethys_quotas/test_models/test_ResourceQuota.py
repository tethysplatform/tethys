from tethys_sdk.testing import TethysTestCase
from tethys_quotas.models.resource_quota import ResourceQuota
import mock


def test_function():
    pass


class ResourceQuotaTest(TethysTestCase):
    def set_up(self):
        self.resourcequota_user = ResourceQuota(
            codename='test_codename',
            name='test_name',
            description='test_description',
            default=1.21,
            units='GW',
            applies_to='django.contrib.auth.models.User',
            impose_default=True,
            help='Exceeded quota',
            _handler='tethys_quotas.handlers.WorkspaceQuotaHandler'
        )
        self.resourcequota_user.save()

        self.resourcequota_app = ResourceQuota(
            codename='test_codename',
            name='test_name',
            description='test_description',
            default=1.21,
            units='GW',
            applies_to='tethys_app.models.TethysApp',
            impose_default=True,
            help='Exceeded quota',
            _handler='tethys_quotas.handlers.WorkspaceQuotaHandler'
        )
        self.resourcequota_app.save()

    def tear_down(self):
        self.resourcequota_user.delete()
        self.resourcequota_app.delete()

    def test_handler(self):
        with self.assertRaises(NotImplemented) as context:
            self.resourcequota_user.handler

        self.resourcequota_user.assertTrue('Handler property net yet implemented' in context.exception)
