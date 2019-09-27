from tethys_sdk.testing import TethysTestCase

import tethys_portal.routing as routing


class TestRoutings(TethysTestCase):

    def set_up(self):
        pass

    def tear_down(self):
        pass

    def test_routings(self):
        application = routing.application
        self.assertIn('websocket', application.application_mapping)
        self.assertIn('http', application.application_mapping)
