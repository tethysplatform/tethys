from unittest import mock
import unittest
import tethys_gizmos.templatetags.tethys_gizmos as gizmos_templatetags
from tethys_gizmos.gizmo_options.base import TethysGizmoOptions
from datetime import datetime, date
from django.template import base
from django.template import TemplateSyntaxError
from django.template import Context
from importlib import reload
from pathlib import Path
import sys


class CustomGizmo(TethysGizmoOptions):
    gizmo_name = "test_gizmo"

    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name

    @staticmethod
    def get_vendor_js():
        return (
            "https://cdn.jsdelivr.net/gh/openlayers/openlayers.github.io@master/en/v6.9.0/ol.min.js",
            "://plotly-load_from_python.js",
        )

    @staticmethod
    def get_gizmo_js():
        return (str(Path("tethys_gizmos/js/tethys_map_view.js")),)

    @staticmethod
    def get_vendor_css():
        return (
            "https://cdn.jsdelivr.net/gh/openlayers/openlayers.github.io@master/en/v6.9.0/ol.min.css",
        )

    @staticmethod
    def get_gizmo_css():
        return (str(Path("tethys_gizmos/css/tethys_map_view.min.css")),)

    @staticmethod
    def get_gizmo_modals():
        return ("<modals>",)


class TestTethysGizmos(unittest.TestCase):
    def setUp(self):
        self.gizmo_name = "tethysext.test_extension"
        pass

    def tearDown(self):
        pass

    @mock.patch("tethys_apps.harvester.SingletonHarvester")
    def test_TestTethysGizmos(self, mock_harvest):
        mock_harvest().extension_modules = {
            "Test Extension": "tethysext.test_extension"
        }
        gizmos_templatetags.EXTENSION_PATH_MAP = {}
        reload(gizmos_templatetags)
        self.assertIn("custom_select_input", gizmos_templatetags.EXTENSION_PATH_MAP)

    @mock.patch("tethys_apps.harvester.SingletonHarvester")
    def test_TestTethysGizmos_import_error(self, mock_harvest):
        mock_harvest().extension_modules = {
            "Test Extension": "tethysext.test_extension1"
        }
        reload(gizmos_templatetags)
        # self.assertRaises(ImportError, reload, gizmos_templatetags)

    def test_HighchartsDateEncoder(self):
        result = gizmos_templatetags.HighchartsDateEncoder().default(
            datetime(2018, 1, 1)
        )

        # Timestamp should be 1514764800
        expected = 1514790000000.0 if sys.platform == "win32" else 1514764800000.0
        self.assertEqual(expected, result)

    def test_HighchartsDateEncoder_no_dt(self):
        result = gizmos_templatetags.HighchartsDateEncoder().default(date(2018, 1, 1))

        # Check Result
        self.assertEqual("2018-01-01", result)

    def test_SetVarNode_template_error(self):
        node = gizmos_templatetags.SetVarNode("test", "test")
        result = node.render({})
        self.assertEqual("", result)

    @mock.patch("tethys_gizmos.templatetags.tethys_gizmos.template.Variable")
    def test_SetVarNode_render(self, mock_template_var):
        mock_Variable = mock.MagicMock()
        mock_Variable.resolve.return_value = "foo"
        mock_template_var.return_value = mock_Variable
        context = {"test1": {}}
        node = gizmos_templatetags.SetVarNode("test1.test", "test")
        result = node.render(context)
        self.assertDictEqual(context, {"test1": {"test": "foo"}})

        self.assertEqual("", result)

    @mock.patch("tethys_gizmos.templatetags.tethys_gizmos.SetVarNode")
    def test_set_var(self, _):
        token = mock.MagicMock()
        token.split_contents.return_value = ["set", "test", "=", "tests"]
        gizmos_templatetags.set_var(None, token)

    def test_set_var_error(self):
        token = mock.MagicMock()
        self.assertRaises(TemplateSyntaxError, gizmos_templatetags.set_var, None, token)

    def test_isstring(self):
        result = gizmos_templatetags.isstring(type("string"))

        # Check Result
        self.assertTrue(result)

        result = gizmos_templatetags.isstring(type(["list"]))

        # Check Result
        self.assertFalse(result)

    def test_return_item(self):
        result = gizmos_templatetags.return_item(["0", "1"], 1)

        # Check Result
        self.assertEqual("1", result)

    def test_return_item_none(self):
        result = gizmos_templatetags.return_item(["0", "1"], 2)

        # Check Result
        self.assertFalse(result)

    def test_json_date_handler(self):
        result = gizmos_templatetags.json_date_handler(datetime(2018, 1, 1))

        # Timestamp should be 1514764800
        expected = 1514790000000.0 if sys.platform == "win32" else 1514764800000.0
        self.assertEqual(expected, result)

    def test_json_date_handler_no_datetime(self):
        result = gizmos_templatetags.json_date_handler("2018")

        # Check Result
        self.assertEqual("2018", result)

    def test_jsonify(self):
        data = ["foo", {"bar": ("baz", None, 1.0, 2)}]

        result = gizmos_templatetags.jsonify(data)

        # Check Result
        self.assertEqual('["foo", {"bar": ["baz", null, 1.0, 2]}]', result)

    def test_divide(self):
        value = 10
        divisor = 2
        expected_result = 5

        result = gizmos_templatetags.divide(value, divisor)

        # Check Result
        self.assertEqual(expected_result, result)


class TestTethysGizmoIncludeDependency(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_load_gizmo_name(self):
        gizmo_name = '"plotly_view"'
        # _load_gizmo_name is loaded in init
        result = gizmos_templatetags.TethysGizmoIncludeDependency(gizmo_name=gizmo_name)

        # Check result
        self.assertEqual("plotly_view", result.gizmo_name)

    def test_load_gizmos_rendered(self):
        gizmo_name = "plotly_view"
        context = {}

        # _load_gizmos_rendered is loaded in render
        gizmos_templatetags.TethysGizmoIncludeDependency(gizmo_name=gizmo_name).render(
            context=context
        )

        self.assertEqual(["plotly_view"], context["gizmos_rendered"])

    @mock.patch("tethys_gizmos.templatetags.tethys_gizmos.settings")
    def test_load_gizmos_rendered_syntax_error(self, mock_settings):
        mock_settings.return_value = mock.MagicMock(TEMPLATE_DEBUG=True)
        gizmo_name = "plotly_view1"
        context = {}

        t = gizmos_templatetags.TethysGizmoIncludeDependency(gizmo_name=gizmo_name)

        self.assertRaises(TemplateSyntaxError, t.render, context=context)


class TestTethysGizmoIncludeNode(unittest.TestCase):
    def setUp(self):
        self.gizmo_name = "tethysext.test_extension"
        pass

    def tearDown(self):
        pass

    def test_render(self):
        gizmos_templatetags.GIZMO_NAME_MAP[CustomGizmo.gizmo_name] = CustomGizmo
        result = gizmos_templatetags.TethysGizmoIncludeNode(
            options="foo", gizmo_name=CustomGizmo.gizmo_name
        )

        context = {"foo": CustomGizmo(name="test_render")}
        result_render = result.render(context)

        # Check Result
        self.assertEqual("test_render", result_render)

    def test_render_no_gizmo_name(self):
        result = gizmos_templatetags.TethysGizmoIncludeNode(
            options="foo", gizmo_name=None
        )

        context = {"foo": CustomGizmo(name="test_render_no_name")}
        result_render = result.render(context)

        # Check Result
        self.assertEqual("test_render_no_name", result_render)

    @mock.patch("tethys_gizmos.templatetags.tethys_gizmos.get_template")
    def test_render_in_extension_path(self, mock_gt):
        # Reset EXTENSION_PATH_MAP
        gizmos_templatetags.EXTENSION_PATH_MAP = {
            CustomGizmo.gizmo_name: "tethys_gizmos"
        }
        mock_gt.return_value = mock.MagicMock()
        result = gizmos_templatetags.TethysGizmoIncludeNode(
            options="foo", gizmo_name=CustomGizmo.gizmo_name
        )
        context = Context({"foo": CustomGizmo(name="test_render")})
        result.render(context)

        # Check Result
        mock_gt.assert_called_with(
            str(Path("tethys_gizmos/templates/gizmos/test_gizmo.html"))
        )

        # We need to delete this extension path map to avoid template not exist error on the
        # previous test
        del gizmos_templatetags.EXTENSION_PATH_MAP[CustomGizmo.gizmo_name]

    @mock.patch("tethys_gizmos.templatetags.tethys_gizmos.settings")
    @mock.patch("tethys_gizmos.templatetags.tethys_gizmos.template")
    def test_render_syntax_error_debug(self, mock_template, mock_setting):
        mock_resolve = mock_template.Variable().resolve()
        mock_resolve.return_value = mock.MagicMock()
        del mock_resolve.gizmo_name
        mock_setting.TEMPLATES = [{"OPTIONS": {"debug": True}}]

        context = Context({"foo": CustomGizmo(name="test_render")})
        tgin = gizmos_templatetags.TethysGizmoIncludeNode(
            options="foo", gizmo_name="not_gizmo"
        )

        self.assertRaises(TemplateSyntaxError, tgin.render, context=context)

    @mock.patch("tethys_gizmos.templatetags.tethys_gizmos.settings")
    @mock.patch("tethys_gizmos.templatetags.tethys_gizmos.template")
    def test_render_syntax_error_no_debug(self, mock_template, mock_setting):
        mock_resolve = mock_template.Variable().resolve()
        mock_resolve.return_value = mock.MagicMock()
        del mock_resolve.gizmo_name
        mock_setting.TEMPLATES = [{"OPTIONS": {"debug": False}}]

        context = Context({"foo": CustomGizmo(name="test_render")})

        result = gizmos_templatetags.TethysGizmoIncludeNode(
            options="foo", gizmo_name=CustomGizmo.gizmo_name
        )
        self.assertEqual("", result.render(context=context))


class TestTags(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch("tethys_gizmos.templatetags.tethys_gizmos.TethysGizmoIncludeNode")
    def test_gizmo(self, mock_tgin):
        token1 = base.Token(token_type="TOKEN_TEXT", contents="token test_options")
        gizmos_templatetags.gizmo(parser="", token=token1)

        # Check Result
        mock_tgin.assert_called_with("test_options", None)

        token2 = base.Token(
            token_type="TOKEN_TEXT", contents="token test_gizmo_name test_options"
        )
        gizmos_templatetags.gizmo(parser="", token=token2)

        # Check Result
        mock_tgin.assert_called_with("test_options", "test_gizmo_name")

    def test_gizmo_syntax_error(self):
        token = base.Token(token_type="TOKEN_TEXT", contents="token")

        # Check Error
        self.assertRaises(
            TemplateSyntaxError, gizmos_templatetags.gizmo, parser="", token=token
        )

    @mock.patch("tethys_gizmos.templatetags.tethys_gizmos.TethysGizmoIncludeDependency")
    def test_import_gizmo_dependency(self, mock_tgid):
        token = base.Token(
            token_type="TOKEN_TEXT", contents="test_tag_name test_gizmo_name"
        )

        gizmos_templatetags.import_gizmo_dependency(parser="", token=token)
        # Check Result
        mock_tgid.assert_called_with("test_gizmo_name")

    def test_import_gizmo_dependency_syntax_error(self):
        token = base.Token(token_type="TOKEN_TEXT", contents="token")

        self.assertRaises(
            TemplateSyntaxError,
            gizmos_templatetags.import_gizmo_dependency,
            parser="",
            token=token,
        )

    @mock.patch("tethys_gizmos.templatetags.tethys_gizmos.TethysGizmoDependenciesNode")
    def test_gizmo_dependencies(self, mock_tgdn):
        token = base.Token(token_type="TOKEN_TEXT", contents='token "css"')
        gizmos_templatetags.gizmo_dependencies(parser="", token=token)

        # Check Result
        mock_tgdn.assert_called_with("css")

    def test_gizmo_dependencies_syntax_error(self):
        token = base.Token(token_type="TOKEN_TEXT", contents="token css js")
        self.assertRaises(
            TemplateSyntaxError,
            gizmos_templatetags.gizmo_dependencies,
            parser="",
            token=token,
        )

    def test_gizmo_dependencies_not_valid(self):
        token = base.Token(token_type="TOKEN_TEXT", contents="token css1")
        self.assertRaises(
            TemplateSyntaxError,
            gizmos_templatetags.gizmo_dependencies,
            parser="",
            token=token,
        )


class TestTethysGizmoDependenciesNode(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch(
        "tethys_gizmos.templatetags.tethys_gizmos.get_plotlyjs",
        return_value="PLOTLY_JAVASCRIPT",
    )
    def test_render_global_js(self, mock_get_plotlyjs):
        gizmos_templatetags.GIZMO_NAME_MAP[CustomGizmo.gizmo_name] = CustomGizmo
        output_global_js = "global_js"
        result = gizmos_templatetags.TethysGizmoDependenciesNode(
            output_type=output_global_js
        )

        # Check result
        self.assertEqual(output_global_js, result.output_type)

        # TEST render
        context = Context({"foo": CustomGizmo(name="test_render")})
        context.update({"gizmos_rendered": []})

        # unless it has the same gizmo name as the predefined one
        render_globaljs = gizmos_templatetags.TethysGizmoDependenciesNode(
            output_type=output_global_js
        ).render(context=context)

        # Check Vendor JS
        mock_get_plotlyjs.assert_called()
        self.assertIn(
            "https://cdn.jsdelivr.net/gh/openlayers/openlayers.github.io@master/en/v6.9.0/ol.min.js",
            render_globaljs,
        )
        self.assertIn("PLOTLY_JAVASCRIPT", render_globaljs)
        self.assertNotIn("tethys_map_view.js", render_globaljs)

    def test_render_global_css(self):
        gizmos_templatetags.GIZMO_NAME_MAP[CustomGizmo.gizmo_name] = CustomGizmo
        output_global_css = "global_css"
        result = gizmos_templatetags.TethysGizmoDependenciesNode(
            output_type=output_global_css
        )

        # Check result
        self.assertEqual(output_global_css, result.output_type)

        # TEST render
        context = Context({"foo": CustomGizmo(name="test_render")})
        context.update({"gizmos_rendered": []})

        # unless it has the same gizmo name as the predefined one
        render_globalcss = gizmos_templatetags.TethysGizmoDependenciesNode(
            output_type=output_global_css
        ).render(context=context)

        # Check Vendor CSS
        self.assertIn(
            "https://cdn.jsdelivr.net/gh/openlayers/openlayers.github.io@master/en/v6.9.0/ol.min.css",
            render_globalcss,
        )
        self.assertNotIn("tethys_map_view.min.css", render_globalcss)
        self.assertNotIn("tethys_gizmos.css", render_globalcss)

    def test_render_css(self):
        gizmos_templatetags.GIZMO_NAME_MAP[CustomGizmo.gizmo_name] = CustomGizmo
        output_css = "css"
        result = gizmos_templatetags.TethysGizmoDependenciesNode(output_type=output_css)

        # Check result
        self.assertEqual(output_css, result.output_type)

        # TEST render
        context = Context({"foo": CustomGizmo(name="test_render")})
        context.update({"gizmos_rendered": []})

        # unless it has the same gizmo name as the predefined one
        render_css = gizmos_templatetags.TethysGizmoDependenciesNode(
            output_type=output_css
        ).render(context=context)

        # Check Gizmo CSS
        self.assertIn("tethys_map_view.min.css", render_css)
        self.assertIn("tethys_gizmos.css", render_css)
        self.assertNotIn("ol.min.css", render_css)

    @mock.patch(
        "tethys_gizmos.templatetags.tethys_gizmos.get_plotlyjs",
        return_value="PLOTLY_JAVASCRIPT",
    )
    def test_render_js(self, mock_get_plotlyjs):
        gizmos_templatetags.GIZMO_NAME_MAP[CustomGizmo.gizmo_name] = CustomGizmo
        output_js = "js"
        result = gizmos_templatetags.TethysGizmoDependenciesNode(output_type=output_js)

        # Check result
        self.assertEqual(output_js, result.output_type)

        # TEST render
        context = Context({"foo": CustomGizmo(name="test_render")})
        context.update({"gizmos_rendered": []})

        # unless it has the same gizmo name as the predefined one
        render_js = gizmos_templatetags.TethysGizmoDependenciesNode(
            output_type=output_js
        ).render(context=context)

        # Check Gizmo JS
        mock_get_plotlyjs.assert_not_called()
        self.assertIn("tethys_map_view.js", render_js)
        self.assertIn("tethys_gizmos.js", render_js)
        self.assertNotIn("ol.min.js", render_js)
        self.assertNotIn("PLOTLY_JAVASCRIPT", render_js)

    def test_render_modals(self):
        gizmos_templatetags.GIZMO_NAME_MAP[CustomGizmo.gizmo_name] = CustomGizmo
        output_type = "modals"
        result = gizmos_templatetags.TethysGizmoDependenciesNode(
            output_type=output_type
        )

        # Check result
        self.assertEqual(output_type, result.output_type)

        # TEST render
        context = Context({"foo": CustomGizmo(name="test_render")})
        context.update({"gizmos_rendered": []})

        # unless it has the same gizmo name as the predefined one
        render_modals = result.render(context=context)

        # Check Gizmo CSS
        self.assertIn("<modals>", render_modals)

    def test_codify(self):
        result = gizmos_templatetags.codify("Test Name")
        self.assertEqual(result, "test-name")
