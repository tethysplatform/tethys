import pytest
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
    @pytest.mark.django_db
    def test_infer_app_from_stack_trace_works(self, mock_inspect):
        mock_stack_item_1 = mock.MagicMock()
        mock_stack_item_1.__getitem__().f_code.co_filename = str(TEST_APP_DIR)
        mock_inspect.stack.return_value = [mock_stack_item_1, mock_stack_item_1]
        app = utils._infer_app_from_stack_trace()
        self.assertEqual(app.package, "test_app")

    @mock.patch("tethys_components.utils.Path")
    def test_infer_app_from_stack_trace_fails_no_app_package(self, mock_path):
        mock_path.side_effect = IndexError

        with self.assertRaises(ModuleNotFoundError) as cm:
            utils._infer_app_from_stack_trace()
            self.assertIn("No such module was found", str(cm.exception))

    @mock.patch("tethys_components.utils.inspect")
    def test_infer_app_from_stack_trace_fails_no_app(self, mock_inspect):
        mock_stack_item_1 = mock.MagicMock()
        mock_stack_item_1.__getitem__().f_code.co_filename = str(TEST_APP_DIR).replace(
            "test", "fake"
        )
        mock_inspect.stack.return_value = [mock_stack_item_1, mock_stack_item_1]
        with self.assertRaises(EnvironmentError) as cm:
            utils._infer_app_from_stack_trace()
            self.assertIn("app was not found", str(cm.exception))

    @mock.patch("tethys_components.utils._infer_app_from_stack_trace")
    def test_use_app_workspace_loading(self, mock_iafst):
        # SETUP ARGS/ENV
        mock_iafst.return_value = self.app
        mock_import = mock.patch("builtins.__import__").start()
        mock_import.return_value.use_query.return_value.loading = True

        # EXECUTE FUNCTION
        result = utils.use_workspace()

        # EVALUATE RESULT
        self.assertIsInstance(result, utils._PathsQuery)
        self.assertTrue(result.checking_quota)
        mock_import.return_value.use_query.assert_called_once_with(
            utils._get_app_workspace, {"app_or_request": self.app}, postprocessor=None
        )
        # CLEANUP
        mock.patch.stopall()

    @mock.patch("tethys_components.utils._infer_app_from_stack_trace")
    def test_use_user_workspace_error(self, mock_iafst):
        # SETUP ARGS/ENV
        mock_iafst.return_value = self.app
        mock_import = mock.patch("builtins.__import__").start()
        mock_import.return_value.use_query.return_value.loading = False
        mock_import.return_value.use_query.return_value.error = True

        # EXECUTE FUNCTION
        result = utils.use_workspace(self.user)

        # EVALUATE RESULT
        self.assertIsInstance(result, utils._PathsQuery)
        self.assertFalse(result.checking_quota)
        self.assertTrue(result.quota_exceeded)
        mock_import.return_value.use_query.assert_called_once_with(
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
        mock_import.return_value.use_query.return_value.loading = False
        mock_import.return_value.use_query.return_value.error = False

        # EXECUTE FUNCTION
        result = utils.use_workspace(self.user)

        # EVALUATE RESULT
        self.assertEqual(result, mock_import.return_value.use_query.return_value.data)
        self.assertFalse(result.checking_quota)
        self.assertFalse(result.quota_exceeded)

        # CLEANUP
        mock.patch.stopall()

    @mock.patch("tethys_components.utils._infer_app_from_stack_trace")
    def test_use_app_media_loading(self, mock_iafst):
        # SETUP ARGS/ENV
        mock_iafst.return_value = self.app
        mock_import = mock.patch("builtins.__import__").start()
        mock_import.return_value.use_query.return_value.loading = True

        # EXECUTE FUNCTION
        result = utils.use_media()

        # EVALUATE RESULT
        self.assertIsInstance(result, utils._PathsQuery)
        self.assertTrue(result.checking_quota)
        mock_import.return_value.use_query.assert_called_once_with(
            utils._get_app_media, {"app_or_request": self.app}, postprocessor=None
        )
        # CLEANUP
        mock.patch.stopall()

    @mock.patch("tethys_components.utils._infer_app_from_stack_trace")
    def test_use_user_media_error(self, mock_iafst):
        # SETUP ARGS/ENV
        mock_iafst.return_value = self.app
        mock_import = mock.patch("builtins.__import__").start()
        mock_import.return_value.use_query.return_value.loading = False
        mock_import.return_value.use_query.return_value.error = True

        # EXECUTE FUNCTION
        result = utils.use_media(self.user)

        # EVALUATE RESULT
        self.assertIsInstance(result, utils._PathsQuery)
        self.assertFalse(result.checking_quota)
        self.assertTrue(result.quota_exceeded)
        mock_import.return_value.use_query.assert_called_once_with(
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
        mock_import.return_value.use_query.return_value.loading = False
        mock_import.return_value.use_query.return_value.error = False

        # EXECUTE FUNCTION
        result = utils.use_media(self.user)

        # EVALUATE RESULT
        self.assertEqual(result, mock_import.return_value.use_query.return_value.data)
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
        
        utils.background_execute(test_func, ("Hello",))
        mock_import.return_value.Thread.assert_called_once_with(
            target=utils._background_execute_wrapper,
            args=(test_func, ("Hello",), None)
        )
        mock_import.return_value.Thread().start.assert_called_once()
        mock.patch.stopall()

    def test_background_execute_delay(self):
        mock_import = mock.patch("builtins.__import__").start()

        def test_func(arg1):
            pass

        utils.background_execute(test_func, ("Hello",), delay_seconds=10)
        mock_import.return_value.Timer.assert_called_once_with(
            interval=10, function=utils._background_execute_wrapper, args=(test_func, ("Hello",), None)
        )
        mock_import.return_value.Timer().start.assert_called_once()
        mock.patch.stopall()

    @mock.patch("tethys_components.utils.RepeatManager")
    def test_background_execute_repeat(self, mock_repeat_manager):
        mock_import = mock.patch("builtins.__import__").start()

        def test_func(arg1):
            pass

        utils.background_execute(test_func, ("Hello",), repeat_seconds=1)
        mock_import.assert_not_called()
        mock_repeat_manager.assert_called_once_with(
            repeat_seconds=1,
            target=utils._background_execute_wrapper,
            args=(test_func, ("Hello",), None)
        )
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

    @mock.patch("tethys_components.utils.layouts")
    def test_get_layout_component_default_layout_not_callable(self, mock_layouts):
        self.app.default_layout = "TestLayout"
        self.assertEqual(
            utils._get_layout_component(self.app, "default"), mock_layouts.TestLayout
        )

    @mock.patch("tethys_components.utils.layouts")
    def test_get_layout_component_not_default_not_callable(self, mock_layouts):
        self.assertEqual(
            utils._get_layout_component(self.app, "TestLayout"), mock_layouts.TestLayout
        )

    def test_AttrDict_all_the_stops(self):
        test_dict = {
            "camelProp": [
                {
                    "list": "of",
                    "props": ["that", {"are": "all"}, "very"],
                    "differEnt": [{"types": "and"}, {"nesting": "orders"}],
                },
            ],
            "clear": "is reserved",
            "update": 100,
            "oneMore": {"howbout": "this"},
        }

        d = utils.DotNotationDict(test_dict)

        self.assertTrue(hasattr(d, "camel_prop"))
        self.assertTrue(isinstance(d.camel_prop, list))
        self.assertEqual(len(d.camel_prop), 1)
        self.assertTrue(isinstance(d.camel_prop[0], utils.DotNotationDict))
        self.assertTrue(hasattr(d.camel_prop[0], "list"))
        self.assertEqual(d.camel_prop[0].list, "of")
        self.assertTrue(hasattr(d.camel_prop[0], "props"))
        self.assertTrue(isinstance(d.camel_prop[0].props, list))
        self.assertEqual(len(d.camel_prop[0].props), 3)
        self.assertEqual(d.camel_prop[0].props[0], "that")
        self.assertTrue(isinstance(d.camel_prop[0].props[1], utils.DotNotationDict))
        self.assertTrue(hasattr(d.camel_prop[0].props[1], "are"))
        self.assertEqual(d.camel_prop[0].props[1].are, "all")
        self.assertEqual(d.camel_prop[0].props[2], "very")
        self.assertTrue(hasattr(d.camel_prop[0], "differ_ent"))
        self.assertTrue(isinstance(d.camel_prop[0].differ_ent, list))
        self.assertEqual(len(d.camel_prop[0].differ_ent), 2)
        self.assertTrue(
            isinstance(d.camel_prop[0].differ_ent[0], utils.DotNotationDict)
        )
        self.assertTrue(
            isinstance(d.camel_prop[0].differ_ent[1], utils.DotNotationDict)
        )
        self.assertTrue(hasattr(d.camel_prop[0].differ_ent[0], "types"))
        self.assertEqual(d.camel_prop[0].differ_ent[0].types, "and")
        self.assertTrue(hasattr(d.camel_prop[0].differ_ent[1], "nesting"))
        self.assertEqual(d.camel_prop[0].differ_ent[1].nesting, "orders")
        self.assertTrue(hasattr(d, "clear_"))
        self.assertEqual(d.clear_, "is reserved")
        self.assertTrue(hasattr(d, "update_"))
        self.assertEqual(d.update_, 100)
        self.assertTrue(hasattr(d, "one_more"))
        self.assertTrue(isinstance(d.one_more, utils.DotNotationDict))
        self.assertTrue(hasattr(d.one_more, "howbout"))
        self.assertEqual(d.one_more.howbout, "this")
        with self.assertRaises(AttributeError):
            d.not_there

    def test_args_to_attrdicts_wrapper(self):
        @utils.args_to_dot_notation_dicts
        def test_func(arg1, arg2, arg3):
            self.assertTrue(isinstance(arg1, utils.DotNotationDict))
            self.assertTrue(isinstance(arg2, utils.DotNotationDict))
            self.assertTrue(isinstance(arg3, str))

        test_func(
            {"this": "is", "a": "test"}, {"how": "about", "another": "one"}, "done"
        )

    def test_fetch_json_as_attrdict(self):
        mock_import = mock.patch("builtins.__import__").start()
        test_dict = {"this": "is", "a": "test"}
        mock_import.return_value.get.return_value.json.return_value = test_dict
        test_url = "test-url"

        data = utils.fetch_json(test_url)

        mock_import.return_value.get.assert_called_once_with(test_url)
        self.assertTrue(isinstance(data, utils.DotNotationDict))
        self.assertEqual(data.this, "is")
        self.assertEqual(data.a, "test")

        mock.patch.stopall()

    def test_fetch_json_not_attrdict(self):
        mock_import = mock.patch("builtins.__import__").start()
        test_dict = {"this": "is", "a": "test"}
        mock_import.return_value.get.return_value.json.return_value = test_dict
        test_url = "test-url"

        data = utils.fetch_json(test_url, as_attr_dict=False)

        mock_import.return_value.get.assert_called_once_with(test_url)
        self.assertDictEqual(data, test_dict)

        mock.patch.stopall()

    def test_transform_coordinate(self):
        mock_import = mock.patch("builtins.__import__").start()
        coordinate = [0, 0]
        src_proj = "EPSG:3857"
        target_proj = "EPSG:4326"

        result = utils.transform_coordinate(coordinate, src_proj, target_proj)

        self.assertEqual(
            mock_import.return_value.Transformer.from_crs.return_value.transform.return_value,
            result,
        )
        mock_import.return_value.CRS.assert_has_calls(
            [mock.call(src_proj), mock.call(target_proj)]
        )

        mock.patch.stopall()

    def test_get_db_object(self):
        app = mock.MagicMock(db_object="expected")
        val = utils._get_db_object(app)
        self.assertEqual(val, "expected")

    def test_background_execute_wrapper(self):
        test_func = mock.MagicMock()
        test_func.return_value = "Test"
        callback = mock.MagicMock()

        utils._background_execute_wrapper(test_func, ("Hello",), callback)
        test_func.assert_called_once_with("Hello")
        callback.assert_called_once_with("Test")
