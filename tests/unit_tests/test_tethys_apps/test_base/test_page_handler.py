import sys
from unittest import TestCase, mock
from importlib import reload

from tethys_apps.base import page_handler
import tethys_apps.base.controller as tethys_controller


class TestPageHandler(TestCase):
    @mock.patch("tethys_apps.base.page_handler.render")
    @mock.patch("tethys_apps.base.page_handler.ComponentLibrary")
    @mock.patch("tethys_apps.base.page_handler._get_layout_component")
    def test_global_page_controller(self, mock_get_layout, mock_lib, mock_render):
        # FUNCTION ARGS
        request = mock.MagicMock()
        mock_app = mock.MagicMock()
        layout = "test_layout"
        component_func = mock.MagicMock()
        component_source_code = "test123"
        title = "test_title"
        custom_css = ["custom.css"]
        custom_js = ["custom.js"]

        # MOCK INTERNALS
        component_func.__name__ = "my_mock_component_func"
        expected_return_value = "Expected return value"
        mock_render.return_value = expected_return_value
        mock_get_layout.return_value = "my_layout_func"

        # EXECUTE FUNCTION
        response = page_handler.global_page_controller(
            request=request,
            app=mock_app,
            layout=layout,
            component_func=component_func,
            component_source_code=component_source_code,
            title=title,
            custom_css=custom_css,
            custom_js=custom_js,
        )

        # EVALUATE EXECUTION
        mock_get_layout.assert_called_once_with(mock_app, layout)
        render_called_with_args = mock_render.call_args.args
        self.assertEqual(render_called_with_args[0], request)
        self.assertEqual(render_called_with_args[1], "tethys_apps/component_base.html")
        render_context = render_called_with_args[2]
        self.assertListEqual(
            list(render_context.keys()),
            [
                "app",
                "layout_func",
                "component_func",
                "reactjs_version",
                "reactjs_version_int",
                "title",
                "custom_css",
                "custom_js",
                "extras",
            ],
        )
        self.assertEqual(render_context["app"], mock_app)
        self.assertEqual(render_context["layout_func"](), "my_layout_func")
        self.assertEqual(render_context["component_func"](), component_func)
        self.assertEqual(render_context["reactjs_version"], mock_lib.REACTJS_VERSION)
        self.assertEqual(
            render_context["reactjs_version_int"], mock_lib.REACTJS_VERSION_INT
        )
        self.assertEqual(render_context["title"], title)
        self.assertEqual(render_context["custom_css"], custom_css)
        self.assertEqual(render_context["custom_js"], custom_js)
        self.assertEqual(response, expected_return_value)


class TestPageComponentWrapper(TestCase):

    @classmethod
    def setUpClass(cls):
        mock_has_module = mock.patch("tethys_portal.optional_dependencies.has_module")
        mock_has_module.return_value = True
        mock_has_module.start()
        mock_reactpy = mock.MagicMock()
        sys.modules["reactpy"] = mock_reactpy
        mock_reactpy.component = lambda x: x
        reload(page_handler)

    @classmethod
    def tearDownClass(cls):
        mock.patch.stopall()
        del sys.modules["reactpy"]
        reload(page_handler)

    @mock.patch("tethys_apps.base.page_handler.PageLoader")
    @mock.patch("tethys_apps.base.page_handler.ComponentLibraryManager")
    def test_page_component_wrapper__layout_none(self, mock_clm, mock_pl):
        mock_lib = mock.MagicMock()
        mock_clm.get_library.return_value = mock_lib
        mock_pl.return_value = "rendered_page"
        # FUNCTION ARGS
        app = mock.MagicMock(package="test_app")
        user = mock.MagicMock()
        layout = None
        proof_mock = mock.MagicMock()

        def component(lib):
            proof_mock(lib)
            return "rendered_component"

        return_value = page_handler.page_component_wrapper(app, user, layout, component)

        self.assertEqual(return_value, "rendered_page")
        mock_clm.get_library.assert_called_once_with("test_app-component")
        mock_pl.assert_called_once_with(mock_lib, content="rendered_component")
        proof_mock.assert_called_once_with(mock_lib)

    @mock.patch("tethys_apps.base.page_handler.PageLoader")
    @mock.patch("tethys_apps.base.page_handler.ComponentLibraryManager")
    def test_page_component_wrapper__layout_none_with_extras(self, mock_clm, mock_pl):
        mock_lib = mock.MagicMock()
        mock_clm.get_library.return_value = mock_lib
        mock_pl.return_value = "rendered_page"
        # FUNCTION ARGS
        mock_app = mock.MagicMock(package="test_app")
        mock_user = mock.MagicMock()
        layout = None
        extras = {"extra1": "val1", "extra2": 2}
        proof_mock = mock.MagicMock()

        def component(lib, extra1, extra2):
            proof_mock(lib, extra1, extra2)
            return "rendered_component"

        return_value = page_handler.page_component_wrapper(
            mock_app, mock_user, layout, component, extras
        )

        self.assertEqual(return_value, mock_pl.return_value)
        proof_mock.assert_called_once_with(mock_lib, "val1", 2)
        mock_clm.get_library.assert_called_once_with("test_app-component")
        mock_pl.assert_called_once_with(mock_lib, content="rendered_component")

    @mock.patch("tethys_apps.base.page_handler.PageLoader")
    @mock.patch("tethys_apps.base.page_handler.ComponentLibraryManager")
    def test_page_component_wrapper__layout_not_none(self, mock_clm, mock_pl):
        mock_lib = mock.MagicMock()
        mock_clm.get_library.return_value = mock_lib
        mock_pl.return_value = "rendered_page"
        # FUNCTION ARGS
        mock_app = mock.MagicMock(package="test_app")
        mock_app.registered_url_maps = []
        mock_user = mock.MagicMock()
        layout = mock.MagicMock()
        layout_return_val = "returned_layout"
        layout.return_value = layout_return_val
        proof_mock = mock.MagicMock()

        def component(lib):
            proof_mock(lib)
            return "rendered_component"

        return_value = page_handler.page_component_wrapper(
            mock_app, mock_user, layout, component
        )

        self.assertEqual(return_value, layout_return_val)
        layout.assert_called_once_with(
            mock_lib,
            app=mock_app,
            user=mock_user,
            nav_links=mock_app.navigation_links,
            content=mock_pl.return_value,
        )
        proof_mock.assert_called_once_with(mock_lib)
        mock_clm.get_library.assert_called_once_with("test_app-component")
        mock_pl.assert_called_once_with(mock_lib, content="rendered_component")

    @mock.patch("tethys_apps.base.page_handler.PageLoader")
    @mock.patch("tethys_apps.base.page_handler.ComponentLibraryManager")
    def test_page_component_wrapper__layout_not_none_with_extras(
        self, mock_clm, mock_pl
    ):
        mock_lib = mock.MagicMock()
        mock_clm.get_library.return_value = mock_lib
        mock_pl.return_value = "rendered_page"
        # FUNCTION ARGS
        mock_app = mock.MagicMock(package="test_app")
        mock_app.registered_url_maps = []
        mock_user = mock.MagicMock()
        layout = mock.MagicMock()
        layout_return_val = "returned_layout"
        layout.return_value = layout_return_val
        extras = {"extra1": "val1", "extra2": 2}
        component_return_val = "rendered_component"
        proof_mock = mock.MagicMock()

        def component(lib, extra1, extra2):
            proof_mock(lib, extra1, extra2)
            return component_return_val

        return_value = page_handler.page_component_wrapper(
            mock_app, mock_user, layout, component, extras
        )

        self.assertEqual(return_value, layout_return_val)
        layout.assert_called_once_with(
            mock_lib,
            app=mock_app,
            user=mock_user,
            nav_links=mock_app.navigation_links,
            content=mock_pl.return_value,
        )
        proof_mock.assert_called_once_with(mock_lib, "val1", 2)
        mock_clm.get_library.assert_called_once_with("test_app-component")
        mock_pl.assert_called_once_with(mock_lib, content="rendered_component")


class TestPage(TestCase):
    @mock.patch("tethys_apps.base.controller._process_url_kwargs")
    @mock.patch("tethys_apps.base.controller.global_page_controller")
    @mock.patch("tethys_apps.base.controller.permission_required")
    @mock.patch("tethys_apps.base.controller.enforce_quota")
    @mock.patch("tethys_apps.base.controller.ensure_oauth2")
    @mock.patch("tethys_apps.base.controller.login_required_decorator")
    @mock.patch("tethys_apps.base.controller._get_url_map_kwargs_list")
    def test_page_with_permissions(
        self,
        mock_get_url_map_kwargs_list,
        mock_login_required_decorator,
        mock_ensure_oauth2,
        mock_enforce_quota,
        mock_permission_required,
        mock_global_page_component,
        mock_process_kwargs,
    ):
        layout = "MyLayout"
        title = "My Cool Page"
        index = 0
        custom_css = ["custom.css"]
        custom_js = ["custom.js"]
        my_function = lambda x: x  # noqa E731

        return_value = tethys_controller.page(
            app=mock.MagicMock(),
            permissions_required=["test_permission"],
            enforce_quotas=["test_quota"],
            ensure_oauth2_provider=["test_oauth2_provider"],
            layout=layout,
            title=title,
            index=index,
            custom_css=custom_css,
            custom_js=custom_js,
        )(my_function)

        self.assertTrue(callable(return_value))
        mock_request = mock.MagicMock()
        mock_process_kwargs.assert_called_once()
        process_kwargs_args = mock_process_kwargs.call_args.args
        self.assertTrue(callable(process_kwargs_args[0]))
        self.assertEqual(
            process_kwargs_args[0](mock_request), mock_login_required_decorator()()()
        )
        mock_permission_required.assert_called_once()
        mock_enforce_quota.assert_called_once()
        mock_ensure_oauth2.assert_called_once()
        self.assertEqual(mock_login_required_decorator.call_count, 2)
        mock_get_url_map_kwargs_list.assert_called_once_with(
            function_or_class=my_function,
            name=None,
            url=None,
            protocol="http",
            regex=None,
            title=title,
            index=index,
            for_page=True,
        )

    def test_page_raises_error_if_not_called_with_app(self):
        self.assertRaises(ValueError, tethys_controller.page)

    @mock.patch("tethys_apps.base.controller._process_url_kwargs")
    @mock.patch("tethys_apps.base.controller.global_page_controller")
    @mock.patch("tethys_apps.base.controller._get_url_map_kwargs_list")
    def test_page_with_defaults(
        self,
        mock_get_url_map_kwargs_list,
        mock_global_page_component,
        mock_process_kwargs,
    ):
        my_function = lambda x: x  # noqa: E731
        return_value = tethys_controller.page(app=mock.MagicMock())(my_function)
        self.assertTrue(callable(return_value))
        mock_request = mock.MagicMock()
        mock_process_kwargs.assert_called_once()
        process_kwargs_args = mock_process_kwargs.call_args.args
        self.assertTrue(callable(process_kwargs_args[0]))
        self.assertEqual(
            process_kwargs_args[0](mock_request),
            mock_global_page_component(
                mock_request,
                layout="default",
                component_func=my_function,
                component_source_code="lambda x: x",
                title=mock_get_url_map_kwargs_list[0]["title"],
                custom_css=[],
                custom_js=[],
            ),
        )
        mock_get_url_map_kwargs_list.assert_called_once_with(
            function_or_class=my_function,
            name=None,
            url=None,
            protocol="http",
            regex=None,
            title=None,
            index=None,
            for_page=True,
        )

    @mock.patch("tethys_apps.base.controller._process_url_kwargs")
    @mock.patch("tethys_apps.base.controller.global_page_controller")
    @mock.patch("tethys_apps.base.controller._get_url_map_kwargs_list")
    def test_page_with_handler(
        self,
        mock_get_url_map_kwargs_list,
        mock_global_page_component,
        mock_process_kwargs,
    ):
        component_function = lambda x: x  # noqa: E731
        handler_function = mock.MagicMock()
        return_value = tethys_controller.page(
            app=mock.MagicMock(), handler=handler_function
        )(component_function)
        self.assertTrue(callable(return_value))
        mock_request = mock.MagicMock()
        mock_process_kwargs.assert_called_once()
        process_kwargs_args = mock_process_kwargs.call_args.args
        self.assertTrue(callable(process_kwargs_args[0]))
        mock_global_page_component.assert_not_called()
        self.assertEqual(
            process_kwargs_args[0](mock_request),
            handler_function(
                mock_request,
                layout="default",
                component_func=component_function,
                component_source_code="lambda x: x",
                title=mock_get_url_map_kwargs_list[0]["title"],
                custom_css=[],
                custom_js=[],
            ),
        )
        mock_get_url_map_kwargs_list.assert_called_once_with(
            function_or_class=component_function,
            name=None,
            url=None,
            protocol="http",
            regex=None,
            title=None,
            index=None,
            for_page=True,
        )

    def test_page(self):
        tethys_controller.app_controllers_list = list()

        @tethys_controller.page(app=mock.MagicMock())
        def my_page(lib):
            pass

        kwargs = tethys_controller.app_controllers_list.pop(0)
        name = my_page.__name__
        self.assertEqual(name, kwargs["name"])
        url = f'test-page-handler/{name.replace("_", "-")}/'
        self.assertEqual(url, kwargs["url"])
