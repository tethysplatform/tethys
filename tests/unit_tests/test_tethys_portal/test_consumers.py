import asyncio
import asynctest
from unittest import mock
from tethys_sdk.testing import TethysTestCase

from bokeh.server.django import autoload
from bokeh.server.django.consumers import SessionConsumer, ConsumerHelper
from tethys_portal.consumers.bokeh_consumers import BokehAutoloadJsCDN
from tethysapp.test_app.controllers import home_handler


class BokehAutoloadJsCDNTests(TethysTestCase):
    def set_up(self):
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)
        self.addCleanup(self.event_loop.close)
        self.bokeh_app = autoload('apps/test-app', home_handler)
        self.kwargs = dict(app_context=self.bokeh_app.app_context)
        self.scope = {
            'url_route': {
                'kwargs': self.kwargs,
            },
            'headers': [
                (b"Access-Control-Allow-Headers", b"*"),
                (b"Access-Control-Allow-Methods", b"PUT, GET, OPTIONS"),
                (b"Access-Control-Allow-Origin", b"*"),
                (b"Content-Type", b"application/javascript")
            ],
            'cookies': {},
            'query_string': b'bokeh-autoload-element=1234&'
                            b'bokeh-app-path=/apps/test-app&'
                            b'bokeh-absolute-url=http://localhost:8000/apps/test-app'
        }
        self.body = b''

        self.consumer = BokehAutoloadJsCDN(self.scope)
        self.consumer.send_response = asynctest.CoroutineMock()

    def test_resources(self):
        res = BokehAutoloadJsCDN.resources(SessionConsumer)

        self.assertEqual('cdn', res.mode)
        self.assertIn('bokeh', res.js_components)
        self.assertIn('bokeh-widgets', res.js_components)
        self.assertIn('bokeh-tables', res.js_components)
        self.assertIn('bokeh-gl', res.js_components)

    def test_handle(self):
        self.event_loop.run_until_complete(self.consumer.handle(self.body))
        self.consumer.send_response.assert_awaited_once()
        aal = self.consumer.send_response.await_args_list
        self.assertEqual(200, aal[0][0][0])
        self.assertIn(b'js_urls', aal[0][0][1])
        self.assertIn(b'bokeh', aal[0][0][1])
        self.assertIn(b'bokeh-widgets', aal[0][0][1])
        self.assertIn(b'bokeh-tables', aal[0][0][1])
        self.assertIn(b'bokeh-gl', aal[0][0][1])
        self.assertIn(b'"elementid":"1234"', aal[0][0][1])
        self.assertIn(b'root.Bokeh.embed.embed_items(docs_json, render_items, "/apps/test-app", '
                      b'"http://localhost:8000/apps/test-app");', aal[0][0][1])
        self.assertEqual([(b"Access-Control-Allow-Headers", b"*"),
                          (b"Access-Control-Allow-Methods", b"PUT, GET, OPTIONS"),
                          (b"Access-Control-Allow-Origin", b"*"), (b"Content-Type", b"application/javascript")],
                         aal[0][1]['headers'])

    def test_handle_no_element_id(self):
        self.scope['query_string'] = b''

        with self.assertRaises(RuntimeError):
            self.event_loop.run_until_complete(self.consumer.handle(self.body))

    def test_handle_resources_param_none(self):
        side_effect = ['1234', '/apps/test-app', 'http://localhost:8000/apps/test-app', 'none']

        with mock.patch.object(ConsumerHelper, 'get_argument', side_effect=side_effect):
            self.event_loop.run_until_complete(self.consumer.handle(self.body))

            aal = self.consumer.send_response.await_args_list
            self.assertIn(b'var js_urls = []', aal[0][0][1])
            self.assertIn(b'css_urls = []', aal[0][0][1])
