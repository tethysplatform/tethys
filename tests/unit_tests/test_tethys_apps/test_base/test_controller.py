import unittest
from unittest import mock
import tethys_apps.base.controller as tethys_controller


class TestController(unittest.TestCase):
    def setUp(self):
        tethys_controller.app_controllers_list = list()

    def tearDown(self):
        pass

    @mock.patch("django.views.generic.View.as_view")
    def test_TethysController(self, mock_as_view):
        kwargs = {"foo": "bar"}
        tethys_controller.TethysController.as_controller(**kwargs)
        mock_as_view.assert_called_with(**kwargs)

    def check_url_map_kwargs(self, name, url=None):
        kwargs = tethys_controller.app_controllers_list.pop(0)
        self.assertEqual(name, kwargs["name"])
        url = url or f'test-controller/{name.replace("_", "-")}/'
        self.assertEqual(url, kwargs["url"])
        return kwargs

    def test_controller(self):
        @tethys_controller.controller
        def controller_func(request):
            pass

        self.check_url_map_kwargs(name=controller_func.__name__)

    def test_controller_TethysController(self):
        @tethys_controller.controller
        class TestTethysController(tethys_controller.TethysController):
            def get(self, request):
                pass

        self.check_url_map_kwargs(name=TestTethysController.__name__)

    @mock.patch("tethys_apps.base.controller.issubclass", return_value=True)
    def test_controller_protocol_websocket(self, _):
        @tethys_controller.controller(
            protocol="websocket",
        )
        class TestConsumer:
            @classmethod
            def as_asgi(cls):
                return ""

        self.check_url_map_kwargs(name=TestConsumer.__name__)

    def test_controller_url_arg(self):
        @tethys_controller.controller
        def controller_func(request, url_arg):
            pass

        self.check_url_map_kwargs(
            name=controller_func.__name__,
            url="test-controller/controller-func/{url_arg}/",
        )

    def test_controller_url_kwarg(self):
        @tethys_controller.controller
        def controller_func(request, url_arg=None):
            pass

        self.check_url_map_kwargs(
            name=controller_func.__name__, url="test-controller/controller-func/"
        )
        self.check_url_map_kwargs(
            name=f"{controller_func.__name__}_1",
            url="test-controller/controller-func/{url_arg}/",
        )

    def test_controller_user_workspace(self):
        @tethys_controller.controller(user_workspace=True)
        def controller_func(request, user_workspace):
            pass

        self.check_url_map_kwargs(name=controller_func.__name__)

    def test_controller_app_workspace(self):
        @tethys_controller.controller(app_workspace=True)
        def controller_func(request, app_workspace):
            pass

        self.check_url_map_kwargs(name=controller_func.__name__)

    def test_controller_ensure_oauth2_provider(self):
        @tethys_controller.controller(ensure_oauth2_provider="test_provider")
        def controller_func(request):
            pass

        self.check_url_map_kwargs(name=controller_func.__name__)

    def test_controller_permissions_required(self):
        @tethys_controller.controller(permissions_required="test_permission")
        def controller_func(request):
            pass

        self.check_url_map_kwargs(name=controller_func.__name__)

    def test_controller_enforce_quota_codenames(self):
        @tethys_controller.controller(enforce_quotas="test_quota")
        def controller_func(request):
            pass

        self.check_url_map_kwargs(name=controller_func.__name__)

    def test_controller_custom_arguments(self):
        name = "test_name"
        url = "/test/url/"
        protocol = "test_protocol"
        handler = "handler"
        handler_type = "handler_type"

        @tethys_controller.controller(
            name=name,
            url=url,
            protocol=protocol,
            _handler=handler,
            _handler_type=handler_type,
        )
        def controller_func(request):
            pass

        kwargs = self.check_url_map_kwargs(name=name, url=url)
        self.assertEqual(protocol, kwargs["protocol"])
        self.assertEqual(handler, kwargs["handler"])
        self.assertEqual(handler_type, kwargs["handler_type"])

    def test_handler_controller_as_string(self):
        function = mock.MagicMock(__name__="test")
        tethys_controller.handler(controller="test_app.controllers.home_controller")(
            function
        )

    @mock.patch("tethys_apps.base.controller.with_request_decorator")
    def test_handler_with_request(self, mock_with_request):
        function = mock.MagicMock(__name__="test")
        mock_with_request.return_value = function
        tethys_controller.handler(with_request=True)(function)
        mock_with_request.assert_called_with(function)

    @mock.patch("tethys_apps.base.controller.deprecation_warning")
    @mock.patch("tethys_apps.base.controller.with_workspaces_decorator")
    def test_handler_with_workspaces(self, mock_with_workspaces, __):
        function = mock.MagicMock(__name__="test")
        mock_with_workspaces.return_value = function
        tethys_controller.handler(with_workspaces=True)(function)
        mock_with_workspaces.assert_called_with(function)

    @mock.patch("tethys_apps.base.controller.with_paths_decorator")
    def test_handler_with_paths(self, mock_with_request):
        function = mock.MagicMock(__name__="test")
        mock_with_request.return_value = function
        tethys_controller.handler(with_paths=True)(function)
        mock_with_request.assert_called_with(function)

    @mock.patch("tethys_apps.base.controller.importlib.import_module")
    @mock.patch("tethys_apps.base.controller.get_all_submodules")
    def test_register_controllers(self, mock_submodules, mock_import):
        mock_controllers_module = mock.MagicMock()
        mock_controllers_module._listify.return_value = ["controllers"]
        mock_import.side_effect = [mock_controllers_module, None]
        result = tethys_controller.register_controllers("root", "controllers")
        mock_submodules.assert_called_once()
        mock_import.assert_called_with("controllers")

        self.assertEqual([], result)

    @mock.patch("tethys_apps.base.controller.isinstance")
    @mock.patch("tethys_apps.base.controller.get_all_submodules")
    @mock.patch("tethys_apps.base.controller.importlib")
    @mock.patch("tethys_apps.base.controller.write_warning")
    @mock.patch("tethys_apps.base.controller.list")
    def test_register_controllers_duplicate_name(
        self, mock_list, mock_warning, _, __, ___
    ):
        mock_controller = mock.MagicMock(__module__="module", __name__="name")
        mock_list.return_value = [
            {"name": "name", "url": "url", "controller": mock_controller},
            {"name": "name", "url": "url", "controller": mock_controller},
        ]
        tethys_controller.register_controllers("root", "controllers")
        mock_warning.assert_called_once()

    @mock.patch("tethys_apps.base.controller.isinstance")
    @mock.patch("tethys_apps.base.controller.get_all_submodules")
    @mock.patch("tethys_apps.base.controller.importlib")
    @mock.patch("tethys_apps.base.controller.url_map_maker")
    @mock.patch("tethys_apps.base.controller.list")
    def test_register_controllers_with_index(self, mock_list, _, __, ___, ____):
        mock_list.return_value = [
            {"name": "index", "url": "url"},
        ]
        tethys_controller.register_controllers("root", "controllers", "index")

    @mock.patch("tethys_apps.base.controller.isinstance")
    @mock.patch("tethys_apps.base.controller.get_all_submodules")
    @mock.patch("tethys_apps.base.controller.importlib")
    @mock.patch("tethys_apps.base.controller.url_map_maker")
    @mock.patch("tethys_apps.base.controller.write_warning")
    @mock.patch("tethys_apps.base.controller.list")
    def test_register_controllers_with_index_error(
        self, mock_list, mock_warning, _, __, ___, ____
    ):
        mock_list.return_value = [
            {"name": "name", "url": "url"},
        ]
        with self.assertRaises(RuntimeError):
            tethys_controller.register_controllers("root", "controllers", "index")

    @mock.patch("tethys_apps.base.controller.get_all_submodules")
    @mock.patch("tethys_apps.base.controller.url_map_maker")
    @mock.patch(
        "tethys_apps.base.controller._listify", return_value=["non_existent_module"]
    )
    @mock.patch("tethys_apps.base.controller.write_warning")
    @mock.patch("tethys_apps.base.controller.importlib")
    def test_register_controllers_with_import_error(
        self, mock_importlib, mock_warning, _, __, ___
    ):
        mock_importlib.import_module.side_effect = ImportError
        tethys_controller.register_controllers("root", "controllers")
        self.assertEqual(2, mock_warning.call_count)

    @mock.patch("tethys_apps.base.controller.get_all_submodules")
    @mock.patch("tethys_apps.base.controller.url_map_maker")
    @mock.patch(
        "tethys_apps.base.controller._listify", return_value=["non_existent_module"]
    )
    @mock.patch("tethys_apps.base.controller.write_warning")
    @mock.patch("tethys_apps.base.controller.importlib")
    def test_register_controllers_with_module_not_found_error(
        self, mock_importlib, mock_warning, _, __, ___
    ):
        mock_importlib.import_module.side_effect = ModuleNotFoundError(
            "No module named 'another_non_existent_module'"
        )
        tethys_controller.register_controllers("root", "controllers")
        self.assertEqual(2, mock_warning.call_count)

    @mock.patch("tethys_apps.base.controller.isinstance")
    @mock.patch("tethys_apps.base.controller.get_all_submodules")
    @mock.patch("tethys_apps.base.controller.importlib")
    @mock.patch("tethys_apps.base.controller.list")
    @mock.patch("tethys_apps.base.controller.url_map_maker")
    def test_register_controllers_catch_all(
        self, mock_url_map_maker, mock_list, _, __, ___
    ):
        mock_controller = mock.MagicMock(__module__="module", __name__="name")
        mock_list.return_value = [
            {"name": "foo", "url": "url", "controller": mock_controller},
        ]
        mock_UrlMap = mock_url_map_maker()
        tethys_controller.register_controllers("root", "controllers", catch_all="foo")
        mock_UrlMap.assert_called_with(
            name="catch_all", url="root/.*/", controller=mock_controller
        )

    def test__get_url_map_kwargs_list_url_dict(self):
        result = tethys_controller._get_url_map_kwargs_list(
            url={
                "test": "test/url/",
                "another_test": "test/{another}/url/",
            }
        )
        self.assertEqual(result[0]["title"], "Test")
        self.assertEqual(result[1]["title"], "Another Test")

    def test__get_url_map_kwargs_list_url_list(self):
        result = tethys_controller._get_url_map_kwargs_list(
            name="test",
            url=[
                "test/url/",
                "test/{another}/url/",
            ],
        )
        self.assertEqual(result[0]["title"], "Test")
        self.assertEqual(result[1]["title"], "Test 1")
