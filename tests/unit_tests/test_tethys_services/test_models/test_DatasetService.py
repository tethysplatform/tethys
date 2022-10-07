from tethys_sdk.testing import TethysTestCase
import tethys_services.models as service_model
from django.core.exceptions import ObjectDoesNotExist
from social_core.exceptions import AuthException
from unittest import mock


class DatasetServiceTests(TethysTestCase):
    def set_up(self):
        pass

    def tear_down(self):
        pass

    def test_unicode(self):
        ds = service_model.DatasetService(
            name="test_ds",
        )

        self.assertEqual("test_ds", str(ds))

    @mock.patch("tethys_services.models.HydroShareDatasetEngine")
    def test_get_engine_hydroshare(self, mock_hsde):
        request = mock.MagicMock()
        ds = service_model.DatasetService(
            name="test_ds",
            engine="tethys_dataset_services.engines.HydroShareDatasetEngine",
            endpoint="http://localhost/api/3/action/",
            apikey="test_api",
            username="foo",
            password="password",
        )
        ds.save()
        ds.get_engine(request=request)
        mock_hsde.assert_called_with(
            apikey="test_api",
            endpoint="http://localhost/api/3/action/",
            password="password",
            username="foo",
        )

    @mock.patch("tethys_services.models.HydroShareDatasetEngine")
    def test_get_engine_hydroshare_error(self, _):
        user = mock.MagicMock()
        user.social_auth.get.side_effect = ObjectDoesNotExist
        request = mock.MagicMock(user=user)
        ds = service_model.DatasetService(
            name="test_ds",
            engine="tethys_dataset_services.engines.HydroShareDatasetEngine",
        )
        self.assertRaises(AuthException, ds.get_engine, request=request)

    @mock.patch("tethys_services.models.CkanDatasetEngine")
    def test_get_engine_ckan(self, mock_ckan):
        ds = service_model.DatasetService(
            name="test_ds",
            apikey="test_api",
            endpoint="http://localhost/api/3/action/",
            username="foo",
            password="password",
        )
        ds.save()
        ds.get_engine()
        mock_ckan.assert_called_with(
            apikey="test_api",
            endpoint="http://localhost/api/3/action/",
            password="password",
            username="foo",
        )
