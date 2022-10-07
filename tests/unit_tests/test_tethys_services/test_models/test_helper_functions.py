from tethys_sdk.testing import TethysTestCase
import tethys_services.models as service_model
from django.core.exceptions import ValidationError


class HelperFunctionTests(TethysTestCase):
    def set_up(self):
        pass

    def tear_down(self):
        pass

    def test_validate_url_valid(self):
        test_url = "http://"
        raised = False
        try:
            service_model.validate_url(test_url)
        except ValidationError:
            raised = True
        self.assertFalse(raised)

    def test_validate_url(self):
        test_url = "test_url"
        self.assertRaises(ValidationError, service_model.validate_url, test_url)

    def test_validate_dataset_service_endpoint(self):
        test_url = "http://test_url"
        self.assertRaises(
            ValidationError, service_model.validate_dataset_service_endpoint, test_url
        )

    def test_validate_spatial_dataset_service_endpoint(self):
        test_url = "test_url"  # Not HTTP
        self.assertRaises(
            ValidationError,
            service_model.validate_spatial_dataset_service_endpoint,
            test_url,
        )

    def test_validate_wps_service_endpoint(self):
        test_url = "http://test_url"
        self.assertRaises(
            ValidationError, service_model.validate_wps_service_endpoint, test_url
        )

    def test_validate_persistent_store_port(self):
        test_url = "800"
        self.assertRaises(
            ValidationError, service_model.validate_persistent_store_port, test_url
        )
