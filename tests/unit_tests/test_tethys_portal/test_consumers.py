# from django.conf.urls import url
#
# from channels.testing import HttpCommunicator
# from channels.routing import URLRouter
# from channels.http import AsgiHandler
#
# from bokeh.server.django import autoload
#
# from tethys_sdk.testing import TethysTestCase
# from tethys_portal.consumers.bokeh_consumers import BokehAutoloadJsCDN
#
# from tethysapp.test_app.controllers import home_handler
#
#
# class TestBokehAutoloadJsCDN(TethysTestCase):
#     def set_up(self):
#         bokeh_app = autoload("apps/test-app", home_handler)
#         kwargs = dict(app_context=bokeh_app.app_context)
#
#         self.application = URLRouter([
#             url('apps/test-app/autoload.js', BokehAutoloadJsCDN, kwargs=kwargs),
#             url(r'', AsgiHandler)
#         ])
#
#     def test_bokeh_autoload_js_cdn(self):
#         communicator = HttpCommunicator(self.application, "GET", "/apps/test-app/autoload.js/")
#         response = communicator.get_response()
#
#         assert response['status'] == 200
