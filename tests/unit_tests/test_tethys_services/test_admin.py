import unittest
from unittest import mock

from django.test.utils import override_settings
from django.utils.translation import gettext_lazy as _
from tethys_services.models import (
    DatasetService,
    SpatialDatasetService,
    WebProcessingService,
    PostgresPersistentStoreService,
    SecureMapService,
)
from tethys_services.admin import (
    DatasetServiceForm,
    SpatialDatasetServiceForm,
    WebProcessingServiceForm,
    PostgresPersistentStoreServiceForm,
    DatasetServiceAdmin,
    SpatialDatasetServiceAdmin,
    WebProcessingServiceAdmin,
    PostgresPersistentStoreServiceAdmin,
    SecureMapServiceForm,
)


class TestTethysServicesAdmin(unittest.TestCase):
    def setUp(self):
        self.expected_labels = {"public_endpoint": _("Public Endpoint")}

    def tearDown(self):
        pass

    def test_DatasetServiceForm(self):
        mock_args = mock.MagicMock()
        expected_fields = (
            "name",
            "engine",
            "endpoint",
            "public_endpoint",
            "apikey",
            "username",
            "password",
        )

        ret = DatasetServiceForm(mock_args)
        self.assertEqual(DatasetService, ret.Meta.model)
        self.assertEqual(expected_fields, ret.Meta.fields)
        self.assertTrue("password" in ret.Meta.widgets)
        self.assertEqual(self.expected_labels, ret.Meta.labels)

    def test_SpatialDatasetServiceForm(self):
        mock_args = mock.MagicMock()
        expected_fields = (
            "name",
            "engine",
            "endpoint",
            "public_endpoint",
            "apikey",
            "username",
            "password",
        )

        ret = SpatialDatasetServiceForm(mock_args)
        self.assertEqual(SpatialDatasetService, ret.Meta.model)
        self.assertEqual(expected_fields, ret.Meta.fields)
        self.assertTrue("password" in ret.Meta.widgets)
        self.assertEqual(self.expected_labels, ret.Meta.labels)

    def test_WebProcessingServiceForm(self):
        mock_args = mock.MagicMock()
        expected_fields = (
            "name",
            "endpoint",
            "public_endpoint",
            "username",
            "password",
        )

        ret = WebProcessingServiceForm(mock_args)
        self.assertEqual(WebProcessingService, ret.Meta.model)
        self.assertEqual(expected_fields, ret.Meta.fields)
        self.assertTrue("password" in ret.Meta.widgets)
        self.assertEqual(self.expected_labels, ret.Meta.labels)

    def test_PostgresPersistentStoreServiceForm(self):
        mock_args = mock.MagicMock()
        expected_fields = ("name", "engine", "host", "port", "username", "password")

        ret = PostgresPersistentStoreServiceForm(mock_args)
        self.assertEqual(PostgresPersistentStoreService, ret.Meta.model)
        self.assertEqual(expected_fields, ret.Meta.fields)
        self.assertTrue("password" in ret.Meta.widgets)

    @override_settings(AUTHENTICATION_BACKENDS=[])
    def test_SecureMapServiceForm_no_authentication_backends(self):
        mock_args = mock.MagicMock()

        ret = SecureMapServiceForm(mock_args)
        self.assertEqual(SecureMapService, ret.Meta.model)
        self.assertEqual("__all__", ret.Meta.fields)
        self.assertTrue("api_key" in ret.Meta.widgets)

        oauth_provider_field = ret.fields.get("oauth_provider")
        self.assertEqual([], oauth_provider_field.choices)

    @override_settings(AUTHENTICATION_BACKENDS=["this_is_a_backend"])
    @mock.patch("tethys_services.admin.import_string")
    def test_SecureMapServiceForm_with_authentication_backends_no_name(self, mock_is):
        mock_args = mock.MagicMock()
        # Mock an object without a name attribute
        mock_is.return_value = object()

        ret = SecureMapServiceForm(mock_args)
        self.assertEqual(SecureMapService, ret.Meta.model)
        self.assertEqual("__all__", ret.Meta.fields)
        self.assertTrue("api_key" in ret.Meta.widgets)

        oauth_provider_field = ret.fields.get("oauth_provider")
        self.assertEqual([], oauth_provider_field.choices)

    @override_settings(AUTHENTICATION_BACKENDS=["this_is_a_backend"])
    @mock.patch("tethys_services.admin.import_string")
    def test_SecureMapServiceForm_with_authentication_backends(self, mock_is):
        mock_args = mock.MagicMock()
        mock_is.return_value = mock.MagicMock()
        mock_is.return_value.name = "fake_backend_name"

        ret = SecureMapServiceForm(mock_args)
        self.assertEqual(SecureMapService, ret.Meta.model)
        self.assertEqual("__all__", ret.Meta.fields)
        self.assertTrue("api_key" in ret.Meta.widgets)

        oauth_provider_field = ret.fields.get("oauth_provider")
        self.assertEqual(
            [("fake_backend_name", "fake_backend_name")], oauth_provider_field.choices
        )

    def test_DatasetServiceAdmin(self):
        mock_args = mock.MagicMock()
        expected_fields = (
            "name",
            "engine",
            "endpoint",
            "public_endpoint",
            "apikey",
            "username",
            "password",
        )

        ret = DatasetServiceAdmin(mock_args, mock_args)
        self.assertEqual(DatasetServiceForm, ret.form)
        self.assertEqual(expected_fields, ret.fields)

    def test_SpatialDatasetServiceAdmin(self):
        mock_args = mock.MagicMock()
        expected_fields = (
            "name",
            "engine",
            "endpoint",
            "public_endpoint",
            "apikey",
            "username",
            "password",
        )

        ret = SpatialDatasetServiceAdmin(mock_args, mock_args)
        self.assertEqual(SpatialDatasetServiceForm, ret.form)
        self.assertEqual(expected_fields, ret.fields)

    def test_WebProcessingServiceAdmin(self):
        mock_args = mock.MagicMock()
        expected_fields = (
            "name",
            "endpoint",
            "public_endpoint",
            "username",
            "password",
        )

        ret = WebProcessingServiceAdmin(mock_args, mock_args)
        self.assertEqual(WebProcessingServiceForm, ret.form)
        self.assertEqual(expected_fields, ret.fields)

    def test_PostgresPersistentStoreServiceAdmin(self):
        mock_args = mock.MagicMock()
        expected_fields = ("name", "engine", "host", "port", "username", "password")

        ret = PostgresPersistentStoreServiceAdmin(mock_args, mock_args)
        self.assertEqual(PostgresPersistentStoreServiceForm, ret.form)
        self.assertEqual(expected_fields, ret.fields)

    def test_admin_site_register(self):
        from django.contrib import admin

        registry = admin.site._registry
        self.assertIn(DatasetService, registry)
        self.assertIsInstance(registry[DatasetService], DatasetServiceAdmin)

        self.assertIn(SpatialDatasetService, registry)
        self.assertIsInstance(
            registry[SpatialDatasetService], SpatialDatasetServiceAdmin
        )

        self.assertIn(WebProcessingService, registry)
        self.assertIsInstance(registry[WebProcessingService], WebProcessingServiceAdmin)

        self.assertIn(PostgresPersistentStoreService, registry)
        self.assertIsInstance(
            registry[PostgresPersistentStoreService],
            PostgresPersistentStoreServiceAdmin,
        )
