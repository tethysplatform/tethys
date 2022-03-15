import unittest
from unittest import mock
import tethys_apps.base.controller as tethys_controller


class TestController(unittest.TestCase):
    def setUp(self):
        tethys_controller.app_controllers_list = list()

    def tearDown(self):
        pass

    @mock.patch('django.views.generic.View.as_view')
    def test_TethysController(self, mock_as_view):
        kwargs = {'foo': 'bar'}
        tethys_controller.TethysController.as_controller(**kwargs)
        mock_as_view.assert_called_with(**kwargs)

    def check_url_map_kwargs(self, name, url=None):
        kwargs = tethys_controller.app_controllers_list.pop(0)
        self.assertEqual(name, kwargs['name'])
        url = url or f'test-controller/{name.replace("_", "-")}/'
        self.assertEqual(url, kwargs['url'])
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

    @mock.patch('tethys_apps.base.controller.issubclass', return_value=True)
    def test_controller_protocol_websocket(self, _):

        @tethys_controller.controller(
            protocol='websocket',
        )
        class TestConsumer:
            @classmethod
            def as_asgi(cls):
                return ''

        self.check_url_map_kwargs(name=TestConsumer.__name__)

    def test_controller_url_arg(self):
        @tethys_controller.controller
        def controller_func(request, url_arg):
            pass

        self.check_url_map_kwargs(name=controller_func.__name__, url='test-controller/controller-func/{url_arg}/')

    def test_controller_url_kwarg(self):
        @tethys_controller.controller
        def controller_func(request, url_arg=None):
            pass

        self.check_url_map_kwargs(name=controller_func.__name__, url='test-controller/controller-func/')
        self.check_url_map_kwargs(
            name=f'{controller_func.__name__}_1',
            url='test-controller/controller-func/{url_arg}/'
        )

    def test_controller_user_workspace(self):
        @tethys_controller.controller(
            user_workspace=True
        )
        def controller_func(request, user_workspace):
            pass

        self.check_url_map_kwargs(name=controller_func.__name__)

    def test_controller_app_workspace(self):
        @tethys_controller.controller(
            app_workspace=True
        )
        def controller_func(request, app_workspace):
            pass

        self.check_url_map_kwargs(name=controller_func.__name__)

    def test_controller_ensure_oauth2_provider(self):
        @tethys_controller.controller(
            ensure_oauth2_provider='test_provider'
        )
        def controller_func(request):
            pass

        self.check_url_map_kwargs(name=controller_func.__name__)

    def test_controller_permissions_required(self):
        @tethys_controller.controller(
            permissions_required='test_permission'
        )
        def controller_func(request):
            pass

        self.check_url_map_kwargs(name=controller_func.__name__)

    def test_controller_enforce_quota_codenames(self):
        @tethys_controller.controller(
            enforce_quotas='test_quota'
        )
        def controller_func(request):
            pass

        self.check_url_map_kwargs(name=controller_func.__name__)

    def test_controller_custom_arguments(self):
        name = 'test_name'
        url = '/test/url/'
        protocol = 'test_protocol'
        handler = 'handler'
        handler_type = 'handler_type'

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
        self.assertEqual(protocol, kwargs['protocol'])
        self.assertEqual(handler, kwargs['handler'])
        self.assertEqual(handler_type, kwargs['handler_type'])

    @mock.patch('tethys_apps.base.controller.with_request_decorator')
    def test_handler_with_request(self, mock_with_request):
        function = mock.MagicMock(__name__='test')
        mock_with_request.return_value = function
        tethys_controller.handler(with_request=True)(function)
        mock_with_request.assert_called_with(function)

    @mock.patch('tethys_apps.base.controller.with_workspaces_decorator')
    def test_handler_with_workspaces(self, mock_with_request):
        function = mock.MagicMock(__name__='test')
        mock_with_request.return_value = function
        tethys_controller.handler(with_workspaces=True)(function)
        mock_with_request.assert_called_with(function)
