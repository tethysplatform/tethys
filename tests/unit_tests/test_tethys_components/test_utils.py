import pytest
from unittest import TestCase, mock
from tethys_components import utils
from pathlib import Path
from urllib.parse import urlencode, urljoin

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

    def test_background_execute_invalid_args(self):
        with self.assertRaises(ValueError):
            utils.background_execute(lambda: None, "fail")

    def test_background_execute_no_delay(self):
        mock_import = mock.patch("builtins.__import__").start()

        def _test_func(arg1):
            pass

        utils.background_execute(_test_func, ("Hello",))
        mock_import.return_value.Thread.assert_called_once_with(
            target=utils._background_execute_wrapper,
            args=(_test_func, ("Hello",), None),
        )
        mock_import.return_value.Thread().start.assert_called_once()
        mock.patch.stopall()

    def test_background_execute_delay(self):
        mock_import = mock.patch("builtins.__import__").start()

        def _test_func(arg1):
            pass

        utils.background_execute(_test_func, ("Hello",), delay_seconds=10)
        mock_import.return_value.Timer.assert_called_once_with(
            interval=10,
            function=utils._background_execute_wrapper,
            args=(_test_func, ("Hello",), None),
        )
        mock_import.return_value.Timer().start.assert_called_once()
        mock.patch.stopall()

    @mock.patch("tethys_components.utils.RepeatManager")
    def test_background_execute_repeat(self, mock_repeat_manager):
        mock_import = mock.patch("builtins.__import__").start()

        def _test_func(arg1):
            pass

        utils.background_execute(_test_func, ("Hello",), repeat_seconds=1)
        mock_import.assert_not_called()
        mock_repeat_manager.assert_called_once_with(
            repeat_seconds=1,
            target=utils._background_execute_wrapper,
            args=(_test_func, ("Hello",), None),
        )
        mock.patch.stopall()

    def test_props_all_cases_combined(self):
        expected = {"foo": "bar", "onClick": "test", "thisProp": "none"}
        value = utils.Props(foo_="bar", on_click="test", this_prop=None)

        self.assertEqual(value, expected)

    def test_get_layout_component_layout_callable(self):
        def _test_layout_func():
            pass

        self.assertEqual(
            utils._get_layout_component(self.app, _test_layout_func), _test_layout_func
        )

    def test_get_layout_component_default_layout_callable(self):
        def _test_layout_func():
            pass

        self.app.default_layout = _test_layout_func
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
        def _test_func(arg1, arg2, arg3):
            self.assertTrue(isinstance(arg1, utils.DotNotationDict))
            self.assertTrue(isinstance(arg2, utils.DotNotationDict))
            self.assertTrue(isinstance(arg3, str))

        _test_func(
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

    def test_fetch(self):
        mock_import = mock.patch("builtins.__import__").start()
        test_content = "this is a test"
        mock_import.return_value.get.return_value.text = test_content
        test_url = "test-url"

        data = utils.fetch(test_url)

        mock_import.return_value.get.assert_called_once_with(test_url)
        self.assertEqual(data, test_content)

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

    def test_transform_coordinate_custom_projections(self):
        mock_import = mock.patch("builtins.__import__").start()
        coordinate = [0, 0]
        src_proj = {"definition": "test src proj"}
        target_proj = {"definition": "test src proj"}

        result = utils.transform_coordinate(coordinate, src_proj, target_proj)

        self.assertEqual(
            mock_import.return_value.Transformer.from_crs.return_value.transform.return_value,
            result,
        )
        mock_import.return_value.CRS.assert_has_calls(
            [mock.call(src_proj["definition"]), mock.call(target_proj["definition"])]
        )

        mock.patch.stopall()

    def test_transform_coordinate_invalid_src_proj(self):
        mock.patch("builtins.__import__").start()
        coordinate = [0, 0]
        src_proj = 1234
        target_proj = {"definition": "test src proj"}

        with self.assertRaises(ValueError):
            utils.transform_coordinate(coordinate, src_proj, target_proj)

    def test_transform_coordinate_invalid_target_proj(self):
        mock.patch("builtins.__import__").start()
        coordinate = [0, 0]
        src_proj = {"definition": "test src proj"}
        target_proj = 1234

        with self.assertRaises(ValueError):
            utils.transform_coordinate(coordinate, src_proj, target_proj)

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

    def test_repeat_manager_start_and_cancel(self):
        # Patch the Thread and Timer implementations on the class
        rm = utils.RepeatManager(repeat_seconds=2, target=lambda: None, args=(1,))

        with (
            mock.patch.object(utils.RepeatManager, "Thread") as mock_thread_cls,
            mock.patch.object(utils.RepeatManager, "Timer") as mock_timer_cls,
        ):

            # Make start/cancel available on instances
            mock_thread = mock.MagicMock()
            mock_timer = mock.MagicMock()
            mock_thread_cls.return_value = mock_thread
            mock_timer_cls.return_value = mock_timer

            # Start the repeat manager
            rm.start()

            # Thread should be created and started for the first invocation
            mock_thread_cls.assert_called()
            mock_thread.start.assert_called_once()

            # Timer should be created with the correct interval and function
            mock_timer_cls.assert_called()
            called_args, called_kwargs = mock_timer_cls.call_args
            self.assertEqual(called_kwargs.get("interval"), 2)
            self.assertTrue(callable(called_kwargs.get("function")))

            # is_alive should be True after start
            self.assertTrue(rm.is_alive())

            # Cancel should stop the repeating timer
            rm.cancel()
            mock_timer.cancel.assert_called_once()
            self.assertFalse(rm.is_alive())

    def test_repeat_manager_repeat_schedules_timer_again(self):
        # Verify that _repeat_function schedules another timer when running
        rm = utils.RepeatManager(repeat_seconds=3, target=lambda: None, args=(1,))

        with (
            mock.patch.object(utils.RepeatManager, "Thread") as mock_thread_cls,
            mock.patch.object(utils.RepeatManager, "Timer") as mock_timer_cls,
        ):

            mock_thread = mock.MagicMock()
            mock_timer = mock.MagicMock()
            mock_thread_cls.return_value = mock_thread
            mock_timer_cls.return_value = mock_timer

            # Directly call internal repeat function to simulate running state
            rm._running = False
            rm._repeat_function()
            mock_thread.start.assert_not_called()
            rm._running = True
            rm._repeat_function()

            # Should have started a Thread and scheduled a Timer
            mock_thread.start.assert_called_once()
            mock_timer.start.assert_called_once()
            # The created timer instance should be stored on the manager
            self.assertIs(rm._timer, mock_timer)

    def test_get_legend_url_invalid_tag(self):
        vdom = {"tagName": "Div", "attributes": {}}
        with self.assertRaises(ValueError):
            utils._get_legend_url_(vdom)

    def test_get_legend_url_single_layer_list_returns_none(self):
        # When LAYERS is a single-element list the function currently treats
        # it as not a single-layer and will print and return None.
        vdom = {
            "tagName": "ImageWMSSource",
            "attributes": {
                "options": {
                    "params": {"LAYERS": ["only_layer"]},
                    "url": "http://example.com/wms",
                }
            },
        }

        with (
            mock.patch("builtins.print") as mock_print,
            mock.patch("builtins.__import__"),
        ):
            result = utils._get_legend_url_(vdom)
            self.assertIsNone(result)
            mock_print.assert_called_with("NOT SINGLE LAYER")

    def test_get_legend_url_basic_with_layer_and_no_resolution(self):
        vdom = {
            "tagName": "TileWMSSource",
            "attributes": {
                "options": {
                    "params": {"LAYER": "layer1"},
                    "url": "http://example.com/wms",
                }
            },
        }

        with mock.patch("builtins.__import__") as mock_import:
            mock_import.return_value.urljoin = urljoin
            mock_import.return_value.urlencode = urlencode
            url = utils._get_legend_url_(vdom)
            self.assertIsInstance(url, str)
            self.assertIn("GetLegendGraphic", url)
            self.assertIn("LAYER=layer1", url)

    def test_get_legend_url_basic_with_single_layer_in_layers(self):
        vdom = {
            "tagName": "TileWMSSource",
            "attributes": {
                "options": {
                    "params": {"LAYERS": "layer1"},
                    "url": "http://example.com/wms",
                }
            },
        }

        with mock.patch("builtins.__import__") as mock_import:
            mock_import.return_value.urljoin = urljoin
            mock_import.return_value.urlencode = urlencode
            url = utils._get_legend_url_(vdom)
            self.assertIsInstance(url, str)
            self.assertIn("GetLegendGraphic", url)
            self.assertIn("LAYER=layer1", url)

    def test_get_legend_url_with_resolution_and_scale(self):
        vdom = {
            "tagName": "ImageWMSSource",
            "attributes": {
                "options": {
                    "params": {"LAYER": "layerX", "projection": "EPSG:3857"},
                    "url": "http://example.com/wms",
                }
            },
        }

        with mock.patch("builtins.__import__") as mock_import:
            mock_import.return_value.urljoin = urljoin
            mock_import.return_value.urlencode = urlencode
            mock_crs = mock_import.return_value.CRS
            mock_axis = mock.MagicMock()
            mock_axis.unit_conversion_factor = 2
            mock_crs.return_value.axis_info = [mock_axis]

            # Call with resolution so SCALE is computed
            result = utils._get_legend_url_(vdom, resolution=100)

        self.assertIsInstance(result, str)
        self.assertIn("GetLegendGraphic", result)
        self.assertIn("SCALE=", result)

    def test_get_feature_info_url_invalid_tag(self):
        vdom = {"tagName": "Div", "attributes": {}}
        with self.assertRaises(ValueError):
            utils._get_feature_info_url_(vdom, [0, 0], 1, "EPSG:3857", "EPSG:3857")

    def test_get_feature_info_url_not_implemented_for_diff_projections(self):
        vdom = {
            "tagName": "TileWMSSource",
            "attributes": {
                "options": {
                    "params": {"LAYERS": "layer1"},
                    "url": "http://example.com/wms",
                }
            },
        }

        with mock.patch("builtins.__import__"):
            with self.assertRaises(NotImplementedError):
                # map_proj != layer_proj triggers NotImplementedError
                utils._get_feature_info_url_(vdom, [0, 0], 1, "EPSG:3857", "EPSG:4326")

    def test_get_feature_info_url_success(self):
        vdom = {
            "tagName": "ImageWMSSource",
            "attributes": {
                "options": {
                    "params": {"LAYERS": "layer1"},
                    "url": "http://example.com/wms",
                }
            },
        }

        # Patch pyproj.CRS to provide predictable axis_info and directions
        with mock.patch("builtins.__import__") as mock_import:
            mock_import.return_value.urljoin = urljoin
            mock_import.return_value.urlencode = urlencode
            mock_crs = mock_import.return_value.CRS
            mock_axis1 = mock.MagicMock()
            mock_axis1.direction = "north"
            mock_axis2 = mock.MagicMock()
            mock_axis2.direction = "east"
            mock_crs.return_value.axis_info = [mock_axis1, mock_axis2]

            feature_url = utils._get_feature_info_url_(
                vdom,
                map_coordinate=[0, 0],
                map_resolution=1,
                map_proj="EPSG:3857",
                layer_proj="EPSG:3857",
            )

        self.assertIsInstance(feature_url, str)
        self.assertIn("GetFeatureInfo", feature_url)
        self.assertIn("I=", feature_url)
        self.assertIn("J=", feature_url)

    def test_find_by_tag_various_structures(self):
        # Nested dict/list structure with two matching tags
        tree = {
            "tagName": "root",
            "children": [
                {"tagName": "target", "children": []},
                {
                    "tagName": "branch",
                    "children": [
                        {"tagName": "target", "children": []},
                        "some text",
                    ],
                },
            ],
        }

        found = utils.find_by_tag(tree, "target")
        self.assertEqual(len(found), 2)

        # Top-level list input
        found_list = utils.find_by_tag(
            [tree, {"tagName": "target", "children": []}], "target"
        )
        self.assertEqual(len(found_list), 3)

        # Non-element input returns empty list
        self.assertEqual(utils.find_by_tag("not an element", "target"), [])
