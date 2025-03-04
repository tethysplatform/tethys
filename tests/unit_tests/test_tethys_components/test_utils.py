from unittest import TestCase, mock
from tethys_components import utils
from pathlib import Path

THIS_DIR = Path(__file__).parent
TEST_APP_DIR = (
    THIS_DIR.parents[1] / "apps" / "tethysapp-test_app" / "tethysapp" / "test_app"
)


class TestComponentUtils(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = mock.MagicMock()
        cls.app = mock.MagicMock()

    @mock.patch("tethys_components.utils.inspect")
    def test_infer_app_from_stack_trace_works(self, mock_inspect):
        mock_stack_item_1 = mock.MagicMock()
        mock_stack_item_1.__getitem__().f_code.co_filename = str(TEST_APP_DIR)
        mock_inspect.stack.return_value = [mock_stack_item_1, mock_stack_item_1]
        app = utils._infer_app_from_stack_trace()
        self.assertEqual(app.package, "test_app")

    @mock.patch("tethys_components.utils.inspect")
    def test_infer_app_from_stack_trace_fails_no_app_package(self, mock_inspect):
        mock_stack_item_1 = mock.MagicMock()
        mock_stack_item_1.__getitem__().f_code.co_filename = "throws_exception"

        with self.assertRaises(Exception) as cm:
            utils._infer_app_from_stack_trace()
            self.assertIn("No package was found", str(cm.exception))

    @mock.patch("tethys_components.utils.inspect")
    def test_infer_app_from_stack_trace_fails_no_app(self, mock_inspect):
        mock_stack_item_1 = mock.MagicMock()
        mock_stack_item_1.__getitem__().f_code.co_filename = str(TEST_APP_DIR).replace(
            "test", "fake"
        )
        mock_inspect.stack.return_value = [mock_stack_item_1, mock_stack_item_1]
        with self.assertRaises(Exception) as cm:
            utils._infer_app_from_stack_trace()
            self.assertIn("app was not found", str(cm.exception))

    @mock.patch("tethys_components.utils._infer_app_from_stack_trace")
    def test_use_app_workspace_loading(self, mock_iafst):
        # SETUP ARGS/ENV
        mock_iafst.return_value = self.app
        mock_import = mock.patch("builtins.__import__").start()
        mock_import().use_query.return_value.loading = True

        # EXECUTE FUNCTION
        result = utils.use_workspace()

        # EVALUATE RESULT
        self.assertIsInstance(result, utils._PathsQuery)
        self.assertTrue(result.checking_quota)
        mock_import().use_query.assert_called_once_with(
            utils._get_app_workspace, {"app_or_request": self.app}, postprocessor=None
        )
        # CLEANUP
        mock.patch.stopall()

    @mock.patch("tethys_components.utils._infer_app_from_stack_trace")
    def test_use_user_workspace_error(self, mock_iafst):
        # SETUP ARGS/ENV
        mock_iafst.return_value = self.app
        mock_import = mock.patch("builtins.__import__").start()
        mock_import().use_query.return_value.loading = False
        mock_import().use_query.return_value.error = True

        # EXECUTE FUNCTION
        result = utils.use_workspace(self.user)

        # EVALUATE RESULT
        self.assertIsInstance(result, utils._PathsQuery)
        self.assertFalse(result.checking_quota)
        self.assertTrue(result.quota_exceeded)
        mock_import().use_query.assert_called_once_with(
            utils._get_user_workspace,
            {"app_or_request": self.app, "user_or_request": self.user},
            postprocessor=None,
        )
        # CLEANUP
        mock.patch.stopall()

    @mock.patch("tethys_components.utils._infer_app_from_stack_trace")
    def test_use_user_workspace_ready(self, mock_iafst):
        # SETUP ARGS/ENV
        mock_iafst.return_value = self.app
        mock_import = mock.patch("builtins.__import__").start()
        mock_import().use_query.return_value.loading = False
        mock_import().use_query.return_value.error = False

        # EXECUTE FUNCTION
        result = utils.use_workspace(self.user)

        # EVALUATE RESULT
        self.assertEqual(result, mock_import().use_query.return_value.data)
        self.assertFalse(result.checking_quota)
        self.assertFalse(result.quota_exceeded)

        # CLEANUP
        mock.patch.stopall()

    @mock.patch("tethys_components.utils._infer_app_from_stack_trace")
    def test_use_app_media_loading(self, mock_iafst):
        # SETUP ARGS/ENV
        mock_iafst.return_value = self.app
        mock_import = mock.patch("builtins.__import__").start()
        mock_import().use_query.return_value.loading = True

        # EXECUTE FUNCTION
        result = utils.use_media()

        # EVALUATE RESULT
        self.assertIsInstance(result, utils._PathsQuery)
        self.assertTrue(result.checking_quota)
        mock_import().use_query.assert_called_once_with(
            utils._get_app_media, {"app_or_request": self.app}, postprocessor=None
        )
        # CLEANUP
        mock.patch.stopall()

    @mock.patch("tethys_components.utils._infer_app_from_stack_trace")
    def test_use_user_media_error(self, mock_iafst):
        # SETUP ARGS/ENV
        mock_iafst.return_value = self.app
        mock_import = mock.patch("builtins.__import__").start()
        mock_import().use_query.return_value.loading = False
        mock_import().use_query.return_value.error = True

        # EXECUTE FUNCTION
        result = utils.use_media(self.user)

        # EVALUATE RESULT
        self.assertIsInstance(result, utils._PathsQuery)
        self.assertFalse(result.checking_quota)
        self.assertTrue(result.quota_exceeded)
        mock_import().use_query.assert_called_once_with(
            utils._get_user_media,
            {"app_or_request": self.app, "user_or_request": self.user},
            postprocessor=None,
        )
        # CLEANUP
        mock.patch.stopall()

    @mock.patch("tethys_components.utils._infer_app_from_stack_trace")
    def test_use_user_media_ready(self, mock_iafst):
        # SETUP ARGS/ENV
        mock_iafst.return_value = self.app
        mock_import = mock.patch("builtins.__import__").start()
        mock_import().use_query.return_value.loading = False
        mock_import().use_query.return_value.error = False

        # EXECUTE FUNCTION
        result = utils.use_media(self.user)

        # EVALUATE RESULT
        self.assertEqual(result, mock_import().use_query.return_value.data)
        self.assertFalse(result.checking_quota)
        self.assertFalse(result.quota_exceeded)

        # CLEANUP
        mock.patch.stopall()

    @mock.patch("tethys_components.utils._infer_app_from_stack_trace")
    def test_use_resources(self, mock_iafst):
        mock_iafst.return_value = self.app

        result = utils.use_resources()

        self.assertEqual(result, self.app.resources_path)

    @mock.patch("tethys_components.utils._infer_app_from_stack_trace")
    def test_use_public(self, mock_iafst):
        mock_iafst.return_value = self.app

        result = utils.use_public()

        self.assertEqual(result, self.app.public_path)

    def test_background_execute_no_delay(self):
        mock_import = mock.patch("builtins.__import__").start()

        def test_func(arg1):
            pass

        utils.background_execute(test_func, ["Hello"])
        mock_import().Thread.assert_called_once_with(test_func, args=["Hello"])
        mock_import().Thread().start.assert_called_once()
        mock.patch.stopall()

    def test_background_execute_delay(self):
        mock_import = mock.patch("builtins.__import__").start()

        def test_func(arg1):
            pass

        utils.background_execute(test_func, ["Hello"], 10)
        mock_import().Timer.assert_called_once_with(10, test_func, ["Hello"])
        mock_import().Timer().start.assert_called_once()
        mock.patch.stopall()

    def test_props_all_cases_combined(self):
        expected = {"foo": "bar", "onClick": "test", "thisProp": "none"}
        value = utils.Props(foo_="bar", on_click="test", this_prop=None)

        self.assertEqual(value, expected)

    def test_get_layout_component_layout_callable(self):
        def test_layout_func():
            pass

        self.assertEqual(
            utils._get_layout_component(self.app, test_layout_func), test_layout_func
        )

    def test_get_layout_component_default_layout_callable(self):
        def test_layout_func():
            pass

        self.app.default_layout = test_layout_func
        self.assertEqual(
            utils._get_layout_component(self.app, "default"), self.app.default_layout
        )

    def test_get_layout_component_default_layout_not_callable(self):
        self.app.default_layout = "TestLayout"
        mock_import = mock.patch("builtins.__import__").start()
        self.assertEqual(
            utils._get_layout_component(self.app, "default"),
            mock_import().layouts.TestLayout,
        )
        mock.patch.stopall()

    def test_get_layout_component_not_default_not_callable(self):
        mock_import = mock.patch("builtins.__import__").start()
        self.assertEqual(
            utils._get_layout_component(self.app, "TestLayout"),
            mock_import().layouts.TestLayout,
        )
        mock.patch.stopall()
