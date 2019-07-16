import unittest
import tethys_apps.base.permissions as tethys_permission
from unittest import mock

from django.test import RequestFactory
from ... import UserFactory


class TestPermission(unittest.TestCase):
    def setUp(self):
        self.name = 'test_name'
        self.description = 'test_description'
        self.check_string = '<Permission name="{0}" description="{1}">'.\
            format(self.name, self.description)

    def tearDown(self):
        pass

    def test_init(self):
        result = tethys_permission.Permission(name=self.name, description=self.description)
        self.assertEqual(self.name, result.name)
        self.assertEqual(self.description, result.description)

    def test_repr(self):
        result = tethys_permission.Permission(name=self.name, description=self.description)._repr()

        # Check Result
        self.assertEqual(self.check_string, result)

    def test_str(self):
        result = tethys_permission.Permission(name=self.name, description=self.description).__str__()

        # Check Result
        self.assertEqual(self.check_string, result)

    def test_repr_(self):
        result = tethys_permission.Permission(name=self.name, description=self.description).__repr__()

        # Check Result
        self.assertEqual(self.check_string, result)


class TestPermissionGroup(unittest.TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.request_factory = RequestFactory()
        self.name = 'test_name'
        self.permissions = ['foo', 'bar']
        self.check_string = '<Group name="{0}">'.format(self.name)

    def tearDown(self):
        pass

    def test_init(self):
        result = tethys_permission.PermissionGroup(name=self.name, permissions=['foo', 'bar'])

        self.assertEqual(self.name, result.name)
        self.assertEqual(self.permissions, result.permissions)

    def test_repr(self):
        result = tethys_permission.PermissionGroup(name=self.name)._repr()

        # Check Result
        self.assertEqual(self.check_string, result)

    def test_str(self):
        result = tethys_permission.PermissionGroup(name=self.name).__str__()

        # Check Result
        self.assertEqual(self.check_string, result)

    def test_repr_(self):
        result = tethys_permission.PermissionGroup(name=self.name).__repr__()

        # Check Result
        self.assertEqual(self.check_string, result)

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
