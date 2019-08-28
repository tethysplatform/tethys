import asyncio
import os
import re

from django.conf.urls import url

from channels.testing import HttpCommunicator
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.http import AsgiHandler

from bokeh.server.django import autoload

from tethys_sdk.testing import TethysTestCase
from tethys_portal.consumers.bokeh_consumers import BokehAutoloadJsCDN

from tethysapp.test_app.controllers import home_handler


class TestBokehAutoloadJsCDN(TethysTestCase):
    def test_bokeh_autoload_js_cdn(self):
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)

        bokeh_app = autoload("/apps/test-app", home_handler)
        kwargs = dict(app_context=bokeh_app.app_context)

        application = ProtocolTypeRouter({
            'http': AuthMiddlewareStack(
                URLRouter([
                    url(os.path.join(re.escape(bokeh_app.url)) + '/autoload.js', BokehAutoloadJsCDN, kwargs=kwargs),
                    url(r'', AsgiHandler)
                ])
            ),
            # 'websocket': AuthMiddlewareStack(
            #     URLRouter([
            #         url(os.path.join(re.escape(bokeh_app.url)) + '/ws', BokehAutoloadJsCDN, kwargs=kwargs),
            #     ])
            # ),
        })

        async def run_test():
            communicator = HttpCommunicator(application, "GET", "/apps/test-app")
            response = await communicator.get_response()

            assert response['status'] == 200

        # Run the async test
        coroutine = asyncio.coroutine(run_test)
        event_loop.run_until_complete(coroutine())
        event_loop.close()
