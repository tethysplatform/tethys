from unittest import mock
from django.test import RequestFactory, TestCase

from tethys_gizmos.gizmo_options import MVView
from tethys_layouts.views.map_layout import MapLayout
from tethys_layouts.exceptions import TethysLayoutPropertyException


class TestTethysLayout(TestCase):
    def setUp(self):
        self.inst = MapLayout()
        self.factory = RequestFactory()

    def tearDown(self):
        pass

    def test_default_props(self):
        inst = MapLayout()
        self.assertEqual(inst.template_name, 'tethys_layouts/map_layout/map_layout.html')
        self.assertListEqual(inst.http_method_names, ['get', 'post'])
        self.assertEqual(inst._geocode_endpoint, 'http://api.opencagedata.com/geocode/v1/geojson')
        self.assertEqual(inst.map_subtitle, '')
        self.assertEqual(inst.map_title, '')
        self.assertListEqual(inst.basemaps, [
            'Stamen',
            {'Stamen': {'layer': 'toner', 'control_label': 'Black and White'}},
            'OpenStreetMap',
            'ESRI',
        ])
        self.assertIsNone(inst.cesium_ion_token)
        self.assertListEqual(inst.default_center, [-98.583, 39.833])
        self.assertFalse(inst.default_disable_basemap)
        self.assertIsNone(inst.geocode_api_key)
        self.assertFalse(inst.enforce_permissions)
        self.assertIsNone(inst.geocode_extent)
        self.assertEqual(inst.geoserver_workspace, '')
        self.assertListEqual(inst.initial_map_extent, [-65.69, 23.81, -129.17, 49.38])
        self.assertFalse(inst.feature_selection_multiselect)
        self.assertEqual(inst.feature_selection_sensitivity, 4)
        self.assertEqual(inst.layer_tab_name, 'Layers')
        self.assertEqual(inst.map_type, 'tethys_map_view')
        self.assertEqual(inst.max_zoom, 28)
        self.assertEqual(inst.min_zoom, 0)
        self.assertFalse(inst.plot_slide_sheet)
        self.assertEqual(inst.plotly_version, '2.3.0')
        self.assertEqual(inst.sds_setting_name, '')
        self.assertFalse(inst.show_custom_layer)
        self.assertFalse(inst.show_legends)
        self.assertFalse(inst.show_map_clicks)
        self.assertFalse(inst.show_map_click_popup)
        self.assertFalse(inst.show_properties_popup)
        self.assertFalse(inst.show_public_toggle)
        self.assertFalse(inst.wide_nav)

    def test_map_extent(self):
        ret = MapLayout.map_extent
        self.assertListEqual(ret, [-65.69, 23.81, -129.17, 49.38])

    def test_default_view(self):
        ret = MapLayout.default_view
        self.assertIsInstance(ret, MVView)
        self.assertDictEqual(ret, {
            'center': [-97.42999999999999, 36.595],
            'maxZoom': 28,
            'minZoom': 0,
            'projection': 'EPSG:4326',
            'zoom': 4
        })

    def test_sds_setting(self):
        mock_app = mock.MagicMock()

        class SdsMapLayout(MapLayout):
            app = mock_app
            sds_setting_name = 'foo'

        ret = SdsMapLayout.sds_setting
        mock_app.get_spatial_dataset_service.assert_called_with('foo')
        self.assertEqual(ret, mock_app.get_spatial_dataset_service('foo'))

    def test_sds_setting_no_name(self):
        mock_app = mock.MagicMock()

        class NoSdsNameMapLayout(MapLayout):
            app = mock_app
            sds_setting_name = ''

        with self.assertRaises(TethysLayoutPropertyException) as cm:
            NoSdsNameMapLayout.sds_setting

        self.assertEqual(
            str(cm.exception),
            'You must define the "sds_setting_name" property on your MapLayout class to use this feature.'
        )

    def test_sds_setting_no_app(self):
        class NoAppNameMapLayout(MapLayout):
            app = None
            sds_setting_name = 'foo'

        with self.assertRaises(TethysLayoutPropertyException) as cm:
            NoAppNameMapLayout.sds_setting

        self.assertEqual(
            str(cm.exception),
            'You must define the "app" property on your MapLayout class to use this feature.'
        )

    def test_compose_layers(self):
        mock_request = mock.MagicMock()
        mock_map_view = mock.MagicMock()
        inst = MapLayout()
        ret = inst.compose_layers(mock_request, mock_map_view)
        self.assertListEqual(ret, list())

    def test_get_initial_map_extent(self):
        class ExtentMapLayout(MapLayout):
            initial_map_extent = [-123.4, -234.5, 345.6, 456.7]

        ret = ExtentMapLayout.get_initial_map_extent()
        self.assertListEqual(ret, [-123.4, -234.5, 345.6, 456.7])

    def test_get_plot_for_layer_feature(self):
        mock_request = mock.MagicMock()
        inst = MapLayout()
        plot_title, data, layout = inst.get_plot_for_layer_feature(mock_request, 'Foo', '12345')
        self.assertEqual(plot_title, 'Undefined')
        self.assertListEqual(data, [{
            'name': '12345',
            'mode': 'lines',
            'x': [1, 2, 3, 4],
            'y': [10, 15, 13, 17],
        }])
        self.assertDictEqual(layout, {
            'xaxis': {
                'title': 'Foo'
            },
            'yaxis': {
                'title': 'Undefined'
            }
        })

    def test_get_vector_style_map(self):
        ret = MapLayout.get_vector_style_map()
        self.assertDictEqual(ret, {
            'Point': {'ol.style.Style': {
                'image': {'ol.style.Circle': {
                    'radius': 5,
                    'fill': {'ol.style.Fill': {
                        'color': 'navy',
                    }},
                    'stroke': {'ol.style.Stroke': {
                        'color': 'navy',
                    }}
                }}
            }},
            'LineString': {'ol.style.Style': {
                'stroke': {'ol.style.Stroke': {
                    'color': 'navy',
                    'width': 2
                }}
            }},
            'Polygon': {'ol.style.Style': {
                'stroke': {'ol.style.Stroke': {
                    'color': 'navy',
                    'width': 2
                }},
                'fill': {'ol.style.Fill': {
                    'color': 'rgba(0, 0, 255, 0.1)'
                }}
            }},
            'MultiPolygon': {'ol.style.Style': {
                'stroke': {'ol.style.Stroke': {
                    'color': 'navy',
                    'width': 2
                }},
                'fill': {'ol.style.Fill': {
                    'color': 'rgba(0, 0, 255, 0.1)'
                }}
            }},
        })

    def test_should_disable_basemap(self):
        class DisableBasemapMapLayout(MapLayout):
            default_disable_basemap = True

        mock_request = mock.MagicMock()
        inst = DisableBasemapMapLayout()
        ret = inst.save_custom_layers(mock_request)
        self.assertTrue(ret)

    def test_save_custom_layers(self):
        mock_request = mock.MagicMock()
        inst = MapLayout()
        ret = inst.save_custom_layers(mock_request)
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(ret.content, b'{"success": true, "message": "Not Implemented."}')

    def test_remove_custom_layer(self):
        mock_request = mock.MagicMock()
        inst = MapLayout()
        ret = inst.remove_custom_layer(mock_request)
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(ret.content, b'{"success": true, "message": "Not Implemented."}')

    def test_get_context(self):
        pass

    @mock.patch('tethys_layouts.views.map_layout.has_permission')
    def test_get_permissions_not_enforce(self, mock_has_permission):
        class GrantPermissionMapLayout(MapLayout):
            enforce_permissions = False
            plot_slide_sheet = True
            show_public_toggle = True

        mock_request = mock.MagicMock()
        permissions = dict()
        inst = GrantPermissionMapLayout()
        ret = inst.get_permissions(mock_request, permissions)
        mock_has_permission.assert_not_called()
        self.assertDictEqual(ret, {
            'can_download': True,
            'can_use_geocode': True,
            'can_use_plot': True,
            'show_public_toggle': True,
            'show_remove': True,
            'show_rename': True,
        })

    @mock.patch('tethys_layouts.views.map_layout.has_permission')
    def test_get_permissions_enforce(self, mock_has_permission):
        class EnforcePermissionMapLayout(MapLayout):
            enforce_permissions = True
            plot_slide_sheet = True
            show_public_toggle = True

        mock_request = mock.MagicMock()
        mock_has_permission.return_value = False
        permissions = dict()
        inst = EnforcePermissionMapLayout()
        ret = inst.get_permissions(mock_request, permissions)
        self.assertEqual(mock_has_permission.call_count, 6)
        mock_has_permission.assert_any_call(mock_request, 'can_download')
        mock_has_permission.assert_any_call(mock_request, 'use_map_geocode')
        mock_has_permission.assert_any_call(mock_request, 'use_map_plot')
        mock_has_permission.assert_any_call(mock_request, 'toggle_public_layers')
        mock_has_permission.assert_any_call(mock_request, 'remove_layers')
        mock_has_permission.assert_any_call(mock_request, 'rename_layers')
        self.assertDictEqual(ret, {
            'can_download': False,
            'can_use_geocode': False,
            'can_use_plot': False,
            'show_public_toggle': False,
            'show_remove': False,
            'show_rename': False,
        })

    @mock.patch('tethys_layouts.views.map_layout.has_permission')
    def test_get_permissions_enforce_no_slidesheet_or_public_toggle(self, mock_has_permission):
        class EnforcePermissionMapLayout(MapLayout):
            enforce_permissions = True
            plot_slide_sheet = False
            show_public_toggle = False

        mock_request = mock.MagicMock()
        mock_has_permission.return_value = False
        permissions = dict()
        inst = EnforcePermissionMapLayout()
        ret = inst.get_permissions(mock_request, permissions)
        self.assertEqual(mock_has_permission.call_count, 4)
        mock_has_permission.assert_any_call(mock_request, 'can_download')
        mock_has_permission.assert_any_call(mock_request, 'use_map_geocode')
        mock_has_permission.assert_any_call(mock_request, 'remove_layers')
        mock_has_permission.assert_any_call(mock_request, 'rename_layers')
        self.assertDictEqual(ret, {
            'can_download': False,
            'can_use_geocode': False,
            'can_use_plot': False,
            'show_public_toggle': False,
            'show_remove': False,
            'show_rename': False,
        })

    def test__build_map_view(self):
        pass

    def test__build_ceisum_map_view(self):
        pass

    def test__get_map_extent_and_view(self):
        pass

    def test__translate_layers_to_cesium_ImageWMS(self):
        pass

    def test__translate_layers_to_cesium_TileWMS(self):
        pass

    def test__translate_layers_to_cesium_GeoJSON(self):
        pass

    def test_get_plot_data(self):
        pass

    def test_build_legend_item(self):
        pass

    def test_build_layer_tree_item(self):
        pass

    def test_find_location_by_query(self):
        pass

    def test_find_location_by_query_permission_denied(self):
        pass

    def test_find_location_by_query_no_geocode_api_key(self):
        pass

    def test_find_location_by_query_error_response(self):
        pass

    def test_find_location_by_query_bounds(self):
        pass

    def test_find_location_by_query_no_bounds(self):
        pass

    def test_convert_geojson_to_shapefile_Polygon(self):
        pass

    def test_convert_geojson_to_shapefile_Point(self):
        pass

    def test_convert_geojson_to_shapefile_LineString(self):
        pass

    def test_convert_geojson_to_shapefile_unsupported_shape(self):
        pass

    @mock.patch('tethys_layouts.views.map_layout.MapLayout.sds_setting', new_callable=mock.PropertyMock)
    def test_get_wms_endpoint_trailing_slash(self, mock_sds_setting):
        mock_sds_setting.return_value = mock.MagicMock(
            public_endpoint='https://example.com/geoserver/rest/'
        )
        ret = MapLayout.get_wms_endpoint()
        self.assertEqual(ret, 'https://example.com/geoserver/wms/')

    @mock.patch('tethys_layouts.views.map_layout.MapLayout.sds_setting', new_callable=mock.PropertyMock)
    def test_get_wms_endpoint_no_trailing_slash(self, mock_sds_setting):
        mock_sds_setting.return_value = mock.MagicMock(
            public_endpoint='https://example.com/geoserver/rest'
        )
        ret = MapLayout.get_wms_endpoint()
        self.assertEqual(ret, 'https://example.com/geoserver/wms/')

    @mock.patch('tethys_layouts.views.map_layout.MapLayout.sds_setting', new_callable=mock.PropertyMock)
    def test_get_wms_endpoint_not_public(self, mock_sds_setting):
        mock_sds_setting.return_value = mock.MagicMock(
            endpoint='https://example.com/geoserver/rest/'
        )
        ret = MapLayout.get_wms_endpoint(public=False)
        self.assertEqual(ret, 'https://example.com/geoserver/wms/')
