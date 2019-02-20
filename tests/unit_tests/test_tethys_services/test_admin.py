import unittest
from unittest import mock

from django.utils.translation import ugettext_lazy as _
from tethys_services.models import DatasetService, SpatialDatasetService, WebProcessingService, PersistentStoreService
from tethys_services.admin import DatasetServiceForm, SpatialDatasetServiceForm, WebProcessingServiceForm,\
    PersistentStoreServiceForm, DatasetServiceAdmin, SpatialDatasetServiceAdmin, WebProcessingServiceAdmin,\
    PersistentStoreServiceAdmin


class TestTethysServicesAdmin(unittest.TestCase):

    def setUp(self):
        self.expected_labels = {
            'public_endpoint': _('Public Endpoint')
        }

    def tearDown(self):
        pass

    def test_DatasetServiceForm(self):
        mock_args = mock.MagicMock()
        expected_fields = ('name', 'engine', 'endpoint', 'public_endpoint', 'apikey', 'username', 'password')

        ret = DatasetServiceForm(mock_args)
        self.assertEquals(DatasetService, ret.Meta.model)
        self.assertEquals(expected_fields, ret.Meta.fields)
        self.assertTrue('password' in ret.Meta.widgets)
        self.assertEquals(self.expected_labels, ret.Meta.labels)

    def test_SpatialDatasetServiceForm(self):
        mock_args = mock.MagicMock()
        expected_fields = ('name', 'engine', 'endpoint', 'public_endpoint', 'apikey', 'username', 'password')

        ret = SpatialDatasetServiceForm(mock_args)
        self.assertEquals(SpatialDatasetService, ret.Meta.model)
        self.assertEquals(expected_fields, ret.Meta.fields)
        self.assertTrue('password' in ret.Meta.widgets)
        self.assertEquals(self.expected_labels, ret.Meta.labels)

    def test_WebProcessingServiceForm(self):
        mock_args = mock.MagicMock()
        expected_fields = ('name', 'endpoint', 'public_endpoint', 'username', 'password')

        ret = WebProcessingServiceForm(mock_args)
        self.assertEquals(WebProcessingService, ret.Meta.model)
        self.assertEquals(expected_fields, ret.Meta.fields)
        self.assertTrue('password' in ret.Meta.widgets)
        self.assertEquals(self.expected_labels, ret.Meta.labels)

    def test_PersistentStoreServiceForm(self):
        mock_args = mock.MagicMock()
        expected_fields = ('name', 'engine', 'host', 'port', 'username', 'password')

        ret = PersistentStoreServiceForm(mock_args)
        self.assertEquals(PersistentStoreService, ret.Meta.model)
        self.assertEquals(expected_fields, ret.Meta.fields)
        self.assertTrue('password' in ret.Meta.widgets)

    def test_DatasetServiceAdmin(self):
        mock_args = mock.MagicMock()
        expected_fields = ('name', 'engine', 'endpoint', 'public_endpoint', 'apikey', 'username', 'password')

        ret = DatasetServiceAdmin(mock_args, mock_args)
        self.assertEquals(DatasetServiceForm, ret.form)
        self.assertEquals(expected_fields, ret.fields)

    def test_SpatialDatasetServiceAdmin(self):
        mock_args = mock.MagicMock()
        expected_fields = ('name', 'engine', 'endpoint', 'public_endpoint', 'apikey', 'username', 'password')

        ret = SpatialDatasetServiceAdmin(mock_args, mock_args)
        self.assertEquals(SpatialDatasetServiceForm, ret.form)
        self.assertEquals(expected_fields, ret.fields)

    def test_WebProcessingServiceAdmin(self):
        mock_args = mock.MagicMock()
        expected_fields = ('name', 'endpoint', 'public_endpoint', 'username', 'password')

        ret = WebProcessingServiceAdmin(mock_args, mock_args)
        self.assertEquals(WebProcessingServiceForm, ret.form)
        self.assertEquals(expected_fields, ret.fields)

    def test_PersistentStoreServiceAdmin(self):
        mock_args = mock.MagicMock()
        expected_fields = ('name', 'engine', 'host', 'port', 'username', 'password')

        ret = PersistentStoreServiceAdmin(mock_args, mock_args)
        self.assertEquals(PersistentStoreServiceForm, ret.form)
        self.assertEquals(expected_fields, ret.fields)

    def test_admin_site_register(self):
        from django.contrib import admin
        registry = admin.site._registry
        self.assertIn(DatasetService, registry)
        self.assertIsInstance(registry[DatasetService], DatasetServiceAdmin)

        self.assertIn(SpatialDatasetService, registry)
        self.assertIsInstance(registry[SpatialDatasetService], SpatialDatasetServiceAdmin)

        self.assertIn(WebProcessingService, registry)
        self.assertIsInstance(registry[WebProcessingService], WebProcessingServiceAdmin)

        self.assertIn(PersistentStoreService, registry)
        self.assertIsInstance(registry[PersistentStoreService], PersistentStoreServiceAdmin)
