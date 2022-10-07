from unittest import mock
from django.http import HttpResponse
from django.test import RequestFactory, TestCase, override_settings

from tethys_layouts.views.tethys_layout import TethysLayout


class MethodLayout(TethysLayout):
    def some_method(self, request, *args, **kwargs):
        return "some-response"


class TestTethysLayout(TestCase):
    def setUp(self):
        self.inst = TethysLayout()
        self.factory = RequestFactory()

    def tearDown(self):
        pass

    def test_default_props(self):
        ret = TethysLayout()
        self.assertEqual("", ret.template_name)
        self.assertIsNone(ret.app)
        self.assertIsNone(ret.back_url)
        self.assertEqual("tethys_layouts/tethys_layout.html", ret.base_template)
        self.assertEqual("", ret.layout_title)
        self.assertEqual("", ret.layout_subtitle)

    @mock.patch("tethys_layouts.views.tethys_layout.render")
    @override_settings(
        DEBUG=False,
        ENABLE_OPEN_PORTAL=True,
    )
    def test_get(self, mock_render):
        class CustomLayout(TethysLayout):
            base_template = "bar.html"
            template_name = "foo.html"
            back_url = "/a/back/url"
            layout_title = "Foo"
            layout_subtitle = "Bar"

            def get_context(self, request, context, *args, **kwargs):
                context["bar"] = "baz"
                return context

            def get_permissions(self, request, permissions, *args, **kwargs):
                permissions["can_do_the_thing"] = True
                return permissions

        request = self.factory.get("/some/endpoint")
        mock_render.return_value = "render-response"
        controller = CustomLayout.as_controller()
        ret = controller(request)
        self.assertEqual(ret, "render-response")
        expected_context = {
            "base_template": "bar.html",
            "back_url": "/a/back/url",
            "is_in_debug": False,
            "nav_title": "Foo",
            "nav_subtitle": "Bar",
            "open_portal_mode": True,
            "bar": "baz",
            "can_do_the_thing": True,
        }
        mock_render.assert_called_with(request, "foo.html", expected_context)

    def test_get_on_get_http_response(self):
        class OnGetLayout(TethysLayout):
            def on_get(self, request, *args, **kwargs):
                return HttpResponse("on-get-response")

        request = self.factory.get("/some/endpoint")
        controller = OnGetLayout.as_controller()
        ret = controller(request)
        self.assertEqual(ret.content, b"on-get-response")

    def test_get_with_method(self):
        request = self.factory.get("/some/endpoint", data={"method": "some-method"})
        controller = MethodLayout().as_controller()
        ret = controller(request)
        self.assertEqual(ret, "some-response")

    def test_post_no_method(self):
        request = self.factory.post("/some/endpoint")
        controller = MethodLayout().as_controller()
        ret = controller(request)
        self.assertEqual(ret.status_code, 404)

    def test_post_with_method(self):
        request = self.factory.post("/some/endpoint", data={"method": "some-method"})
        controller = MethodLayout().as_controller()
        ret = controller(request)
        self.assertEqual(ret, "some-response")

    def test_request_to_method_get_with_dashes(self):
        request = self.factory.get("/some/endpoint", data={"method": "some-method"})
        inst = MethodLayout()
        ret = inst.request_to_method(request)
        self.assertEqual(ret, inst.some_method)

    def test_request_to_method_post_with_underscores(self):
        request = self.factory.post("/some/endpoint", data={"method": "some_method"})
        inst = MethodLayout()
        ret = inst.request_to_method(request)
        self.assertEqual(ret, inst.some_method)

    def test_request_to_method_put(self):
        request = self.factory.put("/some/endpoint", data={"method": "some-method"})
        inst = MethodLayout()
        ret = inst.request_to_method(request)
        self.assertIsNone(ret)

    def test_request_to_method_no_request_method(self):
        request = self.factory.get("/some/endpoint", data={"method": "not-a-method"})
        inst = MethodLayout()
        ret = inst.request_to_method(request)
        self.assertIsNone(ret)

    def test_on_get(self):
        mock_request = mock.MagicMock()
        ret = self.inst.on_get(mock_request)
        self.assertIsNone(ret)

    def test_get_permissions(self):
        test_perms = dict(foo=True)
        mock_request = mock.MagicMock()
        ret = self.inst.get_permissions(mock_request, test_perms)
        self.assertIs(test_perms, ret)

    def test_get_context(self):
        test_context = dict(foo="bar")
        mock_request = mock.MagicMock()
        ret = self.inst.get_context(mock_request, test_context)
        self.assertIs(test_context, ret)
