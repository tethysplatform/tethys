import asyncio
from unittest import TestCase, mock
from tethys_components import utils
from tethys_apps.base import TethysWorkspace
from pathlib import Path
from django.contrib.auth.models import User

THIS_DIR = Path(__file__).parent
TEST_APP_DIR = THIS_DIR.parent.parent / 'apps' / 'tethysapp-test_app' / 'tethysapp' / 'test_app'


class TestComponentUtils(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loop = asyncio.get_event_loop()
        cls.user = User.objects.create_user(
            username="john", email="john@gmail.com", password="pass"
        )
        cls.app = mock.MagicMock()

    @classmethod
    def tearDownClass(cls):
        cls.loop.close()
        cls.user.delete()

    def run_coroutine(self, f, *args, **kwargs):
        result = self.loop.run_until_complete(f(*args, **kwargs))
        return result

    def test_get_workspace_for_app(self):
        workspace = self.run_coroutine(utils.get_workspace, 'test_app', user=None)
        self.assertIsInstance(workspace, TethysWorkspace)
        self.assertEqual(workspace.path, str(TEST_APP_DIR / 'workspaces' / 'app_workspace').lower())

    def test_get_workspace_for_user(self):
        workspace = self.run_coroutine(utils.get_workspace, 'test_app', user=self.user)
        self.assertIsInstance(workspace, TethysWorkspace)
        self.assertEqual(workspace.path, str(TEST_APP_DIR / 'workspaces' / 'user_workspaces' / 'john').lower())

    @mock.patch('tethys_components.utils.inspect')
    def test_use_workspace(self, mock_inspect):
        mock_import = mock.patch('builtins.__import__').start()
        try:
            mock_inspect.stack().__getitem__().__getitem__().f_code.co_filename = str(TEST_APP_DIR)
            workspace = utils.use_workspace('john')
            self.assertEqual(mock_import.call_args_list[-1][0][0], 'reactpy_django.hooks')
            self.assertEqual(mock_import.call_args_list[-1][0][3][0], 'use_query')
            mock_import().use_query.assert_called_once_with(utils.get_workspace, {'app_package': 'test_app', 'user': 'john'}, postprocessor=None)
            self.assertEqual(workspace, mock_import().use_query().data)
        finally:
            mock.patch.stopall()

    def test_delayed_execute(self):
        mock_import = mock.patch('builtins.__import__').start()

        def test_func(arg1):
            print(arg1)

        utils.delayed_execute(10, test_func, ['Hello'])
        mock_import().Timer.assert_called_once_with(10, test_func, ['Hello'])
        mock_import().Timer().start.assert_called_once()
        mock.patch.stopall()

    def test_props_all_cases_combined(self):
        expected = {
            'foo': 'bar',
            'on_click': 'test',
            'this-prop': 'none'
        }
        value = utils.Props(foo_='bar', on_click='test', this_prop=None)

        self.assertEqual(value, expected)

    def test_get_layout_component_layout_callable(self):
        def test_layout_func():
            pass
        self.assertEqual(utils.get_layout_component(self.app, test_layout_func), test_layout_func)

    def test_get_layout_component_default_layout_callable(self):
        def test_layout_func():
            pass
        self.app.default_layout = test_layout_func
        self.assertEqual(utils.get_layout_component(self.app, "default"), self.app.default_layout)

    def test_get_layout_component_default_layout_not_callable(self):
        self.app.default_layout = "TestLayout"
        mock_import = mock.patch('builtins.__import__').start()
        self.assertEqual(utils.get_layout_component(self.app, "default"), mock_import().layouts.TestLayout)
        mock.patch.stopall()

    def test_get_layout_component_not_default_not_callable(self):
        mock_import = mock.patch('builtins.__import__').start()
        self.assertEqual(utils.get_layout_component(self.app, "TestLayout"), mock_import().layouts.TestLayout)
        mock.patch.stopall()
