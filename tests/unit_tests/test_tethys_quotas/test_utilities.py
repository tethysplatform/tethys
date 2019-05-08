from unittest import mock
from django.test import TestCase
from django.contrib.auth.models import User
from tethys_apps.models import TethysApp
from tethys_quotas.models import ResourceQuota, UserQuota, TethysAppQuota
from tethys_quotas import utilities


class TethysQuotasUtilitiesTest(TestCase):

    def setUp(self):
        ResourceQuota.objects.all().delete()

    def tearDown(self):
        pass

    @mock.patch('tethys_quotas.utilities.settings', RESOURCE_QUOTA_HANDLERS=['my'])
    @mock.patch('tethys_quotas.utilities.log')
    def test_bad_rq_handler(self, mock_log, _):
        utilities.sync_resource_quota_handlers()
        mock_log.warning.assert_called()

    @mock.patch('tethys_quotas.utilities.settings', RESOURCE_QUOTA_HANDLERS=[
        'tethys_quotas.handlers.workspace.WorkspaceQuotaHandler'])
    @mock.patch('tethys_quotas.utilities.log')
    def test_good_existing_rq(self, mock_log, _):
        utilities.sync_resource_quota_handlers()
        mock_log.warning.assert_not_called()

    @mock.patch('tethys_quotas.utilities.settings', RESOURCE_QUOTA_HANDLERS=['not.subclass.of.rq'])
    @mock.patch('tethys_quotas.utilities.log')
    def test_not_subclass_of_rq(self, mock_log, _):
        utilities.sync_resource_quota_handlers()
        mock_log.warning.assert_called()

    @mock.patch('tethys_quotas.models.ResourceQuota')
    def test_passes_quota_passes(self, mock_rq):
        rq = mock.MagicMock()
        mock_rq.objects.get.return_value = rq
        rq.check_quota.return_value = True
        self.assertTrue(utilities.passes_quota(UserQuota, 'codename'))

    @mock.patch('tethys_quotas.models.ResourceQuota')
    def test_passes_quota_fails(self, mock_rq):
        rq = mock.MagicMock()
        mock_rq.objects.get.return_value = rq
        rq.check_quota.return_value = False
        self.assertFalse(utilities.passes_quota(UserQuota, 'codename'))

    @mock.patch('tethys_quotas.utilities.get_quota')
    @mock.patch('tethys_quotas.models.ResourceQuota')
    def test_get_resource_available_user(self, mock_rq, mock_get_quota):
        rq = mock.MagicMock()
        rq.units = 'gb'
        mock_rq.objects.get.return_value = rq
        rqh = mock.MagicMock()
        rq.handler.return_value = rqh
        rqh.get_current_use.return_value = 1
        mock_get_quota.return_value = {'quota': 5}

        ret = utilities.get_resource_available(User(), 'codename')

        self.assertEqual(4, ret['resource_available'])
        self.assertEqual('gb', ret['units'])

    @mock.patch('tethys_quotas.utilities.get_quota')
    @mock.patch('tethys_quotas.models.ResourceQuota')
    def test_get_resource_available_app(self, mock_rq, mock_get_quota):
        rq = mock.MagicMock()
        rq.units = 'gb'
        mock_rq.objects.get.return_value = rq
        rqh = mock.MagicMock()
        rq.handler.return_value = rqh
        rqh.get_current_use.return_value = 1
        mock_get_quota.return_value = {'quota': 5}

        ret = utilities.get_resource_available(TethysApp(), 'codename')

        self.assertEqual(4, ret['resource_available'])
        self.assertEqual('gb', ret['units'])

    @mock.patch('tethys_quotas.utilities.get_quota')
    @mock.patch('tethys_quotas.models.ResourceQuota')
    def test_get_resource_not_available(self, mock_rq, mock_get_quota):
        rq = mock.MagicMock()
        mock_rq.objects.get.return_value = rq
        rqh = mock.MagicMock()
        rq.handler.return_value = rqh
        rqh.get_current_use.return_value = 6
        mock_get_quota.return_value = {'quota': 3}

        ret = utilities.get_resource_available(TethysApp(), 'codename')

        self.assertEqual(0, ret['resource_available'])

    @mock.patch('tethys_quotas.utilities.log')
    @mock.patch('tethys_quotas.models.ResourceQuota')
    def test_get_resource_available_rq_dne(self, mock_rq, mock_log):
        mock_rq.objects.get.side_effect = ResourceQuota.DoesNotExist
        mock_rq.DoesNotExist = ResourceQuota.DoesNotExist
        ret = utilities.get_resource_available(mock.MagicMock(), 'codename')

        mock_log.warning.assert_called_with('Invalid Codename: ResourceQuota with codename codename does not exist.')
        self.assertEquals(None, ret)

    @mock.patch('tethys_quotas.models.ResourceQuota')
    def test_get_quota_rq_inactive(self, mock_rq):
        rq = mock.MagicMock()
        rq.active = False
        mock_rq.objects.get.return_value = rq

        ret = utilities.get_quota(mock.MagicMock(), 'codename')
        self.assertEquals(None, ret['quota'])

    @mock.patch('tethys_quotas.models.ResourceQuota')
    def test_get_quota_bad_entity(self, mock_rq):
        rq = mock.MagicMock()
        rq.active = True
        mock_rq.objects.get.return_value = rq

        with self.assertRaises(ValueError) as context:
            utilities.get_quota(mock.MagicMock(), 'codename')
        self.assertTrue(
            'Entity needs to be User or TethysApp' in str(context.exception))

    @mock.patch('tethys_quotas.models.TethysAppQuota')
    @mock.patch('tethys_quotas.models.ResourceQuota')
    def test_get_quota_aq(self, mock_rq, mock_aq):
        rq = mock.MagicMock()
        rq.active = True
        mock_rq.objects.get.return_value = rq

        aq = mock.MagicMock()
        aq.value = 100
        mock_aq.objects.get.return_value = aq

        ret = utilities.get_quota(TethysApp(), 'codename')
        self.assertEquals(100, ret['quota'])

    @mock.patch('tethys_quotas.models.TethysAppQuota')
    @mock.patch('tethys_quotas.models.ResourceQuota')
    def test_get_quota_aq_dne(self, mock_rq, mock_aq):
        rq = mock.MagicMock()
        rq.active = True
        rq.impose_default = False
        mock_rq.objects.get.return_value = rq

        mock_aq.objects.get.side_effect = TethysAppQuota.DoesNotExist
        mock_aq.DoesNotExist = TethysAppQuota.DoesNotExist

        ret = utilities.get_quota(TethysApp(), 'codename')
        self.assertEquals(None, ret['quota'])

    @mock.patch('tethys_quotas.models.TethysAppQuota')
    @mock.patch('tethys_quotas.models.ResourceQuota')
    def test_get_quota_impose_default(self, mock_rq, mock_aq):
        rq = mock.MagicMock()
        rq.active = True
        rq.default = 100
        mock_rq.objects.get.return_value = rq

        mock_aq.objects.get.side_effect = TethysAppQuota.DoesNotExist
        mock_aq.DoesNotExist = TethysAppQuota.DoesNotExist

        ret = utilities.get_quota(TethysApp(), 'codename')
        self.assertEquals(100, ret['quota'])

    @mock.patch('tethys_quotas.models.ResourceQuota')
    def test_get_quota_staff(self, mock_rq):
        rq = mock.MagicMock()
        rq.active = True
        mock_rq.objects.get.return_value = rq

        user = User()
        user.is_staff = True

        ret = utilities.get_quota(user, 'codename')
        self.assertEquals(None, ret['quota'])
