from tethys_sdk.testing import TethysTestCase

from bokeh.server.django.consumers import SessionConsumer
from tethys_portal.consumers.bokeh_consumers import BokehAutoloadJsCDN


class TestConsumers(TethysTestCase):
    def test_bokeh_autoload_resources(self):
        res = BokehAutoloadJsCDN.resources(SessionConsumer)

        self.assertEqual('cdn', res.mode)
        self.assertIn('bokeh', res.js_components)
        self.assertIn('bokeh-widgets', res.js_components)
        self.assertIn('bokeh-tables', res.js_components)
        self.assertIn('bokeh-gl', res.js_components)
