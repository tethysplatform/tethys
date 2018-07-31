import unittest
import tethys_gizmos.templatetags.tethys_gizmos as gizmos_templatetags
import mock
from datetime import datetime, date
from django.template import base
from django.template import TemplateSyntaxError

class TestTethysGizmos(unittest.TestCase):
    def setUp(self):
        self.gizmo_name = 'tethysext.test_extension'
        pass

    def tearDown(self):
        pass

    # @mock.patch('tethys_gizmos.templatetags.tethys_gizmos.SingletonHarvester')
    @mock.patch('tethys_apps.harvester.SingletonHarvester')
    def test_TestTethysGizmos(self, mock_harvest):
        mock_harvest().extension_modules = {'Test Extension': 'tethysext.test_extension'}
        gizmos_templatetags.EXTENSION_PATH_MAP = {}
        reload(gizmos_templatetags)
        self.assertIn('custom_select_input', gizmos_templatetags.EXTENSION_PATH_MAP)

    @mock.patch('tethys_apps.harvester.SingletonHarvester')
    def test_TestTethysGizmos_import_error(self, mock_harvest):
        mock_harvest().extension_modules = {'Test Extension': 'tethysext.test_extension1'}
        reload(gizmos_templatetags)
        # self.assertRaises(ImportError, reload, gizmos_templatetags)

    def test_HighchartsDateEncoder(self):
        result = gizmos_templatetags.HighchartsDateEncoder().default(datetime(2018, 01, 01))

        # Timestamp should be 1514764800
        self.assertEqual(1514764800000.0, result)

    def test_HighchartsDateEncoder_no_dt(self):
        result = gizmos_templatetags.HighchartsDateEncoder().default(date(2018, 01, 01))

        # Check Result
        self.assertEqual('2018-01-01', result)

    def test_isstring(self):
        result = gizmos_templatetags.isstring(type('string'))

        # Check Result
        self.assertTrue(result)

        result = gizmos_templatetags.isstring(type(['list']))

        # Check Result
        self.assertFalse(result)

    def test_return_item(self):
        result = gizmos_templatetags.return_item(['0', '1'], 1)

        # Check Result
        self.assertEqual('1', result)

    def test_return_item_none(self):
        result = gizmos_templatetags.return_item(['0', '1'], 2)

        # Check Result
        self.assertFalse(result)

    def test_json_date_handler(self):
        result = gizmos_templatetags.json_date_handler(datetime(2018, 01, 01))

        # Timestamp should be 1514764800
        self.assertEqual(1514764800000.0, result)

    def test_json_date_handler_no_datetime(self):
        result = gizmos_templatetags.json_date_handler('2018')

        # Check Result
        self.assertEqual('2018', result)

    def test_jsonify(self):
        data = ['foo', {'bar': ('baz', None, 1.0, 2)}]

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

    def test_TethysGizmoIncludeDependency(self):
        gizmo_name = '"plotly_view"'
        context = {}
        gizmos_templatetags.TethysGizmoIncludeDependency(gizmo_name=gizmo_name)
        gizmos_templatetags.TethysGizmoIncludeDependency(gizmo_name=gizmo_name).render(context=context)

        self.assertEqual(['plotly_view'], context['gizmos_rendered'])

    @mock.patch('tethys_gizmos.templatetags.tethys_gizmos.settings')
    def test_TethysGizmoIncludeDependency_syntax_error(self, mock_settings):
        mock_settings.return_value = mock.MagicMock(TEMPLATE_DEBUG=True)
        gizmo_name = 'plotly_view1'
        context = {}
        tethysGizmos_dependency = gizmos_templatetags.TethysGizmoIncludeDependency(gizmo_name=gizmo_name)

        self.assertRaises(TemplateSyntaxError, tethysGizmos_dependency.render, context=context)

    def test_TethysGizmoIncludeNode(self):
        gizmo_name = '"plotly_view"'
        result = gizmos_templatetags.TethysGizmoIncludeNode(options='gizmo_name', gizmo_name='date_picker2')

        # Check Result
        self.assertIsInstance(result, gizmos_templatetags.TethysGizmoIncludeNode)

        context = {'gizmo_name': {'gizmo_name': 'date_picker'}}
        # result.render(context)

        # TODO: Ask Nathan how resolved_options has attribute

    def test_gizmo(self):
        token1 = base.Token(token_type='TOKEN_TEXT', contents='token test_options')
        result = gizmos_templatetags.gizmo(parser='', token=token1)
        # Check Result
        self.assertIsInstance(result, gizmos_templatetags.TethysGizmoIncludeNode)
        self.assertEqual('test_options', result.options)
        self.assertFalse(result.gizmo_name)

        token2 = base.Token(token_type='TOKEN_TEXT', contents='token test_gizmo_name test_options')
        result = gizmos_templatetags.gizmo(parser='', token=token2)
        # Check Result
        self.assertIsInstance(result, gizmos_templatetags.TethysGizmoIncludeNode)
        self.assertEqual('test_options', result.options)
        self.assertEqual('test_gizmo_name', result.gizmo_name)

    def test_gizmo_syntax_error(self):
        token = base.Token(token_type='TOKEN_TEXT', contents='token')

        # Check Error
        self.assertRaises(TemplateSyntaxError, gizmos_templatetags.gizmo, parser='', token=token)

    def test_import_gizmo_dependency(self):
        token = base.Token(token_type='TOKEN_TEXT', contents='test_tag_name test_gizmo_name')

        result = gizmos_templatetags.import_gizmo_dependency(parser='', token=token)
        # Check Result
        self.assertIsInstance(result, gizmos_templatetags.TethysGizmoIncludeDependency)
        self.assertEqual('test_gizmo_name', result.gizmo_name)

    def test_import_gizmo_dependency_syntax_error(self):
        token = base.Token(token_type='TOKEN_TEXT', contents='token')

        self.assertRaises(TemplateSyntaxError, gizmos_templatetags.import_gizmo_dependency,
                          parser='', token=token)

    def test_TethysGizmoDependenciesNode(self):
        output_type = 'html'
        result = gizmos_templatetags.TethysGizmoDependenciesNode(output_type=output_type)

        # Check result
        self.assertEqual(output_type, result.output_type)

        dependency_list = ['http://depend1', 'depend2', 'depend3']
        dependency = 'http://depend1'

        # TEST _append_dependency
        # Dependency in list
        result = result._append_dependency(dependency=dependency, dependency_list=dependency_list)

        # Dependency not in list
        dependency = 'gizmo_name'
        result = gizmos_templatetags.TethysGizmoDependenciesNode(output_type=output_type)
        result._append_dependency(dependency=dependency, dependency_list=dependency_list)

        # TEST render
        from django.template import Context
        context = Context({'gizmo_name': 'date_picker2'})
        # context = {'gizmo_name': {'gizmo_name': 'date_picker2'}}
        # result.render(context=context)

    def test_gizmo_dependencies(self):
        token = base.Token(token_type='TOKEN_TEXT', contents='token "css"')

        result = gizmos_templatetags.gizmo_dependencies(parser='', token=token)

        # Check Result
        self.assertIsInstance(result, gizmos_templatetags.TethysGizmoDependenciesNode)
        self.assertEqual('css', result.output_type)

    def test_gizmo_dependencies_syntax_error(self):
        token = base.Token(token_type='TOKEN_TEXT', contents='token css js')
        self.assertRaises(TemplateSyntaxError, gizmos_templatetags.gizmo_dependencies,
                          parser='', token=token)

    def test_gizmo_dependencies_not_valid(self):
        token = base.Token(token_type='TOKEN_TEXT', contents='token css1')
        self.assertRaises(TemplateSyntaxError, gizmos_templatetags.gizmo_dependencies,
                          parser='', token=token)

