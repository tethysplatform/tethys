import datetime
import threading

import json
import asyncio
import logging
from urllib.parse import urlparse, parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.http import AsyncHttpConsumer

from bokeh.embed.server import server_html_page_for_session
from bokeh.resources import Resources
from bokeh.server.views.static_handler import StaticHandler
from bokeh.server.protocol_handler import ProtocolHandler
from bokeh.protocol import Protocol
from bokeh.protocol.receiver import Receiver
from bokeh.util.session_id import generate_session_id, check_session_id_signature

from tornado.platform.asyncio import AsyncIOMainLoop
from tornado import locks

from tethys_apps.jupyterapp.patched_bokeh import PatchedServerConnection


log = logging.getLogger(__name__)


class BasicHttpConsumer(AsyncHttpConsumer):

    # How to test this async endpoint
    # Open 2 blank browser tabs, run the two urls at the same time
    # See: https://www.tornadoweb.org/en/stable/faq.html#my-code-is-asynchronous-but-it-s-not-running-in-parallel-in-two-browser-tabs
    # http://127.0.0.1:8000/asynchttp?x=1
    # http://127.0.0.1:8000/asynchttp?a=2
    # check the 2 "t_start" values, the difference of which should be less than 1 second
    # check the 2 "t_end" values, each of which should be +5 second from "t_start"
    # check the 2 "thread_name" values that should be identical
    async def handle(self, body):
        t_start = datetime.datetime.utcnow().strftime("%H:%M:%S")
        await asyncio.sleep(5)
        t_end = datetime.datetime.utcnow().strftime("%H:%M:%S")
        resp = dict(status="OK",
                    t_start=t_start,
                    t_end=t_end,
                    thread_name=threading.current_thread().name)

        await self.send_response(200, json.dumps(resp).encode(),
                                 headers=[(b"Content-Type", b"application/json"),])


class BokehAppHTTPConsumer(AsyncHttpConsumer):

    def __init__(self, scope):
        super(BokehAppHTTPConsumer, self).__init__(scope)

        kwargs = self.scope['url_route']["kwargs"]
        self.application_context = kwargs["application_context"]
        # self.application_context._loop = asyncio.get_event_loop()
        # should use Torado wrapper for asyncio.get_event_loop()

        event_loop = AsyncIOMainLoop()
        event_loop.initialize()
        self.application_context._loop = event_loop
        self.bokeh_websocket_path = kwargs["bokeh_websocket_path"]

    async def _get_session(self):
        #session_id = self.get_argument("bokeh-session-id", default=None)
        session_id = None
        if session_id is None:
            if True:
                session_id = generate_session_id(secret_key=None,
                                                 signed=False)
            else:
                log.debug("Server configured not to generate session IDs and none was provided")
                raise Exception(status_code=403, reason="No bokeh-session-id provided")
        elif not check_session_id_signature(session_id,
                                            secret_key=self.application.secret_key,
                                            signed=self.application.sign_sessions):
            log.error("Session id had invalid signature: %r", session_id)
            raise Exception(status_code=403, reason="Invalid session ID")
        self.arguments = {}
        self.request = self

        session = await self.application_context.create_session_if_needed(session_id, self.request)

        return session

    async def handle(self, body):

        scope = self.scope
        session = await self._get_session()
        res = Resources(mode="server", root_url="/", path_versioner=StaticHandler.append_version)
        import threading
        page = server_html_page_for_session(session,
                                            resources=res,
                                            # title=session.document.title,
                                            title=str(session._id) + threading.current_thread().name,
                                            template=session.document.template,
                                            template_variables=session.document.template_variables)

        await self.send_response(200, page.encode(), headers=[
            (b"Content-Type", b"text/html"),
        ])


class BokehAppWebsocketConsumer(AsyncWebsocketConsumer):

    def __init__(self, scope):
        super(BokehAppWebsocketConsumer, self).__init__(scope)

        kwargs = self.scope['url_route']["kwargs"]
        self.application_context = kwargs["application_context"]
        self.application_context._loop = asyncio.get_event_loop()
        self.bokeh_websocket_path = kwargs["bokeh_websocket_path"]
        self._clients = set()
        self.lock = locks.Lock()

    async def connect(self):
        log.info('WebSocket connection opened')

        parsed_url = urlparse("/?" + self.scope["query_string"].decode())
        qs_dict = parse_qs(parsed_url.query)
        proto_version = qs_dict.get("bokeh-protocol-version", [None])[0]
        if proto_version is None:
            self.close()
            raise Exception("No bokeh-protocol-version specified")

        session_id = qs_dict.get("bokeh-session-id", [None])[0]
        if session_id is None:
            self.close()
            raise Exception("No bokeh-session-id specified")

        if not check_session_id_signature(session_id,
                                          signed=False,
                                          secret_key=None):
            log.error("Session id had invalid signature: %r", session_id)
            raise Exception("Invalid session ID")

        def on_fully_opened(future):
            e = future.exception()
            if e is not None:
                # this isn't really an error (unless we have a
                # bug), it just means a client disconnected
                # immediately, most likely.
                log.debug("Failed to fully open connlocksection %r", e)

        future = self._async_open(session_id, proto_version)

        #self.application.io_loop.add_future(future, on_fully_opened)

        # rewrite above line using asyncio
        # this task is scheduled to run soon once context is back to event loop
        task = asyncio.ensure_future(future)
        task.add_done_callback(on_fully_opened)
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        fragment = text_data

        message = await self.receiver.consume(fragment)
        if message:
            work = await self.handler.handle(message, self.connection)
            if work:
                await self._send_bokeh_message(work)
        else:
            return None

    async def _async_open(self, session_id, proto_version):

        try:
            self.arguments = {}
            self.request = self
            await self.application_context.create_session_if_needed(session_id, self.request)
            session = self.application_context.get_session(session_id)

            protocol = Protocol(proto_version)
            self.receiver = Receiver(protocol)
            log.debug("Receiver created for %r", protocol)

            self.handler = ProtocolHandler()
            log.debug("ProtocolHandler created for %r", protocol)

            self.connection = self._new_connection(protocol, self, self.application_context, session)
            log.info("ServerConnection created")

        except Exception as e:
            log.error("Could not create new server session, reason: %s", e)
            self.close()
            raise e

        msg = self.connection.protocol.create('ACK')
        await self._send_bokeh_message(msg)
        return None

    async def _send_bokeh_message(self, message):
        sent = 0
        try:
            async with self.lock:

                await self.send(text_data=message.header_json)
                sent += len(message.header_json)

                await self.send(text_data=message.metadata_json)
                sent += len(message.metadata_json)

                await self.send(text_data=message.content_json)
                sent += len(message.content_json)

                for header, payload in message._buffers:
                    await self.send(text_data=json.dumps(header))
                    await self.send(bytes_data=payload)
                    sent += (len(header) + len(payload))

        except Exception as e:  # Tornado 4.x may raise StreamClosedError
            # on_close() is / will be called anyway
            log.warn("Failed sending message as connection was closed")
        return sent

    def _new_connection(self, protocol, socket, application_context, session):
        connection = PatchedServerConnection(protocol, socket, application_context, session)
        self._clients.add(connection)
        return connection
