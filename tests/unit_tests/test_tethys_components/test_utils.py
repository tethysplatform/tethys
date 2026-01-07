import pytest
from unittest import mock
from tethys_components import utils
from pathlib import Path
from urllib.parse import urlencode, urljoin

THIS_DIR = Path(__file__).parent
TEST_APP_DIR = (
    THIS_DIR.parents[1] / "apps" / "tethysapp-test_app" / "tethysapp" / "test_app"
)

MOCK_APP = mock.MagicMock()
MOCK_USER = mock.MagicMock()


@mock.patch("tethys_components.utils.inspect")
@pytest.mark.django_db
def test_infer_app_from_stack_trace_works(mock_inspect):
    mock_stack_item_1 = mock.MagicMock()
    mock_stack_item_1.__getitem__().f_code.co_filename = str(TEST_APP_DIR)
    mock_inspect.stack.return_value = [mock_stack_item_1, mock_stack_item_1]
    app = utils._infer_app_from_stack_trace()
    assert app.package == "test_app"


@mock.patch("tethys_components.utils.Path")
def test_infer_app_from_stack_trace_fails_no_app_package(mock_path):
    mock_path.side_effect = IndexError

    with pytest.raises(ModuleNotFoundError) as cm:
        utils._infer_app_from_stack_trace()
        assert "No such module was found" in str(cm.exception)


@mock.patch("tethys_components.utils.inspect")
def test_infer_app_from_stack_trace_fails_no_app(mock_inspect):
    mock_stack_item_1 = mock.MagicMock()
    mock_stack_item_1.__getitem__().f_code.co_filename = str(TEST_APP_DIR).replace(
        "test", "fake"
    )
    mock_inspect.stack.return_value = [mock_stack_item_1, mock_stack_item_1]
    with pytest.raises(EnvironmentError) as cm:
        utils._infer_app_from_stack_trace()
        assert "app was not found" in str(cm.exception)


@mock.patch("tethys_components.utils._infer_app_from_stack_trace")
def test_use_app_workspace_loading(mock_iafst):
    # SETUP ARGS/ENV
    mock_iafst.return_value = MOCK_APP
    with mock.patch("builtins.__import__") as mock_import:
        mock_import.return_value.use_query.return_value.loading = True

        # EXECUTE FUNCTION
        result = utils.use_workspace()

        # EVALUATE RESULT
        assert isinstance(result, utils._PathsQuery)
        assert result.checking_quota
        mock_import.return_value.use_query.assert_called_once_with(
            utils._get_app_workspace, {"app_or_request": MOCK_APP}, postprocessor=None
        )


@mock.patch("tethys_components.utils._infer_app_from_stack_trace")
def test_use_user_workspace_error(mock_iafst):
    # SETUP ARGS/ENV
    mock_iafst.return_value = MOCK_APP
    with mock.patch("builtins.__import__") as mock_import:
        mock_import.return_value.use_query.return_value.loading = False
        mock_import.return_value.use_query.return_value.error = True

        # EXECUTE FUNCTION
        result = utils.use_workspace(MOCK_USER)

        # EVALUATE RESULT
        assert isinstance(result, utils._PathsQuery)
        assert not result.checking_quota
        assert result.quota_exceeded
        mock_import.return_value.use_query.assert_called_once_with(
            utils._get_user_workspace,
            {"app_or_request": MOCK_APP, "user_or_request": MOCK_USER},
            postprocessor=None,
        )


@mock.patch("tethys_components.utils._infer_app_from_stack_trace")
def test_use_user_workspace_ready(mock_iafst):
    # SETUP ARGS/ENV
    mock_iafst.return_value = MOCK_APP
    with mock.patch("builtins.__import__") as mock_import:
        mock_import.return_value.use_query.return_value.loading = False
        mock_import.return_value.use_query.return_value.error = False

        # EXECUTE FUNCTION
        result = utils.use_workspace(MOCK_USER)

        # EVALUATE RESULT
        assert result == mock_import.return_value.use_query.return_value.data
        assert not result.checking_quota
        assert not result.quota_exceeded


@mock.patch("tethys_components.utils._infer_app_from_stack_trace")
def test_use_app_media_loading(mock_iafst):
    # SETUP ARGS/ENV
    mock_iafst.return_value = MOCK_APP
    with mock.patch("builtins.__import__") as mock_import:
        mock_import.return_value.use_query.return_value.loading = True

        # EXECUTE FUNCTION
        result = utils.use_media()

        # EVALUATE RESULT
        assert isinstance(result, utils._PathsQuery)
        assert result.checking_quota
        mock_import.return_value.use_query.assert_called_once_with(
            utils._get_app_media, {"app_or_request": MOCK_APP}, postprocessor=None
        )


@mock.patch("tethys_components.utils._infer_app_from_stack_trace")
def test_use_user_media_error(mock_iafst):
    # SETUP ARGS/ENV
    mock_iafst.return_value = MOCK_APP
    with mock.patch("builtins.__import__") as mock_import:
        mock_import.return_value.use_query.return_value.loading = False
        mock_import.return_value.use_query.return_value.error = True

        # EXECUTE FUNCTION
        result = utils.use_media(MOCK_USER)

        # EVALUATE RESULT
        assert isinstance(result, utils._PathsQuery)
        assert not result.checking_quota
        assert result.quota_exceeded
        mock_import.return_value.use_query.assert_called_once_with(
            utils._get_user_media,
            {"app_or_request": MOCK_APP, "user_or_request": MOCK_USER},
            postprocessor=None,
        )


@mock.patch("tethys_components.utils._infer_app_from_stack_trace")
def test_use_user_media_ready(mock_iafst):
    # SETUP ARGS/ENV
    mock_iafst.return_value = MOCK_APP
    with mock.patch("builtins.__import__") as mock_import:
        mock_import.return_value.use_query.return_value.loading = False
        mock_import.return_value.use_query.return_value.error = False

        # EXECUTE FUNCTION
        result = utils.use_media(MOCK_USER)

        # EVALUATE RESULT
        assert result == mock_import.return_value.use_query.return_value.data
        assert not result.checking_quota
        assert not result.quota_exceeded


@mock.patch("tethys_components.utils._infer_app_from_stack_trace")
def test_use_resources(mock_iafst):
    mock_iafst.return_value = MOCK_APP

    result = utils.use_resources()

    assert result == MOCK_APP.resources_path


@mock.patch("tethys_components.utils._infer_app_from_stack_trace")
def test_use_public(mock_iafst):
    mock_iafst.return_value = MOCK_APP

    result = utils.use_public()

    assert result == MOCK_APP.public_path


def test_background_execute_invalid_args():
    with pytest.raises(ValueError):
        utils.background_execute(lambda: None, "fail")


def test_background_execute_no_delay():
    def _test_func(arg1):
        pass

    with mock.patch("builtins.__import__") as mock_import:
        utils.background_execute(_test_func, ("Hello",))
        mock_import.return_value.Thread.assert_called_once_with(
            target=utils._background_execute_wrapper,
            args=(_test_func, ("Hello",), None),
        )
        mock_import.return_value.Thread().start.assert_called_once()


def test_background_execute_delay():
    def _test_func(arg1):
        pass

    with mock.patch("builtins.__import__") as mock_import:
        utils.background_execute(_test_func, ("Hello",), delay_seconds=10)
        mock_import.return_value.Timer.assert_called_once_with(
            interval=10,
            function=utils._background_execute_wrapper,
            args=(_test_func, ("Hello",), None),
        )
        mock_import.return_value.Timer().start.assert_called_once()


@mock.patch("tethys_components.utils.RepeatManager")
def test_background_execute_repeat(mock_repeat_manager):
    def _test_func(arg1):
        pass

    with mock.patch("builtins.__import__") as mock_import:
        utils.background_execute(_test_func, ("Hello",), repeat_seconds=1)
        mock_import.assert_not_called()
        mock_repeat_manager.assert_called_once_with(
            repeat_seconds=1,
            target=utils._background_execute_wrapper,
            args=(_test_func, ("Hello",), None),
        )


def test_props_all_cases_combined():
    expected = {"foo": "bar", "onClick": "test", "thisProp": "none"}
    value = utils.Props(foo_="bar", on_click="test", this_prop=None)

    assert value == expected


def test_get_layout_component_layout_callable():
    def _test_layout_func():
        pass

    assert utils._get_layout_component(MOCK_APP, _test_layout_func) == _test_layout_func


def test_get_layout_component_default_layout_callable():
    def _test_layout_func():
        pass

    MOCK_APP.default_layout = _test_layout_func
    assert utils._get_layout_component(MOCK_APP, "default") == MOCK_APP.default_layout


@mock.patch("tethys_components.utils.layouts")
def test_get_layout_component_default_layout_not_callable(mock_layouts):
    MOCK_APP.default_layout = "TestLayout"
    assert utils._get_layout_component(MOCK_APP, "default") == mock_layouts.TestLayout


@mock.patch("tethys_components.utils.layouts")
def test_get_layout_component_not_default_not_callable(mock_layouts):
    assert (
        utils._get_layout_component(MOCK_APP, "TestLayout") == mock_layouts.TestLayout
    )


def test_AttrDict_all_the_stops():
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

    assert hasattr(d, "camel_prop")
    assert isinstance(d.camel_prop, list)
    assert len(d.camel_prop) == 1
    assert isinstance(d.camel_prop[0], utils.DotNotationDict)
    assert hasattr(d.camel_prop[0], "list")
    assert d.camel_prop[0].list == "of"
    assert hasattr(d.camel_prop[0], "props")
    assert isinstance(d.camel_prop[0].props, list)
    assert len(d.camel_prop[0].props) == 3
    assert d.camel_prop[0].props[0] == "that"
    assert isinstance(d.camel_prop[0].props[1], utils.DotNotationDict)
    assert hasattr(d.camel_prop[0].props[1], "are")
    assert d.camel_prop[0].props[1].are == "all"
    assert d.camel_prop[0].props[2] == "very"
    assert hasattr(d.camel_prop[0], "differ_ent")
    assert isinstance(d.camel_prop[0].differ_ent, list)
    assert len(d.camel_prop[0].differ_ent) == 2
    assert isinstance(d.camel_prop[0].differ_ent[0], utils.DotNotationDict)
    assert isinstance(d.camel_prop[0].differ_ent[1], utils.DotNotationDict)
    assert hasattr(d.camel_prop[0].differ_ent[0], "types")
    assert d.camel_prop[0].differ_ent[0].types == "and"
    assert hasattr(d.camel_prop[0].differ_ent[1], "nesting")
    assert d.camel_prop[0].differ_ent[1].nesting == "orders"
    assert hasattr(d, "clear_")
    assert d.clear_ == "is reserved"
    assert hasattr(d, "update_")
    assert d.update_ == 100
    assert hasattr(d, "one_more")
    assert isinstance(d.one_more, utils.DotNotationDict)
    assert hasattr(d.one_more, "howbout")
    assert d.one_more.howbout == "this"
    with pytest.raises(AttributeError):
        d.not_there


def test_args_to_attrdicts_wrapper():
    @utils.args_to_dot_notation_dicts
    def _test_func(arg1, arg2, arg3):
        assert isinstance(arg1, utils.DotNotationDict)
        assert isinstance(arg2, utils.DotNotationDict)
        assert isinstance(arg3, str)

    _test_func({"this": "is", "a": "test"}, {"how": "about", "another": "one"}, "done")


def test_fetch_json_as_attrdict():
    with mock.patch("builtins.__import__") as mock_import:
        test_dict = {"this": "is", "a": "test"}
        mock_import.return_value.get.return_value.json.return_value = test_dict
        test_url = "test-url"

        data = utils.fetch_json(test_url)

        mock_import.return_value.get.assert_called_once_with(test_url)
        assert isinstance(data, utils.DotNotationDict)
        assert data.this == "is"
        assert data.a == "test"


def test_fetch_json_not_attrdict():
    with mock.patch("builtins.__import__") as mock_import:
        test_dict = {"this": "is", "a": "test"}
        mock_import.return_value.get.return_value.json.return_value = test_dict
        test_url = "test-url"

        data = utils.fetch_json(test_url, as_attr_dict=False)

        mock_import.return_value.get.assert_called_once_with(test_url)
        assert data == test_dict


def test_fetch():
    with mock.patch("builtins.__import__") as mock_import:
        test_content = "this is a test"
        mock_import.return_value.get.return_value.text = test_content
        test_url = "test-url"

        data = utils.fetch(test_url)

        mock_import.return_value.get.assert_called_once_with(test_url)
        assert data == test_content


def test_transform_coordinate():
    coordinate = [0, 0]
    src_proj = "EPSG:3857"
    target_proj = "EPSG:4326"

    with mock.patch("builtins.__import__") as mock_import:
        result = utils.transform_coordinate(coordinate, src_proj, target_proj)

    assert (
        mock_import.return_value.Transformer.from_crs.return_value.transform.return_value
        == result
    )
    mock_import.return_value.CRS.assert_has_calls(
        [mock.call(src_proj), mock.call(target_proj)]
    )


def test_transform_coordinate_custom_projections():
    coordinate = [0, 0]
    src_proj = {"definition": "test src proj"}
    target_proj = {"definition": "test src proj"}

    with mock.patch("builtins.__import__") as mock_import:
        result = utils.transform_coordinate(coordinate, src_proj, target_proj)

    assert (
        mock_import.return_value.Transformer.from_crs.return_value.transform.return_value
        == result
    )
    mock_import.return_value.CRS.assert_has_calls(
        [mock.call(src_proj["definition"]), mock.call(target_proj["definition"])]
    )


def test_transform_coordinate_invalid_src_proj():
    coordinate = [0, 0]
    src_proj = 1234
    target_proj = {"definition": "test src proj"}

    with mock.patch("builtins.__import__"), pytest.raises(ValueError):
        utils.transform_coordinate(coordinate, src_proj, target_proj)


def test_transform_coordinate_invalid_target_proj():
    coordinate = [0, 0]
    src_proj = {"definition": "test src proj"}
    target_proj = 1234

    with mock.patch("builtins.__import__"), pytest.raises(ValueError):
        utils.transform_coordinate(coordinate, src_proj, target_proj)


def test_get_db_object():
    app = mock.MagicMock(db_object="expected")
    val = utils._get_db_object(app)
    assert val == "expected"


def test_background_execute_wrapper():
    test_func = mock.MagicMock()
    test_func.return_value = "Test"
    callback = mock.MagicMock()

    utils._background_execute_wrapper(test_func, ("Hello",), callback)
    test_func.assert_called_once_with("Hello")
    callback.assert_called_once_with("Test")


def test_repeat_manager_start_and_cancel():
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
        assert called_kwargs.get("interval") == 2
        assert callable(called_kwargs.get("function"))

        # is_alive should be True after start
        assert rm.is_alive()

        # Cancel should stop the repeating timer
        rm.cancel()
        mock_timer.cancel.assert_called_once()
        assert not rm.is_alive()


def test_repeat_manager_repeat_schedules_timer_again():
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
        assert id(rm._timer) == id(mock_timer)


def test_get_legend_url_invalid_tag():
    vdom = {"tagName": "Div", "attributes": {}}
    with pytest.raises(ValueError):
        utils._get_legend_url_(vdom)


def test_get_legend_url_single_layer_list_returns_none():
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
        assert result is None
        mock_print.assert_called_with("NOT SINGLE LAYER")


def test_get_legend_url_basic_with_layer_and_no_resolution():
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
        assert isinstance(url, str)
        assert "GetLegendGraphic" in url
        assert "LAYER=layer1" in url


def test_get_legend_url_basic_with_single_layer_in_layers():
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
        assert isinstance(url, str)
        assert "GetLegendGraphic" in url
        assert "LAYER=layer1" in url


def test_get_legend_url_with_resolution_and_scale():
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

    assert isinstance(result, str)
    assert "GetLegendGraphic" in result
    assert "SCALE=" in result


def test_get_feature_info_url_invalid_tag():
    vdom = {"tagName": "Div", "attributes": {}}
    with pytest.raises(ValueError):
        utils._get_feature_info_url_(vdom, [0, 0], 1, "EPSG:3857", "EPSG:3857")


def test_get_feature_info_url_not_implemented_for_diff_projections():
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
        with pytest.raises(NotImplementedError):
            # map_proj != layer_proj triggers NotImplementedError
            utils._get_feature_info_url_(vdom, [0, 0], 1, "EPSG:3857", "EPSG:4326")


def test_get_feature_info_url_success():
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

    assert isinstance(feature_url, str)
    assert "GetFeatureInfo" in feature_url
    assert "I=" in feature_url
    assert "J=" in feature_url


def test_find_by_tag_various_structures():
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
    assert len(found) == 2

    # Top-level list input
    found_list = utils.find_by_tag(
        [tree, {"tagName": "target", "children": []}], "target"
    )
    assert len(found_list) == 3

    # Non-element input returns empty list
    assert utils.find_by_tag("not an element", "target") == []


def test_ol_manager_attribute_chaining_and_call():
    base = utils.OlManager("ol")

    # Accessing an attribute should return a new OlManager with dotted attr
    src = base.source
    assert isinstance(src, utils.OlManager)
    assert src.attr == "ol.source"

    # Chaining attributes should build dotted names
    chained = base.layer.tile
    assert chained.attr == "ol.layer.tile"

    # Accessed attributes are cached on the instance
    assert base.source is src

    # Calling returns a dict with type and provided kwargs
    res = src(foo="bar")
    assert isinstance(res, dict)
    assert res["type"] == "ol.source"
    assert res["foo"] == "bar"


def test_ol_manager_geom_arg_handling():
    # When the attr contains 'ol.geom' and a single positional arg is given,
    # the call should place that arg into the 'geom' kwarg
    geom_mgr = utils.OlManager("ol.geom")

    out = geom_mgr("POINT(1 2)")
    assert out["type"] == "ol.geom"
    assert out["geom"] == "POINT(1 2)"

    # If kwargs already provide geom it should be preserved/overridden by call logic
    out2 = geom_mgr("POINT(3 4)", geom="override")
    # __call__ will still set geom from args when args present
    assert out2["geom"] == "POINT(3 4)"

    # For non-geom managers, positional args are ignored and only kwargs are returned
    mgr = utils.OlManager("ol.someType")
    out3 = mgr(1, 2, foo="baz")
    assert out3["type"] == "ol.someType"
    assert out3["foo"] == "baz"
