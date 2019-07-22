from tethys_sdk.testing import TethysTestCase
import tethys_services.models as service_model


class ThreddsServiceTests(TethysTestCase):
    def set_up(self):
        pass

    def tear_down(self):
        pass

    def test__str__(self):
        sds = service_model.ThreddsService(
            name='test_ts',
        )
        self.assertEqual('test_ts', sds.__str__())

    def test_get_wms_url(self):
        ts = service_model.ThreddsService(
            name='test_sds',
            wms_endpoint='http://localhost/thredds/wms/'
        )
        ts.save()

        # Check result
        self.assertEqual('http://localhost/thredds/wms/', ts.get_url())
