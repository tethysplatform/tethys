import json
import asyncio
from os import environ

from tethys_sdk.testing import TethysTestCase
from channels.testing import WebsocketCommunicator

from django.conf import settings


class TestConsumer(TethysTestCase):
    def test_consumer(self):
        from tethysapp.test_app.controllers import TestWS

        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)

        async def run_test():
            environ.setdefault("DJANGO_SETTINGS_MODULE", "tethys_portal.settings")
            settings.CHANNEL_LAYERS = {}

            communicator = WebsocketCommunicator(
                TestWS.as_asgi(), "/ws/test-app/test-app-ws/"
            )
            connected, subprotocol = await communicator.connect()

            # Test connection
            self.assertTrue(connected)

            # Test sending and receiving messages
            await communicator.send_to(
                text_data=json.dumps({"client_message": "This is a consumer test"})
            )
            response = await communicator.receive_from()
            self.assertEqual(
                json.loads(response)["server_message"], "This is a consumer test"
            )

            # Close
            await communicator.disconnect()

        # Run the async test
        event_loop.run_until_complete(run_test())
        event_loop.close()
