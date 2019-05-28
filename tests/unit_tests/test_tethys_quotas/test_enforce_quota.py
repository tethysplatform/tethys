import unittest
from unittest import mock
from tethys_quotas.decorators import enforce_quota
from tethys_quotas.models import ResourceQuota
from django.http import HttpRequest
from tethys_apps.models import TethysApp
from django.core.exceptions import PermissionDenied


@enforce_quota(codename='foo')
def a_controller(request):
    return 'Success'


class DecoratorsTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('tethys_quotas.decorators.passes_quota')
    @mock.patch('tethys_quotas.decorators.get_active_app')
    @mock.patch('tethys_quotas.decorators.ResourceQuota')
    def test_enforce_quota_applies_to_app(self, mock_RQ, mock_active_app, mock_passes_quota):
        mock_RQ.objects.get.return_value = mock.MagicMock(codename='foo', applies_to='tethys_apps.models.TethysApp')
        mock_request = mock.MagicMock(spec=HttpRequest)
        mock_active_app.return_value = mock.MagicMock(TethysApp(name='Test App'))

        ret = a_controller(mock_request)

        mock_passes_quota.assert_called()
        self.assertEqual('Success', ret)

    @mock.patch('tethys_quotas.decorators.passes_quota')
    @mock.patch('tethys_quotas.decorators.ResourceQuota')
    def test_enforce_quota_applies_to_user(self, mock_RQ, mock_passes_quota):
        mock_RQ.objects.get.return_value = mock.MagicMock(codename='foo', applies_to='django.contrib.auth.models.User')
        mock_request = mock.MagicMock(spec=HttpRequest, user=mock.MagicMock())

        ret = a_controller(mock_request)

        mock_passes_quota.assert_called()
        self.assertEqual('Success', ret)

    @mock.patch('tethys_quotas.decorators.log')
    @mock.patch('tethys_quotas.decorators.ResourceQuota')
    def test_enforce_quota_rq_does_not_exist(self, mock_RQ, mock_log):
        mock_RQ.objects.get.side_effect = ResourceQuota.DoesNotExist
        mock_RQ.DoesNotExist = ResourceQuota.DoesNotExist
        mock_request = mock.MagicMock(spec=HttpRequest)

        ret = a_controller(mock_request)

        mock_log.warning.assert_called_with('ResourceQuota with codename foo does not exist.')
        self.assertEqual('Success', ret)

    @mock.patch('tethys_quotas.decorators.log')
    def test_enforce_quota_no_HttpRequest(self, mock_log):
        mock_request = mock.MagicMock()
        ret = a_controller(mock_request)

        mock_log.warning.assert_called_with('Invalid request')
        self.assertEqual('Success', ret)

    @mock.patch('tethys_quotas.decorators.log')
    @mock.patch('tethys_quotas.decorators.ResourceQuota')
    def test_enforce_quota_bad_applies_to(self, mock_RQ, mock_log):
        mock_RQ.objects.get.return_value = mock.MagicMock(codename='foo', applies_to='not.valid.rq')
        mock_request = mock.MagicMock(spec=HttpRequest)

        ret = a_controller(mock_request)

        mock_log.warning.assert_called_with('ResourceQuota that applies_to not.valid.rq is not supported')
        self.assertEqual('Success', ret)

    @mock.patch('tethys_quotas.decorators.passes_quota')
    @mock.patch('tethys_quotas.decorators.ResourceQuota')
    def test_enforce_quota_passes_quota_false(self, mock_RQ, mock_passes_quota):
        mock_RQ.DoesNotExist = ResourceQuota.DoesNotExist

        mock_RQ.objects.get.return_value = mock.MagicMock(codename='foo',
                                                          help='helpful message',
                                                          applies_to='django.contrib.auth.models.User')
        mock_request = mock.MagicMock(spec=HttpRequest, user=mock.MagicMock())
        mock_passes_quota.return_value = False

        with self.assertRaises(PermissionDenied) as context:
            a_controller(mock_request)
        self.assertTrue("helpful message" in str(context.exception))
