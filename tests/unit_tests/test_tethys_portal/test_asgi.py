from tethys_sdk.testing import TethysTestCase

import tethys_portal.asgi as asgi


class TestAsgiApplication(TethysTestCase):

    def set_up(self):
        pass

    def tear_down(self):
        pass

    def test_application(self):
        application = asgi.application
        self.assertIn('websocket', application.application_mapping)
        self.assertIn('http', application.application_mapping)
