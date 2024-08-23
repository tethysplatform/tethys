import unittest
from unittest import mock

from tethys_apps.base import page_handler
from importlib import reload
import tethys_apps.base.controller as tethys_controller

class TestPageHandler(unittest.TestCase):
    def setUp(self) -> None:
        # Do cleanup first so it is ready if an exception is raised
        def kill_patches():  # Create a cleanup callback that undoes our patches
            mock.patch.stopall()  # Stops all patches started with start()
            reload(page_handler)  # Reload our UUT module which restores the original decorator
        self.addCleanup(kill_patches)  # We want to make sure this is run so we do this in addCleanup instead of tearDown
        
        # Now patch the decorator where the decorator is being imported from
        mock.patch('reactpy.component', lambda x: x).start()  # The lambda makes our decorator into a pass-thru. Also, don't forget to call start()          
        reload(page_handler)

    @mock.patch("tethys_apps.base.page_handler.render")
    @mock.patch("tethys_apps.base.page_handler.ComponentLibrary")
    @mock.patch("tethys_apps.base.page_handler.get_active_app")
    @mock.patch("tethys_apps.base.page_handler.get_layout_component")
    def test_global_page_component_controller(self, mock_get_layout, mock_get_app, mock_lib, mock_render):
        # FUNCTION ARGS
        request = mock.MagicMock()
        layout = 'test_layout'
        component_func = mock.MagicMock()
        component_source_code = 'test123'
        title = 'test_title'
        custom_css = ['custom.css']
        custom_js = ['custom.js']

        # MOCK INTERNALS
        mock_get_app.return_value = "app object"
        component_func.__name__ = 'my_mock_component_func'
        expected_return_value = "Expected return value"
        mock_render.return_value = expected_return_value
        mock_get_layout.return_value = "my_layout_func"

        # EXECUTE FUNCTION
        response = page_handler._global_page_component_controller(
            request=request, 
            layout=layout,
            component_func=component_func,
            component_source_code=component_source_code,
            title=title,
            custom_css=custom_css,
            custom_js=custom_js
        )

        # EVALUATE EXECUTION
        mock_get_app.assert_called_once_with(request=request, get_class=True)
        mock_get_layout.assert_called_once_with(mock_get_app(), layout)
        mock_lib.refresh.assert_called_with(new_identifier='my-mock-component-func')
        mock_lib.load_dependencies_from_source_code.assert_called_with(component_source_code)
        render_called_with_args = mock_render.call_args.args
        self.assertEqual(render_called_with_args[0], request)
        self.assertEqual(render_called_with_args[1], 'tethys_apps/reactpy_base.html')
        render_context = render_called_with_args[2]
        self.assertListEqual(list(render_context.keys()), ['app', 'layout_func', 'component_func', 'reactjs_version', 'title', 'custom_css', 'custom_js'])
        self.assertEqual(render_context['app'], 'app object')
        self.assertEqual(render_context['layout_func'](), 'my_layout_func')
        self.assertEqual(render_context['component_func'](), component_func)
        self.assertEqual(render_context['reactjs_version'], mock_lib.REACTJS_VERSION)
        self.assertEqual(render_context['title'], title)
        self.assertEqual(render_context['custom_css'], custom_css)
        self.assertEqual(render_context['custom_js'], custom_js)
        self.assertEqual(response, expected_return_value)

    def test_page_component_wrapper__layout_none(
        self
    ):
        # FUNCTION ARGS
        app = mock.MagicMock()
        user = mock.MagicMock()
        layout = None
        component = mock.MagicMock()
        component_return_val = "rendered_component"
        component.return_value = component_return_val
        
        return_value = page_handler.page_component_wrapper(app, user, layout, component)
        
        self.assertEqual(return_value, component_return_val)

    def test_page_component_wrapper__layout_not_none(
        self
    ):
        # FUNCTION ARGS
        app = mock.MagicMock()
        app.restered_url_maps = []
        user = mock.MagicMock()
        layout = mock.MagicMock()
        layout_return_val = "returned_layout"
        layout.return_value = layout_return_val
        component = mock.MagicMock()
        component_return_val = "rendered_component"
        component.return_value = component_return_val
        
        return_value = page_handler.page_component_wrapper(app, user, layout, component)
        
        self.assertEqual(return_value, layout_return_val)
        layout.assert_called_once_with({'app': app, 'user': user, 'nav-links': app.navigation_links}, component_return_val)

    @mock.patch('tethys_apps.base.controller._process_url_kwargs')
    @mock.patch('tethys_apps.base.controller._global_page_component_controller')
    @mock.patch('tethys_apps.base.controller.permission_required')
    @mock.patch('tethys_apps.base.controller.enforce_quota')
    @mock.patch('tethys_apps.base.controller.ensure_oauth2')
    @mock.patch('tethys_apps.base.controller.login_required_decorator')
    @mock.patch('tethys_apps.base.controller._get_url_map_kwargs_list')
    def test_page_with_permissions(
        self, 
        mock_get_url_map_kwargs_list,
        mock_login_required_decorator,
        mock_ensure_oauth2,
        mock_enforce_quota,
        mock_permission_required,
        mock_global_page_component, 
        mock_process_kwargs
    ):
        layout = "MyLayout"
        title = 'My Cool Page'
        index = 0
        custom_css = ['custom.css']
        custom_js = ['custom.js']
        function = lambda x: x
        return_value = tethys_controller.page(
            permissions_required=['test_permission'],
            enforce_quotas=['test_quota'],
            ensure_oauth2_provider=['test_oauth2_provider'],
            layout=layout,
            title=title,
            index=index,
            custom_css=custom_css,
            custom_js=custom_js
        )(function)
        self.assertTrue(callable(return_value))
        mock_request = mock.MagicMock()
        mock_process_kwargs.assert_called_once()
        process_kwargs_args = mock_process_kwargs.call_args.args
        self.assertTrue(callable(process_kwargs_args[0]))
        self.assertEqual(
            process_kwargs_args[0](mock_request),
            mock_login_required_decorator()()()
        )
        mock_permission_required.assert_called_once()
        mock_enforce_quota.assert_called_once()
        mock_ensure_oauth2.assert_called_once()
        self.assertEqual(mock_login_required_decorator.call_count, 2)
        mock_get_url_map_kwargs_list.assert_called_once_with(
            function_or_class=function,
            name=None,
            url=None,
            protocol="http",
            regex=None,
            title=title,
            index=index
        )

    @mock.patch('tethys_apps.base.controller._process_url_kwargs')
    @mock.patch('tethys_apps.base.controller._global_page_component_controller')
    @mock.patch('tethys_apps.base.controller._get_url_map_kwargs_list')
    def test_page_with_defaults(
        self, 
        mock_get_url_map_kwargs_list,
        mock_global_page_component, 
        mock_process_kwargs
    ):
        function = lambda x: x
        return_value = tethys_controller.page()(function)
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
                component_func=function, 
                component_source_code="lambda x: x", 
                title=mock_get_url_map_kwargs_list[0]['title'], 
                custom_css=[], 
                custom_js=[]
            )
        )
        mock_get_url_map_kwargs_list.assert_called_once_with(
            function_or_class=function,
            name=None,
            url=None,
            protocol="http",
            regex=None,
            title=None,
            index=None
        )
    
    @mock.patch('tethys_apps.base.controller._process_url_kwargs')
    @mock.patch('tethys_apps.base.controller._global_page_component_controller')
    @mock.patch('tethys_apps.base.controller._get_url_map_kwargs_list')
    def test_page_with_handler(
        self, 
        mock_get_url_map_kwargs_list,
        mock_global_page_component, 
        mock_process_kwargs
    ):
        component_function = lambda x: x
        handler_function = mock.MagicMock()
        return_value = tethys_controller.page(handler=handler_function)(component_function)
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
                title=mock_get_url_map_kwargs_list[0]['title'], 
                custom_css=[], 
                custom_js=[]
            )
        )
        mock_get_url_map_kwargs_list.assert_called_once_with(
            function_or_class=component_function,
            name=None,
            url=None,
            protocol="http",
            regex=None,
            title=None,
            index=None
        )
