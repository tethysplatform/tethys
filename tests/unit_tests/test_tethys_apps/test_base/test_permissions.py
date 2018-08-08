import unittest
import tethys_apps.base.permissions as tethys_permission
import mock

from django.test import RequestFactory
from tests.factories.django_user import UserFactory


class TestPermission(unittest.TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.request_factory = RequestFactory()

    def tearDown(self):
        pass

    def test_Permission(self):
        name = 'test_name'
        description = 'test_description'

        result = tethys_permission.Permission(name=name, description=description)

        # Check Result
        self.assertEqual(name, result.name)
        self.assertEqual(description, result.description)

        output = '<Permission name="{0}" description="{1}">'.format(name, description)
        self.assertEqual(output, str(result))

        output2 = u'%s' % result
        self.assertEqual(output, output2)

    def test_PermissionGroup(self):
        name = 'test_group'

        result = tethys_permission.PermissionGroup(name=name)

        # Check Result
        self.assertEqual(name, result.name)

        output = '<Group name="{0}">'.format(name)
        self.assertEqual(output, str(result))

        output2 = u'%s' % result
        self.assertEqual(output, output2)

    @mock.patch('tethys_apps.utilities.get_active_app')
    def test_has_permission(self, mock_app):
        request = self.request_factory
        self.user.has_perm = mock.MagicMock()
        request.user = self.user
        mock_app.return_value = mock.MagicMock(package='test_package')
        result = tethys_permission.has_permission(request=request, perm='test_perm')
        self.assertTrue(result)

    @mock.patch('tethys_apps.utilities.get_active_app')
    def test_has_permission_no(self, mock_app):
        request = self.request_factory
        self.user.has_perm = mock.MagicMock(return_value=False)
        request.user = self.user
        mock_app.return_value = mock.MagicMock(package='test_package')
        result = tethys_permission.has_permission(request=request, perm='test_perm')
        self.assertFalse(result)
