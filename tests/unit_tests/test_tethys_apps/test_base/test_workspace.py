import unittest
import tethys_apps.base.workspace as base_workspace
import os
import shutil
from unittest import mock
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from tethys_apps.base.workspace import user_workspace, app_workspace
from tethys_quotas.models import ResourceQuota


@user_workspace()
def user_dec_controller(request, user_workspace):
    return 'Success'


@app_workspace()
def app_dec_controller(request, app_workspace):
    return 'Success'


class TestUrlMap(unittest.TestCase):
    def setUp(self):
        self.root = os.path.abspath(os.path.dirname(__file__))
        self.test_root = os.path.join(self.root, 'test_workspace')
        self.test_root_a = os.path.join(self.test_root, 'test_workspace_a')
        self.test_root2 = os.path.join(self.root, 'test_workspace2')

    def tearDown(self):
        if os.path.isdir(self.test_root):
            shutil.rmtree(self.test_root)
        if os.path.isdir(self.test_root2):
            shutil.rmtree(self.test_root2)

    def test_TethysWorkspace(self):
        # Test Create new workspace folder test_workspace
        result = base_workspace.TethysWorkspace(path=self.test_root)
        workspace = '<TethysWorkspace path="{0}">'.format(self.test_root)

        # Create new folder inside test_workspace
        base_workspace.TethysWorkspace(path=self.test_root_a)

        # Create new folder test_workspace2
        base_workspace.TethysWorkspace(path=self.test_root2)

        self.assertEqual(result.__repr__(), workspace)
        self.assertEqual(result.path, self.test_root)

        # Create Files
        file_list = ['test1.txt', 'test2.txt']
        for file_name in file_list:
            # Create file
            open(os.path.join(self.test_root, file_name), 'a').close()

        # Test files with full path
        result = base_workspace.TethysWorkspace(path=self.test_root).files(full_path=True)
        for file_name in file_list:
            self.assertIn(os.path.join(self.test_root, file_name), result)

        # Test files without full path
        result = base_workspace.TethysWorkspace(path=self.test_root).files()
        for file_name in file_list:
            self.assertIn(file_name, result)

        # Test Directories with full path
        result = base_workspace.TethysWorkspace(path=self.root).directories(full_path=True)
        self.assertIn(self.test_root, result)
        self.assertIn(self.test_root2, result)

        # Test Directories without full path
        result = base_workspace.TethysWorkspace(path=self.root).directories()
        self.assertIn('test_workspace', result)
        self.assertIn('test_workspace2', result)
        self.assertNotIn(self.test_root, result)
        self.assertNotIn(self.test_root2, result)

        # Write to file
        f = open(os.path.join(self.test_root, 'test2.txt'), 'w')
        f.write('Hello World')
        f.close()

        # Test size greater than zero
        workspace_size = base_workspace.TethysWorkspace(path=self.test_root).get_size()
        self.assertTrue(workspace_size > 0)

        # Test get size unit conversion
        workspace_size_kb = base_workspace.TethysWorkspace(path=self.test_root).get_size('kb')
        self.assertEquals(workspace_size/1000, workspace_size_kb)

        # Test Remove file
        base_workspace.TethysWorkspace(path=self.test_root).remove('test2.txt')

        # Verify that the file has been remove
        self.assertFalse(os.path.isfile(os.path.join(self.test_root, 'test2.txt')))

        # Test Remove Directory
        base_workspace.TethysWorkspace(path=self.root).remove(self.test_root2)

        # Verify that the Directory has been remove
        self.assertFalse(os.path.isdir(self.test_root2))

        # Test Clear
        base_workspace.TethysWorkspace(path=self.test_root).clear()

        # Test size equal to zero
        workspace_size = base_workspace.TethysWorkspace(path=self.test_root).get_size()
        self.assertTrue(workspace_size == 0)

        # Verify that the Directory has been remove
        self.assertFalse(os.path.isdir(self.test_root_a))

        # Verify that the File has been remove
        self.assertFalse(os.path.isfile(os.path.join(self.test_root, 'test1.txt')))

        # Test don't allow overwriting the path property
        workspace = base_workspace.TethysWorkspace(path=self.test_root)
        workspace.path = 'foo'
        self.assertEqual(self.test_root, workspace.path)

    @mock.patch('tethys_apps.base.workspace.log')
    @mock.patch('tethys_quotas.models.ResourceQuota')
    @mock.patch('tethys_apps.utilities.get_active_app')
    @mock.patch('tethys_apps.base.workspace._get_user_workspace')
    def test_user_workspace_user(self, mock_guw, _, mock_rq, mock_log):
        mock_guw.return_value = mock.MagicMock()
        mock_rq.objects.get.return_value = mock.MagicMock(codename='user_workspace_quota')
        mock_rq.DoesNotExist = ResourceQuota.DoesNotExist
        mock_request = mock.MagicMock(spec=WSGIRequest, user=mock.MagicMock(spec=User))

        ret = user_dec_controller(mock_request)
        self.assertEqual('Success', ret)
        self.assertEqual(0, len(mock_log.warning.call_args_list))

    @mock.patch('tethys_apps.base.workspace.log')
    @mock.patch('tethys_quotas.models.ResourceQuota')
    @mock.patch('tethys_apps.utilities.get_active_app')
    @mock.patch('tethys_apps.base.workspace._get_user_workspace')
    def test_user_workspace_rq_does_not_exist(self, _, __, mock_rq, mock_log):
        mock_rq.objects.get.side_effect = ResourceQuota.DoesNotExist
        mock_rq.DoesNotExist = ResourceQuota.DoesNotExist
        mock_request = mock.MagicMock(spec=WSGIRequest, user=mock.MagicMock(spec=User))

        ret = user_dec_controller(mock_request)
        mock_log.warning.assert_called_with('ResourceQuota with codename user_workspace_quota does not exist.')
        self.assertEqual('Success', ret)

    def test_user_workspace_no_WSGIRequest(self):
        mock_request = mock.MagicMock()
        ret = None
        with self.assertRaises(ValueError) as context:
            ret = user_dec_controller(mock_request)
        self.assertTrue(
            'No request given. The user_workspace decorator only works on controllers.' in str(context.exception))
        self.assertEqual(None, ret)

    @mock.patch('tethys_apps.base.workspace.passes_quota')
    @mock.patch('tethys_quotas.models.ResourceQuota')
    @mock.patch('tethys_apps.utilities.get_active_app')
    @mock.patch('tethys_apps.base.workspace._get_user_workspace')
    def test_user_workspace_passes_quota_false(self, _, mock_app, mock_rq, mock_pq):
        mock_rq.DoesNotExist = ResourceQuota.DoesNotExist
        mock_rq.objects.get.return_value = mock.MagicMock(help='helpful message')
        mock_request = mock.MagicMock(spec=WSGIRequest, user=mock.MagicMock(spec=User))
        mock_pq.return_value = False

        ret = None
        with self.assertRaises(PermissionDenied) as context:
            ret = user_dec_controller(mock_request)
        self.assertTrue("helpful message" in str(context.exception))
        self.assertEqual(None, ret)

    @mock.patch('tethys_apps.base.workspace.log')
    @mock.patch('tethys_quotas.models.ResourceQuota')
    @mock.patch('tethys_apps.utilities.get_active_app')
    @mock.patch('tethys_apps.base.workspace._get_app_workspace')
    def test_app_workspace_app(self, mock_guw, _, mock_rq, mock_log):
        mock_guw.return_value = mock.MagicMock()
        mock_rq.objects.get.return_value = mock.MagicMock(codename='app_workspace_quota')
        mock_rq.DoesNotExist = ResourceQuota.DoesNotExist
        mock_request = mock.MagicMock(spec=WSGIRequest, user=mock.MagicMock(spec=User))

        ret = app_dec_controller(mock_request)
        self.assertEqual('Success', ret)
        self.assertEqual(0, len(mock_log.warning.call_args_list))

    @mock.patch('tethys_quotas.helpers.log')
    @mock.patch('tethys_apps.base.workspace.log')
    @mock.patch('tethys_quotas.models.ResourceQuota')
    @mock.patch('tethys_apps.utilities.get_active_app')
    @mock.patch('tethys_apps.base.workspace._get_app_workspace')
    def test_app_workspace_rq_does_not_exist(self, _, __, mock_rq, mock_log, ___):
        mock_rq.objects.get.side_effect = ResourceQuota.DoesNotExist
        mock_rq.DoesNotExist = ResourceQuota.DoesNotExist
        mock_request = mock.MagicMock(spec=WSGIRequest, user=mock.MagicMock(spec=User))

        ret = app_dec_controller(mock_request)
        mock_log.warning.assert_called_with('ResourceQuota with codename app_workspace_quota does not exist.')
        self.assertEqual('Success', ret)

    def test_app_workspace_no_WSGIRequest(self):
        mock_request = mock.MagicMock()
        ret = None
        with self.assertRaises(ValueError) as context:
            ret = app_dec_controller(mock_request)
        self.assertTrue(
            'No request given. The app_workspace decorator only works on controllers.' in str(context.exception))
        self.assertEqual(None, ret)

    @mock.patch('tethys_apps.base.workspace.passes_quota')
    @mock.patch('tethys_quotas.models.ResourceQuota')
    @mock.patch('tethys_apps.utilities.get_active_app')
    @mock.patch('tethys_apps.base.workspace._get_app_workspace')
    def test_app_workspace_passes_quota_false(self, _, mock_app, mock_rq, mock_pq):
        mock_rq.DoesNotExist = ResourceQuota.DoesNotExist
        mock_rq.objects.get.return_value = mock.MagicMock(help='helpful message')
        mock_request = mock.MagicMock(spec=WSGIRequest, user=mock.MagicMock(spec=User))
        mock_pq.return_value = False

        ret = None
        with self.assertRaises(PermissionDenied) as context:
            ret = app_dec_controller(mock_request)
        self.assertTrue("helpful message" in str(context.exception))
        self.assertEqual(None, ret)
