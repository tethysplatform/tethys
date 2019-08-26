# import os
# import json
# import asyncio
#
# from tethys_sdk.testing import TethysTestCase
# from channels.testing import WebsocketCommunicator
# from bokeh.server.django.consumers import SessionConsumer
# from tethys_portal.consumers.bokeh_consumers import BokehAutoloadJsCDN
#
# from bokeh.server.django import autoload
# from tethysapp.test_app.controllers import home_handler
#
# from unittest import mock
#
#
# class TestBokehAutoloadJsCDN(TethysTestCase):
#     @mock.patch('bokeh.server.django.consumers.SessionConsumer', spec=SessionConsumer)
#     def test_bokeh_autoload_js_cdn(self, _):
#         event_loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(event_loop)
#
#         bokeh_app = autoload("/apps/test-app", home_handler)
#         # mock_kwargs = mock.MagicMock(return_value=dict(app_context=bokeh_app.app_context))
#
#         async def run_test():
#             communicator = WebsocketCommunicator(BokehAutoloadJsCDN, "/apps/test-app/autoload.js",
#                                                  headers=[(b'bokeh-autoload-element', b'1075'),
#                                                           (b'bokeh-app-path', b'/apps/test-app&bokeh-absolute-url'),
#                                                           (b'http://localhost:8000/apps/test-app')])
#             connected, subprotocol = await communicator.connect()
#
#             # Test connection
#             self.assertTrue(connected)
#
#             # Test sending and receiving messages
#             await communicator.send_to(text_data=json.dumps({'msgid': "1"}))
#             response = await communicator.receive_from()
#             self.assertEqual(json.loads(response)["server_message"], "This is a consumer test")
#
#             # Close
#             await communicator.disconnect()
#
#         # Run the async test
#         coroutine = asyncio.coroutine(run_test)
#         event_loop.run_until_complete(coroutine())
#         event_loop.close()
