"""
********************************************************************************
* Name: bokeh_consumers.py
* Author: Michael Souffront
* Created On: 2019
* Copyright: (c) Aquaveo, LLC 2019
* License: BSD 2-Clause
********************************************************************************
"""

from bokeh.server.django.consumers import SessionConsumer
from bokeh.resources import Resources
from bokeh.core.templates import AUTOLOAD_JS
from bokeh.util.compiler import bundle_all_models
from bokeh.embed.util import RenderItem
from bokeh.embed.elements import script_for_render_items

from typing import Optional, List


class BokehAutoloadJsCDN(SessionConsumer):
    def resources(self, version: Optional[str] = None) -> Resources:
        return Resources(mode='cdn', version=version)

    async def handle(self, body: bytes) -> None:
        session = await self._get_session()

        element_id = self.get_argument("bokeh-autoload-element", default=None)
        if not element_id:
            raise RuntimeError("No bokeh-autoload-element query parameter")

        app_path = self.get_argument("bokeh-app-path", default="/")
        absolute_url = self.get_argument("bokeh-absolute-url", default=None)

        resources = self.resources()

        bundle = bundle_all_models() or ""

        render_items = [RenderItem(sessionid=session.id, elementid=element_id, use_for_title=False)]
        script = script_for_render_items(None, render_items, app_path=app_path, absolute_url=absolute_url)

        resources_param = self.get_argument("resources", "default")
        js_urls: List[str]
        css_urls: List[str]
        if resources_param == "none":
            js_urls = []
            css_urls = []
        else:
            js_urls = resources.js_files
            css_urls = resources.css_files

        js = AUTOLOAD_JS.render(
            js_urls=js_urls,
            css_urls=css_urls,
            js_raw=resources.js_raw + [bundle, script],
            css_raw=resources.css_raw_str,
            elementid=element_id,
        )

        await self.send_response(200, js.encode(), headers=[(b"Content-Type", b"application/javascript")])
