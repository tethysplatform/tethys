import json
import tempfile
from unittest import mock
import zipfile
from django.test import RequestFactory, TestCase, override_settings
from django.http import JsonResponse

from tethys_gizmos.gizmo_options import (
    MVView,
    MVLayer,
    MapView,
    CesiumMapView,
    ToggleSwitch,
    SlideSheet,
)
from tethys_layouts.views.map_layout import MapLayout
from tethys_layouts.exceptions import TethysLayoutPropertyException


class ComposeLayersMapLayout(MapLayout):
    map_title = "Bar"
    map_subtitle = "Baz"
    geocode_api_key = "12345"
    layer_tab_name = "Foos"
    default_map_extent = [10, 10, 20, 20]
    map_type = "tethys_map_view"
    show_public_toggle = True
    plotly_version = "1.2.3"
    show_properties_popup = True
    show_map_click_popup = True
    show_legends = True
    wide_nav = False
    geoserver_workspace = "foo"

    def compose_layers(self, request, map_view, *args, **kwargs):
        # Legends are built for thredds server layers
        wms_thredds_layer = self.build_wms_layer(
            endpoint="https://foo.bar.baz/thredds/wms/testAll/grace/GRC_jpl_tot.nc",
            server_type="thredds",
            layer_name="area",
            layer_title="WMS THREDDS Layer",
            layer_variable="grace",
            visible=True,
        )

        wms_geoserver_layer = self.build_wms_layer(
            endpoint="https://foo.bar.baz/geoserver",
            server_type="geoserver",
            layer_name="streams",
            layer_title="WMS GeoServer Layer",
            layer_variable="stream_network",
            layer_id="stream_id",
            visible=True,
        )

        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-111.64031982421875, 40.20509926855807],
                    },
                }
            ],
        }

        geojson_layer = self.build_geojson_layer(
            geojson=geojson,
            layer_name="a-point",
            layer_title="GeoJSON Layer",
            layer_variable="reference",
            visible=False,
            extent=[-63.69, 12.81, -129.17, 49.38],
            show_legend=False,
        )

        arc_gis_layer = self.build_arc_gis_layer(
            endpoint="https://sampleserver1.arcgisonline.com"
            "/ArcGIS/rest/services/Specialty/ESRI_StateCityHighway_USA/MapServer",
            layer_name="ESRI_StateCityHighway",
            layer_title="ArcGIS Layer",
            layer_variable="highways",
            visible=False,
            extent=[-173, 17, -65, 72],
        )

        layers = [wms_thredds_layer, wms_geoserver_layer, geojson_layer, arc_gis_layer]

        layer_groups = [
            self.build_layer_group(
                id="test-layer-group",
                display_name="Foo",
                layer_control="radio",
                layers=layers,
            ),
        ]

        return layer_groups


class TestMapLayout(TestCase):
    def setUp(self):
        self.inst = MapLayout()
        self.factory = RequestFactory()
        self.mock_user = mock.MagicMock(is_active=True, is_authenticated=True)

    def tearDown(self):
        pass

    def test_default_props(self):
        inst = MapLayout()
        self.assertEqual(
            inst.template_name, "tethys_layouts/map_layout/map_layout.html"
        )
        self.assertListEqual(inst.http_method_names, ["get", "post"])
        self.assertEqual(
            inst._geocode_endpoint, "http://api.opencagedata.com/geocode/v1/geojson"
        )
        self.assertEqual(inst.map_subtitle, "")
        self.assertEqual(inst.map_title, "")
        self.assertListEqual(inst.basemaps, ["OpenStreetMap", "ESRI"])
        self.assertIsNone(inst.cesium_ion_token)
        self.assertFalse(inst.default_disable_basemap)
        self.assertIsNone(inst.geocode_api_key)
        self.assertFalse(inst.enforce_permissions)
        self.assertIsNone(inst.geocode_extent)
        self.assertEqual(inst.geoserver_workspace, "")
        self.assertListEqual(inst.default_map_extent, [-65.69, 23.81, -129.17, 49.38])
        self.assertFalse(inst.feature_selection_multiselect)
        self.assertEqual(inst.feature_selection_sensitivity, 4)
        self.assertEqual(inst.layer_tab_name, "Layers")
        self.assertEqual(inst.map_type, "tethys_map_view")
        self.assertEqual(inst.max_zoom, 28)
        self.assertEqual(inst.min_zoom, 0)
        self.assertFalse(inst.plot_slide_sheet)
        self.assertEqual(inst.plotly_version, "2.3.0")
        self.assertEqual(inst.sds_setting_name, "")
        self.assertFalse(inst.show_custom_layer)
        self.assertFalse(inst.show_legends)
        self.assertFalse(inst.show_map_clicks)
        self.assertFalse(inst.show_map_click_popup)
        self.assertFalse(inst.show_properties_popup)
        self.assertFalse(inst.show_public_toggle)
        self.assertFalse(inst.wide_nav)

    def test_sds_setting(self):
        mock_app = mock.MagicMock()

        class SdsMapLayout(MapLayout):
            app = mock_app
            sds_setting_name = "foo"

        ret = SdsMapLayout.sds_setting
        mock_app.get_spatial_dataset_service.assert_called_with("foo")
        self.assertEqual(ret, mock_app.get_spatial_dataset_service("foo"))

    def test_sds_setting_no_name(self):
        mock_app = mock.MagicMock()

        class NoSdsNameMapLayout(MapLayout):
            app = mock_app
            sds_setting_name = ""

        with self.assertRaises(TethysLayoutPropertyException) as cm:
            NoSdsNameMapLayout.sds_setting

        self.assertEqual(
            str(cm.exception),
            'You must define the "sds_setting_name" property on your MapLayout class to use this feature.',
        )

    def test_sds_setting_no_app(self):
        class NoAppNameMapLayout(MapLayout):
            app = None
            sds_setting_name = "foo"

        with self.assertRaises(TethysLayoutPropertyException) as cm:
            NoAppNameMapLayout.sds_setting

        self.assertEqual(
            str(cm.exception),
            'You must define the "app" property on your MapLayout class to use this feature.',
        )

    def test_compose_layers(self):
        mock_request = mock.MagicMock()
        mock_map_view = mock.MagicMock()
        inst = MapLayout()
        ret = inst.compose_layers(mock_request, mock_map_view)
        self.assertListEqual(ret, list())

    def test_get_plot_for_layer_feature(self):
        mock_request = mock.MagicMock()
        inst = MapLayout()
        plot_title, data, layout = inst.get_plot_for_layer_feature(
            mock_request, "Foo", "12345", {}, {}
        )
        self.assertEqual(plot_title, "Undefined")
        self.assertListEqual(
            data,
            [
                {
                    "name": "12345",
                    "mode": "lines",
                    "x": [1, 2, 3, 4],
                    "y": [10, 15, 13, 17],
                }
            ],
        )
        self.assertDictEqual(
            layout, {"xaxis": {"title": "Foo"}, "yaxis": {"title": "Undefined"}}
        )

    def test_get_vector_style_map(self):
        ret = MapLayout.get_vector_style_map()
        self.assertDictEqual(
            ret,
            {
                "Point": {
                    "ol.style.Style": {
                        "image": {
                            "ol.style.Circle": {
                                "radius": 5,
                                "fill": {
                                    "ol.style.Fill": {
                                        "color": "navy",
                                    }
                                },
                                "stroke": {
                                    "ol.style.Stroke": {
                                        "color": "navy",
                                    }
                                },
                            }
                        }
                    }
                },
                "LineString": {
                    "ol.style.Style": {
                        "stroke": {"ol.style.Stroke": {"color": "navy", "width": 2}}
                    }
                },
                "Polygon": {
                    "ol.style.Style": {
                        "stroke": {"ol.style.Stroke": {"color": "navy", "width": 2}},
                        "fill": {"ol.style.Fill": {"color": "rgba(0, 0, 255, 0.1)"}},
                    }
                },
                "MultiPolygon": {
                    "ol.style.Style": {
                        "stroke": {"ol.style.Stroke": {"color": "navy", "width": 2}},
                        "fill": {"ol.style.Fill": {"color": "rgba(0, 0, 255, 0.1)"}},
                    }
                },
            },
        )

    def test_should_disable_basemap(self):
        class DisableBasemapMapLayout(MapLayout):
            default_disable_basemap = True

        mock_request = mock.MagicMock()
        inst = DisableBasemapMapLayout()
        ret = inst.should_disable_basemap(mock_request)
        self.assertTrue(ret)

    def test_on_add_custom_layer(self):
        mock_request = mock.MagicMock()
        inst = MapLayout()
        ret = inst.on_add_custom_layer(mock_request)
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(
            ret.content, b'{"success": false, "message": "Not Implemented."}'
        )

    def test_on_remove_tree_item(self):
        mock_request = mock.MagicMock()
        inst = MapLayout()
        ret = inst.on_remove_tree_item(mock_request)
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(
            ret.content, b'{"success": false, "message": "Not Implemented."}'
        )

    def test_on_rename_tree_item(self):
        mock_request = mock.MagicMock()
        inst = MapLayout()
        ret = inst.on_rename_tree_item(mock_request)
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(
            ret.content, b'{"success": false, "message": "Not Implemented."}'
        )

    @mock.patch("tethys_layouts.views.map_layout.log")
    def test_get_context(self, _):
        request = self.factory.get("/some/endpoint")
        inst = ComposeLayersMapLayout()
        initial_context = dict()
        ret = inst.get_context(request, initial_context)
        self.assertTrue(ret["geocode_enabled"])
        self.assertEqual(len(ret["layer_groups"]), 1)
        self.assertEqual(ret["layer_groups"][0]["display_name"], "Foo")
        self.assertEqual(len(ret["layer_groups"][0]["layers"]), 4)
        self.assertEqual(ret["layer_tab_name"], "Foos")
        self.assertListEqual(ret["map_extent"], [10, 10, 20, 20])
        self.assertEqual(ret["map_type"], "tethys_map_view")
        self.assertIsInstance(ret["map_view"], MapView)
        self.assertEqual(len(ret["map_view"].layers), 4)
        self.assertEqual(ret["nav_title"], "Bar")
        self.assertEqual(ret["nav_subtitle"], "Baz")
        self.assertEqual(ret["plotly_version"], "1.2.3")
        self.assertFalse(ret["show_custom_layer"])
        self.assertTrue(ret["show_properties_popup"])
        self.assertTrue(ret["show_map_click_popup"])
        self.assertTrue(ret["show_legends"])
        self.assertFalse(ret["wide_nav"])
        self.assertEqual(ret["workspace"], "foo")
        self.assertIsInstance(ret["plot_slide_sheet"], SlideSheet)

    @mock.patch("tethys_layouts.views.map_layout.log")
    def test_get_context_custom_layer(self, _):
        class CustomLayerMapLayout(ComposeLayersMapLayout):
            show_custom_layer = True

        request = self.factory.get("/some/endpoint")
        inst = CustomLayerMapLayout()
        initial_context = dict()
        ret = inst.get_context(request, initial_context)
        self.assertTrue(ret["geocode_enabled"])
        self.assertEqual(len(ret["layer_groups"]), 2)
        self.assertEqual(ret["layer_groups"][0]["display_name"], "Foo")
        self.assertEqual(ret["layer_groups"][1]["display_name"], "Custom Layers")
        self.assertEqual(ret["layer_groups"][1]["control"], "checkbox")
        self.assertEqual(len(ret["layer_groups"][1]["layers"]), 0)
        self.assertTrue(ret["show_custom_layer"])

    @mock.patch("tethys_layouts.views.map_layout.log")
    def test_get_context_custom_layer_already_exists(self, _):
        class CustomLayerMapLayout(ComposeLayersMapLayout):
            show_custom_layer = True

            def compose_layers(self, request, map_view, *args, **kwargs):
                layer_groups = super().compose_layers(
                    request, map_view, *args, **kwargs
                )
                layer_groups.append(
                    self.build_layer_group(
                        id="custom_layers",
                        display_name="Extra Custom Layers",
                        layers=[],
                        layer_control="radio",
                        visible=True,
                    )
                )
                return layer_groups

        request = self.factory.get("/some/endpoint")
        inst = CustomLayerMapLayout()
        initial_context = dict()
        ret = inst.get_context(request, initial_context)
        self.assertTrue(ret["geocode_enabled"])
        self.assertEqual(len(ret["layer_groups"]), 2)
        self.assertEqual(ret["layer_groups"][0]["display_name"], "Foo")
        self.assertEqual(ret["layer_groups"][1]["display_name"], "Extra Custom Layers")
        self.assertEqual(ret["layer_groups"][1]["control"], "radio")
        self.assertEqual(len(ret["layer_groups"][1]["layers"]), 0)
        self.assertTrue(ret["show_custom_layer"])

    @mock.patch("tethys_layouts.views.map_layout.log")
    def test_get_context_cesium(self, _):
        class CesiumComposeLayersMapLayout(ComposeLayersMapLayout):
            map_type = "cesium_map_view"
            cesium_ion_token = "987-654-321"

        request = self.factory.get("/some/endpoint")
        inst = CesiumComposeLayersMapLayout()
        initial_context = dict()
        ret = inst.get_context(request, initial_context)
        expected_context_vars = [
            "geocode_enabled",
            "layer_groups",
            "layer_tab_name",
            "legends",
            "map_extent",
            "map_type",
            "map_view",
            "nav_subtitle",
            "nav_title",
            "plotly_version",
            "show_custom_layer",
            "show_properties_popup",
            "show_map_click_popup",
            "show_legends",
            "wide_nav",
            "workspace",
            "plot_slide_sheet",
        ]
        for var in expected_context_vars:
            self.assertIn(var, ret)

        self.assertEqual(ret["map_type"], "cesium_map_view")
        self.assertIsInstance(ret["map_view"], CesiumMapView)
        self.assertEqual(len(ret["map_view"].layers), 2)  # ArcGIS Layer not supported
        self.assertEqual(len(ret["map_view"].entities), 1)

    @mock.patch("tethys_layouts.views.map_layout.log")
    def test_get_context_public_toggle(self, _):
        request = self.factory.get("/some/endpoint")
        inst = ComposeLayersMapLayout()
        initial_context = dict(show_public_toggle=True)
        ret = inst.get_context(request, initial_context)
        self.assertIn("layer_dropdown_toggle", ret)
        self.assertIsInstance(ret["layer_dropdown_toggle"], ToggleSwitch)

    @mock.patch("tethys_layouts.views.map_layout.has_permission")
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
        self.assertDictEqual(
            ret,
            {
                "can_download": True,
                "can_use_geocode": True,
                "can_use_plot": True,
                "show_public_toggle": True,
                "show_remove": True,
                "show_rename": True,
            },
        )

    @mock.patch("tethys_layouts.views.map_layout.has_permission")
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
        mock_has_permission.assert_any_call(mock_request, "can_download")
        mock_has_permission.assert_any_call(mock_request, "use_map_geocode")
        mock_has_permission.assert_any_call(mock_request, "use_map_plot")
        mock_has_permission.assert_any_call(mock_request, "toggle_public_layers")
        mock_has_permission.assert_any_call(mock_request, "remove_layers")
        mock_has_permission.assert_any_call(mock_request, "rename_layers")
        self.assertDictEqual(
            ret,
            {
                "can_download": False,
                "can_use_geocode": False,
                "can_use_plot": False,
                "show_public_toggle": False,
                "show_remove": False,
                "show_rename": False,
            },
        )

    @mock.patch("tethys_layouts.views.map_layout.has_permission")
    def test_get_permissions_enforce_no_slidesheet_or_public_toggle(
        self, mock_has_permission
    ):
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
        mock_has_permission.assert_any_call(mock_request, "can_download")
        mock_has_permission.assert_any_call(mock_request, "use_map_geocode")
        mock_has_permission.assert_any_call(mock_request, "remove_layers")
        mock_has_permission.assert_any_call(mock_request, "rename_layers")
        self.assertDictEqual(
            ret,
            {
                "can_download": False,
                "can_use_geocode": False,
                "can_use_plot": False,
                "show_public_toggle": False,
                "show_remove": False,
                "show_rename": False,
            },
        )

    def test__build_map_view(self):
        class MapBuildingMapLayout(MapLayout):
            default_map_extent = [-10, -10, 10, 10]
            default_disable_basemap = True
            feature_selection_multiselect = True
            feature_selection_sensitivity = 10
            show_map_clicks = True
            default_zoom = 6
            min_zoom = 2
            max_zoom = 12

        mock_request = mock.MagicMock()
        extent = [-112, 42, -110, 40]
        view = MVView(extent=extent)
        inst = MapBuildingMapLayout()
        ret = inst._build_map_view(mock_request, view, extent)
        self.assertIsInstance(ret, MapView)
        self.assertListEqual(ret["controls"][2]["ZoomToExtent"]["extent"], extent)
        self.assertTrue(ret["disable_basemap"])
        self.assertTrue(ret["feature_selection"]["multiselect"])
        self.assertEqual(ret["feature_selection"]["sensitivity"], 10)
        self.assertTrue(ret["show_clicks"])
        self.assertDictEqual(
            ret["view"],
            {
                "center": None,
                "extent": extent,
                "maxZoom": 28,
                "minZoom": 0,
                "projection": "EPSG:4326",
                "zoom": 4,
            },
        )

    def test__build_map_view_custom_should_disable_basemap(self):
        class ShouldNotDisableBasemapMapLayout(MapLayout):
            default_map_extent = [-10, -10, 10, 10]
            default_disable_basemap = True
            feature_selection_multiselect = True
            feature_selection_sensitivity = 10
            show_map_clicks = True
            default_zoom = 6
            min_zoom = 2
            max_zoom = 12

            def should_disable_basemap(self, request, *args, **kwargs):
                return False

        mock_request = mock.MagicMock()
        extent = [-112, 42, -110, 40]
        view = MVView(extent=extent)
        inst = ShouldNotDisableBasemapMapLayout()
        ret = inst._build_map_view(mock_request, view, extent)
        self.assertIsInstance(ret, MapView)
        self.assertFalse(ret["disable_basemap"])

    def test__build_ceisum_map_view(self):
        class CesiumMapLayout(MapLayout):
            map_type = "cesium"
            cesium_ion_token = "12345"

        mock_map_view = mock.MagicMock(spec=MapView, layers=["mock-layers"])
        inst = CesiumMapLayout()
        inst._translate_layers_to_cesium = mock.MagicMock(
            return_value=(["layers"], ["entities"])
        )
        ret = inst._build_ceisum_map_view(mock_map_view)
        self.assertIsInstance(ret, CesiumMapView)
        self.assertEqual(ret.cesium_ion_token, "12345")
        inst._translate_layers_to_cesium.assert_called_with(["mock-layers"])
        self.assertListEqual(ret.layers, ["layers"])
        self.assertListEqual(ret.entities, ["entities"])

    def test__build_ceisum_map_view_no_cesium_token(self):
        class NoTokenCesiumMapLayout(MapLayout):
            map_type = "cesium"
            cesium_ion_token = None

        inst = NoTokenCesiumMapLayout()

        mock_map_view = mock.MagicMock(spec=MapView)
        with self.assertRaises(RuntimeError) as cm:
            inst._build_ceisum_map_view(mock_map_view)

        self.assertEqual(
            str(cm.exception),
            'You must set the "cesium_ion_token" attribute of the '
            'MapLayout to use the Cesium "map_type".',
        )

    def test_build_map_extent_and_view(self):
        class ExtentMapLayout(MapLayout):
            default_map_extent = [-20, -20, 10, 20]
            max_zoom = 13
            min_zoom = 3

        mock_request = mock.MagicMock()
        inst = ExtentMapLayout()
        ret_view, ret_extent = inst.build_map_extent_and_view(mock_request)
        self.assertIsInstance(ret_view, MVView)
        self.assertDictEqual(
            ret_view,
            {
                "center": None,
                "extent": [-20, -20, 10, 20],
                "maxZoom": 13,
                "minZoom": 3,
                "projection": "EPSG:4326",
                "zoom": 4,
            },
        )
        self.assertListEqual(ret_extent, [-20, -20, 10, 20])

    def test_build_map_extent_and_view_no_default_extent(self):
        class ExtentMapLayout(MapLayout):
            min_zoom = 3
            max_zoom = 13

        mock_request = mock.MagicMock()
        ret_view, ret_extent = ExtentMapLayout().build_map_extent_and_view(mock_request)
        self.assertIsInstance(ret_view, MVView)
        self.assertDictEqual(
            ret_view,
            {
                "center": None,
                "extent": [-65.69, 23.81, -129.17, 49.38],  # This is the default extent
                "maxZoom": 13,
                "minZoom": 3,
                "projection": "EPSG:4326",
                "zoom": 4,
            },
        )
        self.assertListEqual(
            ret_extent, [-65.69, 23.81, -129.17, 49.38]
        )  # This is the default extent

    def test__translate_layers_to_cesium(self):
        image_wms = MVLayer(
            source="ImageWMS",
            options={
                "url": "http://localhost:8181/geoserver/wms",
                "params": {"LAYERS": "topp:states"},
                "serverType": "geoserver",
            },
            legend_title="Foo",
        )
        tile_wms = MVLayer(
            source="TileWMS",
            options={
                "url": "http://localhost:8181/geoserver/wms",
                "params": {"LAYERS": "topp:states", "TILED": True},
                "serverType": "geoserver",
            },
            legend_title="Bar",
        )
        geojson = MVLayer(
            source="GeoJSON",
            options={
                "type": "FeatureCollection",
                "crs": {"type": "name", "properties": {"name": "EPSG:3857"}},
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [0, 0]},
                    }
                ],
            },
            legend_title="Baz",
        )
        map_view_layers = [image_wms, tile_wms, geojson]
        ret1, ret2 = self.inst._translate_layers_to_cesium(map_view_layers)
        self.assertEqual(len(ret1), 2)
        self.assertIn(image_wms, ret1)
        self.assertIn(tile_wms, ret1)
        self.assertNotIn(geojson, ret1)
        self.assertEqual(len(ret2), 1)
        self.assertNotIn(image_wms, ret2)
        self.assertNotIn(tile_wms, ret2)
        self.assertIn(geojson, ret2)

    def test_get_plot_data(self):
        layer_data = {"layer_id": "24680"}
        feature_props = {"id": "67890", "name": "foo"}
        request = self.factory.post(
            "/some/endpoint",
            data={
                "method": "get-plot-data",
                "layer_name": "Foo",
                "feature_id": "12345",
                "layer_data": json.dumps(layer_data),
                "feature_props": json.dumps(feature_props),
            },
        )

        controller = MapLayout.as_controller()
        ret = controller(request)
        self.assertIsInstance(ret, JsonResponse)
        ret_json = json.loads(ret.content)
        self.assertDictEqual(
            ret_json,
            {
                "data": [
                    {
                        "mode": "lines",
                        "name": "12345",
                        "x": [1, 2, 3, 4],
                        "y": [10, 15, 13, 17],
                    }
                ],
                "layout": {"xaxis": {"title": "Foo"}, "yaxis": {"title": "Undefined"}},
                "title": "Undefined",
            },
        )

    @override_settings(MULTIPLE_APP_MODE=True)
    def test_build_legend_item(self):
        request = self.factory.post(
            "/some/endpoint",
            data={
                "method": "build-legend-item",
                "div_id": "this-one",
                "minimum": 0,
                "maximum": 15,
                "color_ramp": "Galaxy Berry",
                "prefix": "v",
                "color_prefix": "c",
                "first_division": 3,
                "layer_id": "12345",
            },
        )
        request.user = self.mock_user
        controller = MapLayout.as_controller()
        ret = controller(request)
        self.assertIsInstance(ret, JsonResponse)
        ret_json = json.loads(ret.content)
        self.assertDictEqual(
            ret_json,
            {
                "color_ramp": "Galaxy Berry",
                "div_id": "this-one",
                "division_string": "v3:0.00;c3:#fff100;v4:1.67;c4:#ff8c00;v5:3.33;c5:#e81123;v6:5.00;c6:#ec008c;v7:6.67;"
                "c7:#68217a;v8:8.33;c8:#00188f;v9:10.00;c9:#00bcf2;v10:11.67;c10:#00b294;v11:13.33;"
                "c11:#009e49;v12:15.00;c12:#bad80a",
                "layer_id": "12345",
                "response": '<ul class="legend-list" data-collapsed="false">\n'
                "  \n"
                '    <div class="legend-item">\n'
                '      <li class="legend-list-item">\n'
                "        <p>0.0 </p>\n"
                '        <div class="color-box" style="background-color: #fff100;"></div>\n'
                "      </li>\n"
                "    </div>\n"
                "  \n"
                '    <div class="legend-item">\n'
                '      <li class="legend-list-item">\n'
                "        <p>1.67 </p>\n"
                '        <div class="color-box" style="background-color: #ff8c00;"></div>\n'
                "      </li>\n"
                "    </div>\n"
                "  \n"
                '    <div class="legend-item">\n'
                '      <li class="legend-list-item">\n'
                "        <p>3.33 </p>\n"
                '        <div class="color-box" style="background-color: #e81123;"></div>\n'
                "      </li>\n"
                "    </div>\n"
                "  \n"
                '    <div class="legend-item">\n'
                '      <li class="legend-list-item">\n'
                "        <p>5.0 </p>\n"
                '        <div class="color-box" style="background-color: #ec008c;"></div>\n'
                "      </li>\n"
                "    </div>\n"
                "  \n"
                '    <div class="legend-item">\n'
                '      <li class="legend-list-item">\n'
                "        <p>6.67 </p>\n"
                '        <div class="color-box" style="background-color: #68217a;"></div>\n'
                "      </li>\n"
                "    </div>\n"
                "  \n"
                '    <div class="legend-item">\n'
                '      <li class="legend-list-item">\n'
                "        <p>8.33 </p>\n"
                '        <div class="color-box" style="background-color: #00188f;"></div>\n'
                "      </li>\n"
                "    </div>\n"
                "  \n"
                '    <div class="legend-item">\n'
                '      <li class="legend-list-item">\n'
                "        <p>10.0 </p>\n"
                '        <div class="color-box" style="background-color: #00bcf2;"></div>\n'
                "      </li>\n"
                "    </div>\n"
                "  \n"
                '    <div class="legend-item">\n'
                '      <li class="legend-list-item">\n'
                "        <p>11.67 </p>\n"
                '        <div class="color-box" style="background-color: #00b294;"></div>\n'
                "      </li>\n"
                "    </div>\n"
                "  \n"
                '    <div class="legend-item">\n'
                '      <li class="legend-list-item">\n'
                "        <p>13.33 </p>\n"
                '        <div class="color-box" style="background-color: #009e49;"></div>\n'
                "      </li>\n"
                "    </div>\n"
                "  \n"
                '    <div class="legend-item">\n'
                '      <li class="legend-list-item">\n'
                "        <p>15.0 </p>\n"
                '        <div class="color-box" style="background-color: #bad80a;"></div>\n'
                "      </li>\n"
                "    </div>\n"
                "  \n"
                "</ul>",
                "success": True,
            },
        )

    @override_settings(MULTIPLE_APP_MODE=True)
    def test_build_layer_tree_item_create(self):
        request = self.factory.post(
            "/some/endpoint",
            data={
                "method": "build-layer-tree-item",
                "operation": "create",
                "layer_group_name": "Legend Group",
                "layer_group_id": "12345",
                "layer_names": '["Layer 1", "Layer 2"]',
                "layer_ids": '["54321", "98745"]',
                "layer_legends": '["var1", "var2"]',
                "show_rename": "false",
                "show_remove": "false",
                "show_download": "false",
            },
        )
        request.user = self.mock_user

        controller = MapLayout.as_controller()
        ret = controller(request)
        ret_json = json.loads(ret.content)
        self.assertDictEqual(
            ret_json,
            {
                "response": '<li id="12345" class="layer-group-item">\n'
                "  \n"
                '  <label class="flatmark"><span class="display-name">Legend '
                "Group</span>\n"
                '    <input type="checkbox"\n'
                '           class="layer-group-visibility-control"\n'
                '           checked="checked"\n'
                '           data-layer-group-id="12345">\n'
                '    <span class="checkmark checkbox"></span>\n'
                "  </label>\n"
                "\n"
                "  \n"
                "  \n"
                '  <a id="12345--collapse"\n'
                '     class="collapse-action btn btn-sm layers-btn float-end"\n'
                '     data-collapsed="false">\n'
                '    <i class="bi bi-chevron-down"></i>\n'
                "  </a>\n"
                "</li>\n"
                "\n"
                '<ul class="layer-list" id="12345_associated_layers"  '
                'data-collapsed="false">\n'
                "\n"
                '  <li class="layer-list-item">\n'
                "  \n"
                '  <label class="flatmark"><span class="display-name">Layer '
                "1</span>\n"
                '    <input type="checkbox"\n'
                '           class="layer-visibility-control"\n'
                '           checked="checked"\n'
                "           \n"
                '           data-layer-id="54321"\n'
                '           data-layer-variable="var1"\n'
                '           name="12345">\n'
                '    <span class="checkmark checkbox"></span>\n'
                "  </label>\n"
                "\n"
                "  \n"
                '  <div class="dropdown layers-context-menu float-end">\n'
                '    <button id="54321--context-menu"\n'
                '            class="btn btn-sm layers-btn "\n'
                '            data-bs-toggle="dropdown"\n'
                '            aria-expanded="false">\n'
                '      <i class="bi bi-three-dots-vertical"></i>\n'
                "    </button>\n"
                '    <ul class="dropdown-menu dropdown-menu-end" '
                'aria-labeledby="54321--context-menu">\n'
                "      \n"
                "      \n"
                "      \n"
                "      \n"
                '      <li><a class="dropdown-item zoom-to-layer-action" '
                'href="javascript:void(0);" data-layer-id="54321"><i class="bi '
                'bi-fullscreen"></i><span class="command-name">Zoom to '
                "Layer</span></a></li>\n"
                "      \n"
                '      <li><hr class="dropdown-divider"></li>\n'
                "      <li>\n"
                '        <div class="flat-slider-container">\n'
                '          <label><i class="bi bi-circle-half"></i><span '
                'class="command-name">Opacity: </span><span '
                'class="slider-value">100%</span></label>\n'
                '          <input type="range"\n'
                '                 class="flat-slider layer-opacity-control"\n'
                '                 min="0" max="100"\n'
                '                 value="100"\n'
                '                 data-layer-id="54321"\n'
                '                 data-layer-variable="">\n'
                "        </div>\n"
                "      </li>\n"
                "    </ul>\n"
                "  </div>\n"
                "</li>\n"
                "\n"
                '  <li class="layer-list-item">\n'
                "  \n"
                '  <label class="flatmark"><span class="display-name">Layer '
                "2</span>\n"
                '    <input type="checkbox"\n'
                '           class="layer-visibility-control"\n'
                '           checked="checked"\n'
                "           \n"
                '           data-layer-id="98745"\n'
                '           data-layer-variable="var2"\n'
                '           name="12345">\n'
                '    <span class="checkmark checkbox"></span>\n'
                "  </label>\n"
                "\n"
                "  \n"
                '  <div class="dropdown layers-context-menu float-end">\n'
                '    <button id="98745--context-menu"\n'
                '            class="btn btn-sm layers-btn "\n'
                '            data-bs-toggle="dropdown"\n'
                '            aria-expanded="false">\n'
                '      <i class="bi bi-three-dots-vertical"></i>\n'
                "    </button>\n"
                '    <ul class="dropdown-menu dropdown-menu-end" '
                'aria-labeledby="98745--context-menu">\n'
                "      \n"
                "      \n"
                "      \n"
                "      \n"
                '      <li><a class="dropdown-item zoom-to-layer-action" '
                'href="javascript:void(0);" data-layer-id="98745"><i class="bi '
                'bi-fullscreen"></i><span class="command-name">Zoom to '
                "Layer</span></a></li>\n"
                "      \n"
                '      <li><hr class="dropdown-divider"></li>\n'
                "      <li>\n"
                '        <div class="flat-slider-container">\n'
                '          <label><i class="bi bi-circle-half"></i><span '
                'class="command-name">Opacity: </span><span '
                'class="slider-value">100%</span></label>\n'
                '          <input type="range"\n'
                '                 class="flat-slider layer-opacity-control"\n'
                '                 min="0" max="100"\n'
                '                 value="100"\n'
                '                 data-layer-id="98745"\n'
                '                 data-layer-variable="">\n'
                "        </div>\n"
                "      </li>\n"
                "    </ul>\n"
                "  </div>\n"
                "</li>\n"
                "\n"
                "</ul>\n"
                "\n",
                "success": True,
            },
        )

    @override_settings(MULTIPLE_APP_MODE=True)
    def test_build_layer_tree_item_append_with_rename_remove_download(self):
        request = self.factory.post(
            "/some/endpoint",
            data={
                "method": "build-layer-tree-item",
                "operation": "append",
                "layer_group_name": "Legend Group",
                "layer_group_id": "12345",
                "layer_names": '["Layer 1", "Layer 2"]',
                "layer_ids": '["54321", "98745"]',
                "layer_legends": '["var1", "var2"]',
                "show_rename": "true",
                "show_remove": "true",
                "show_download": "true",
            },
        )
        request.user = self.mock_user

        controller = MapLayout.as_controller()
        ret = controller(request)
        ret_json = json.loads(ret.content)
        self.maxDiff = None
        self.assertDictEqual(
            ret_json,
            {
                "response": '<li class="layer-list-item">\n'
                "  \n"
                '  <label class="flatmark"><span class="display-name">Layer 1</span>\n'
                '    <input type="checkbox"\n'
                '           class="layer-visibility-control"\n'
                '           checked="checked"\n'
                "           \n"
                '           data-layer-id="54321"\n'
                '           data-layer-variable="var1"\n'
                '           name="12345">\n'
                '    <span class="checkmark checkbox"></span>\n'
                "  </label>\n"
                "\n"
                "  \n"
                '  <div class="dropdown layers-context-menu float-end">\n'
                '    <button id="54321--context-menu"\n'
                '            class="btn btn-sm layers-btn "\n'
                '            data-bs-toggle="dropdown"\n'
                '            aria-expanded="false">\n'
                '      <i class="bi bi-three-dots-vertical"></i>\n'
                "    </button>\n"
                '    <ul class="dropdown-menu dropdown-menu-end" '
                'aria-labeledby="54321--context-menu">\n'
                "      \n"
                '        <li><a class="dropdown-item rename-action" '
                'href="javascript:void(0);"><i class="bi bi-pencil"></i><span '
                'class="command-name">Rename</span></a></li>\n'
                "      \n"
                "      \n"
                '        <li><a class="dropdown-item remove-action" '
                'href="javascript:void(0);" data-remove-type="layer" '
                'data-layer-id="54321"><i class="bi bi-trash"></i><span '
                'class="command-name">Remove</span></a></li>\n'
                "      \n"
                "      \n"
                "      \n"
                '        <li><hr class="dropdown-divider"></li>\n'
                "      \n"
                '      <li><a class="dropdown-item zoom-to-layer-action" '
                'href="javascript:void(0);" data-layer-id="54321"><i class="bi '
                'bi-fullscreen"></i><span class="command-name">Zoom to '
                "Layer</span></a></li>\n"
                "      \n"
                "        \n"
                "      \n"
                '      <li><hr class="dropdown-divider"></li>\n'
                "      <li>\n"
                '        <div class="flat-slider-container">\n'
                '          <label><i class="bi bi-circle-half"></i><span '
                'class="command-name">Opacity: </span><span '
                'class="slider-value">100%</span></label>\n'
                '          <input type="range"\n'
                '                 class="flat-slider layer-opacity-control"\n'
                '                 min="0" max="100"\n'
                '                 value="100"\n'
                '                 data-layer-id="54321"\n'
                '                 data-layer-variable="">\n'
                "        </div>\n"
                "      </li>\n"
                "    </ul>\n"
                "  </div>\n"
                "</li>",
                "success": True,
            },
        )

    @mock.patch("tethys_layouts.views.map_layout.log")
    def test_build_layer_tree_item_exception(self, mock_log):
        request = self.factory.post(
            "/some/endpoint",
            data={
                "method": "build-layer-tree-item",
                "operation": "append",
                "layer_group_name": "Legend Group",
                "layer_group_id": "12345",
                "layer_names": "not json serializable",  # Error
                "layer_ids": '["54321", "98745"]',
                "layer_legends": '["var1", "var2"]',
                "show_rename": "true",
                "show_remove": "true",
                "show_download": "true",
            },
        )

        controller = MapLayout.as_controller()
        ret = controller(request)
        mock_log.exception.assert_called_with("An unexpected error has occurred.")
        self.assertEqual(ret.status_code, 200)
        ret_json = json.loads(ret.content)
        self.assertDictEqual(
            ret_json, {"success": False, "error": "An unexpected error has occurred."}
        )

    @mock.patch("tethys_layouts.views.map_layout.uuid")
    @mock.patch("tethys_layouts.views.map_layout.has_permission", return_value=True)
    @mock.patch("tethys_layouts.views.map_layout.requests")
    def test_find_location_by_query(self, mock_requests, _, mock_uuid):
        class GeocodingMapLayout(MapLayout):
            geocode_api_key = "12345"
            enforce_permissions = False
            geocode_extent = [-10, -20, 20, 10]

        features = {
            "features": [
                {
                    "geometry": {"coordinates": [-5, 5]},
                    "properties": {
                        "bounds": {
                            "southwest": {"lng": -25, "lat": 15},
                            "northeast": {"lng": -15, "lat": 25},
                        },
                        "formatted": "Foo",
                    },
                },
            ]
        }
        mock_response = mock.MagicMock(
            status_code=200, json=mock.MagicMock(return_value=features)
        )
        mock_requests.get.return_value = mock_response
        request = self.factory.post(
            "/some/endpoint",
            data={
                "method": "find-location-by-query",
                "q": "3210 N. Canyon Road, Provo, UT 84660",
            },
        )
        mock_uuid.uuid4.return_value = "123-456-789"
        controller = GeocodingMapLayout.as_controller()
        ret = controller(request)
        self.assertIsInstance(ret, JsonResponse)
        ret_json = json.loads(ret.content)
        self.assertDictEqual(
            ret_json,
            {
                "results": [
                    {
                        "bbox": [-25.0, 15.0, -15.0, 25.0],
                        "id": "geocode-123-456-789",
                        "point": [-5, 5],
                        "text": "Foo",
                    }
                ],
                "success": True,
            },
        )

    @mock.patch("tethys_layouts.views.map_layout.uuid")
    @mock.patch("tethys_layouts.views.map_layout.has_permission", return_value=True)
    @mock.patch("tethys_layouts.views.map_layout.requests")
    def test_find_location_by_query_small_bounds(self, mock_requests, _, mock_uuid):
        class GeocodingMapLayout(MapLayout):
            geocode_api_key = "12345"
            enforce_permissions = False
            geocode_extent = [-10, -20, 20, 10]

        features = {
            "features": [
                {
                    "geometry": {"coordinates": [-5, 5]},
                    "properties": {
                        "bounds": {
                            "southwest": {"lng": 10.0005, "lat": 10.0005},
                            "northeast": {"lng": 10.0010, "lat": 10.0010},
                        },
                        "formatted": "Foo",
                    },
                },
            ]
        }
        mock_response = mock.MagicMock(
            status_code=200, json=mock.MagicMock(return_value=features)
        )
        mock_requests.get.return_value = mock_response
        request = self.factory.post(
            "/some/endpoint",
            data={
                "method": "find-location-by-query",
                "q": "3210 N. Canyon Road, Provo, UT 84660",
            },
        )
        mock_uuid.uuid4.return_value = "123-456-789"
        controller = GeocodingMapLayout.as_controller()
        ret = controller(request)
        self.assertIsInstance(ret, JsonResponse)
        ret_json = json.loads(ret.content)
        self.assertDictEqual(
            ret_json,
            {
                "results": [
                    {
                        "bbox": [
                            9.999500000000001,
                            9.999500000000001,
                            10.001999999999999,
                            10.001999999999999,
                        ],
                        "id": "geocode-123-456-789",
                        "point": [-5, 5],
                        "text": "Foo",
                    }
                ],
                "success": True,
            },
        )

    @mock.patch("tethys_layouts.views.map_layout.uuid")
    @mock.patch("tethys_layouts.views.map_layout.has_permission", return_value=True)
    @mock.patch("tethys_layouts.views.map_layout.requests")
    def test_find_location_by_query_long_name(self, mock_requests, _, mock_uuid):
        class GeocodingMapLayout(MapLayout):
            geocode_api_key = "12345"
            enforce_permissions = False
            geocode_extent = [-10, -20, 20, 10]

        features = {
            "features": [
                {
                    "geometry": {"coordinates": [-5, 5]},
                    "properties": {
                        "bounds": {
                            "southwest": {"lng": -25, "lat": 15},
                            "northeast": {"lng": -15, "lat": 25},
                        },
                        "formatted": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                    },
                },
            ]
        }
        mock_response = mock.MagicMock(
            status_code=200, json=mock.MagicMock(return_value=features)
        )
        mock_requests.get.return_value = mock_response
        request = self.factory.post(
            "/some/endpoint",
            data={
                "method": "find-location-by-query",
                "q": "3210 N. Canyon Road, Provo, UT 84660",
            },
        )
        mock_uuid.uuid4.return_value = "123-456-789"
        controller = GeocodingMapLayout.as_controller()
        ret = controller(request)
        self.assertIsInstance(ret, JsonResponse)
        ret_json = json.loads(ret.content)
        self.assertDictEqual(
            ret_json,
            {
                "results": [
                    {
                        "bbox": [-25.0, 15.0, -15.0, 25.0],
                        "id": "geocode-123-456-789",
                        "point": [-5, 5],
                        "text": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmn...",
                    }
                ],
                "success": True,
            },
        )

    @mock.patch("tethys_layouts.views.map_layout.has_permission", return_value=False)
    def test_find_location_by_query_permission_denied(self, _):
        class GeocodingMapLayout(MapLayout):
            geocode_api_key = "12345"
            enforce_permissions = True
            geocode_extent = [-10, -20, 20, 10]

        request = self.factory.post(
            "/some/endpoint",
            data={
                "method": "find-location-by-query",
                "q": "3210 N. Canyon Road, Provo, UT 84660",
            },
        )
        controller = GeocodingMapLayout.as_controller()
        ret = controller(request)
        self.assertIsInstance(ret, JsonResponse)
        self.assertEqual(ret.status_code, 200)
        ret_json = json.loads(ret.content)
        self.assertDictEqual(
            ret_json,
            {
                "success": False,
                "error": "Permission Denied: user does not have permission to use geocoding.",
            },
        )

    @mock.patch("tethys_layouts.views.map_layout.has_permission", return_value=True)
    def test_find_location_by_query_no_geocode_api_key(self, _):
        class GeocodingMapLayout(MapLayout):
            geocode_api_key = None
            enforce_permissions = True
            geocode_extent = [-10, -20, 20, 10]

        request = self.factory.post(
            "/some/endpoint",
            data={
                "method": "find-location-by-query",
                "q": "3210 N. Canyon Road, Provo, UT 84660",
            },
        )
        controller = GeocodingMapLayout.as_controller()

        with self.assertRaises(RuntimeError) as cm:
            controller(request)

        self.assertEqual(
            str(cm.exception),
            "Cannot run GeoCode query because no API token was supplied. Please provide the "
            'API key via the "geocode_api_key" attribute of the MapLayoutView.',
        )

    @mock.patch("tethys_layouts.views.map_layout.has_permission", return_value=True)
    @mock.patch("tethys_layouts.views.map_layout.requests")
    def test_find_location_by_query_error_response(self, mock_requests, _):
        class GeocodingMapLayout(MapLayout):
            geocode_api_key = "12345"
            enforce_permissions = False
            geocode_extent = [-10, -20, 20, 10]

        mock_response = mock.MagicMock(status_code=500, text="Foo")
        mock_requests.get.return_value = mock_response
        request = self.factory.post(
            "/some/endpoint",
            data={
                "method": "find-location-by-query",
                "q": "3210 N. Canyon Road, Provo, UT 84660",
            },
        )
        controller = GeocodingMapLayout.as_controller()
        ret = controller(request)
        self.assertIsInstance(ret, JsonResponse)
        ret_json = json.loads(ret.content)
        self.assertDictEqual(
            ret_json,
            {
                "success": False,
                "error": "Foo",
            },
        )

    @mock.patch("tethys_layouts.views.map_layout.uuid")
    @mock.patch("tethys_layouts.views.map_layout.has_permission", return_value=True)
    @mock.patch("tethys_layouts.views.map_layout.requests")
    def test_find_location_by_query_no_bounds(self, mock_requests, _, mock_uuid):
        class GeocodingMapLayout(MapLayout):
            geocode_api_key = "12345"
            enforce_permissions = False
            geocode_extent = [-10, -20, 20, 10]

        features = {
            "features": [
                {
                    "geometry": {"coordinates": [-5, 5]},
                    "properties": {
                        "formatted": "Foo",
                    },
                },
            ]
        }
        mock_response = mock.MagicMock(
            status_code=200, json=mock.MagicMock(return_value=features)
        )
        mock_requests.get.return_value = mock_response
        request = self.factory.post(
            "/some/endpoint",
            data={
                "method": "find-location-by-query",
                "q": "3210 N. Canyon Road, Provo, UT 84660",
            },
        )
        mock_uuid.uuid4.return_value = "123-456-789"
        controller = GeocodingMapLayout.as_controller()
        ret = controller(request)
        self.assertIsInstance(ret, JsonResponse)
        ret_json = json.loads(ret.content)
        self.assertDictEqual(
            ret_json,
            {
                "results": [
                    {
                        "bbox": [-5.001, 4.999, -4.999, 5.001],
                        "id": "geocode-123-456-789",
                        "point": [-5, 5],
                        "text": "Foo",
                    }
                ],
                "success": True,
            },
        )

    def test_convert_geojson_to_shapefile_Polygon(self):
        data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "foo": "bar",
                        "baz": 1,
                        "boo": True,
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [-115.6640625, 45.460130637921004],
                                [-114.9609375, 40.84706035607122],
                                [-107.22656249999999, 39.36827914916014],
                                [-104.94140625, 45.460130637921004],
                                [-115.6640625, 45.460130637921004],
                            ]
                        ],
                    },
                }
            ],
        }

        request = self.factory.post(
            "/some/endpoint",
            data={
                "method": "convert-geojson-to-shapefile",
                "data": json.dumps(data),
                "id": "12345",
            },
        )

        controller = MapLayout.as_controller()
        ret = controller(request)
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(ret["Content-Type"], "application/zip")
        self.assertEqual(
            ret["Content-Disposition"], 'attachment; filename="12345_Polygon.zip"'
        )

        with tempfile.TemporaryFile() as tf:
            tf.write(ret.content)

            with zipfile.ZipFile(tf) as z:
                self.assertListEqual(
                    z.namelist(),
                    [
                        "12345_Polygon.prj",
                        "12345_Polygon.shp",
                        "12345_Polygon.dbf",
                        "12345_Polygon.shx",
                    ],
                )

    def test_convert_geojson_to_shapefile_Point(self):
        data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "foo": "bar",
                        "baz": 1,
                        "boo": True,
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-108.28125, 40.97989806962013],
                    },
                }
            ],
        }
        request = self.factory.post(
            "/some/endpoint",
            data={
                "method": "convert-geojson-to-shapefile",
                "data": json.dumps(data),
                "id": "12345",
            },
        )
        controller = MapLayout.as_controller()
        ret = controller(request)
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(ret["Content-Type"], "application/zip")
        self.assertEqual(
            ret["Content-Disposition"], 'attachment; filename="12345_Point.zip"'
        )

        with tempfile.TemporaryFile() as tf:
            tf.write(ret.content)

            with zipfile.ZipFile(tf) as z:
                self.assertListEqual(
                    z.namelist(),
                    [
                        "12345_Point.prj",
                        "12345_Point.shp",
                        "12345_Point.dbf",
                        "12345_Point.shx",
                    ],
                )

    def test_convert_geojson_to_shapefile_LineString(self):
        data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "foo": "bar",
                        "baz": 1,
                        "boo": True,
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [-118.828125, 43.32517767999296],
                            [-111.62109375, 44.08758502824516],
                            [-106.171875, 41.376808565702355],
                            [-95.625, 42.16340342422401],
                        ],
                    },
                }
            ],
        }
        request = self.factory.post(
            "/some/endpoint",
            data={
                "method": "convert-geojson-to-shapefile",
                "data": json.dumps(data),
                "id": "12345",
            },
        )
        controller = MapLayout.as_controller()
        ret = controller(request)
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(ret["Content-Type"], "application/zip")
        self.assertEqual(
            ret["Content-Disposition"], 'attachment; filename="12345_LineString.zip"'
        )

        with tempfile.TemporaryFile() as tf:
            tf.write(ret.content)

            with zipfile.ZipFile(tf) as z:
                self.assertListEqual(
                    z.namelist(),
                    [
                        "12345_LineString.prj",
                        "12345_LineString.shp",
                        "12345_LineString.dbf",
                        "12345_LineString.shx",
                    ],
                )

    def test_convert_geojson_to_shapefile_unsupported_shape(self):
        data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "NotSupported",
                        "coordinates": [[-118.828125, 43.32517767999296]],
                    },
                }
            ],
        }
        request = self.factory.post(
            "/some/endpoint",
            data={
                "method": "convert-geojson-to-shapefile",
                "data": json.dumps(data),
                "id": "12345",
            },
        )
        controller = MapLayout.as_controller()

        with self.assertRaises(ValueError) as cm:
            controller(request)

        self.assertEqual(
            str(cm.exception),
            "Only GeoJson of the following types are supported: Polygon, Point, or LineString",
        )

    @mock.patch(
        "tethys_layouts.views.map_layout.MapLayout.sds_setting",
        new_callable=mock.PropertyMock,
    )
    def test_get_wms_endpoint_trailing_slash(self, mock_sds_setting):
        mock_sds_setting.return_value = mock.MagicMock(
            public_endpoint="https://example.com/geoserver/rest/"
        )
        ret = MapLayout.get_wms_endpoint()
        self.assertEqual(ret, "https://example.com/geoserver/wms/")

    @mock.patch(
        "tethys_layouts.views.map_layout.MapLayout.sds_setting",
        new_callable=mock.PropertyMock,
    )
    def test_get_wms_endpoint_no_trailing_slash(self, mock_sds_setting):
        mock_sds_setting.return_value = mock.MagicMock(
            public_endpoint="https://example.com/geoserver/rest"
        )
        ret = MapLayout.get_wms_endpoint()
        self.assertEqual(ret, "https://example.com/geoserver/wms/")

    @mock.patch(
        "tethys_layouts.views.map_layout.MapLayout.sds_setting",
        new_callable=mock.PropertyMock,
    )
    def test_get_wms_endpoint_not_public(self, mock_sds_setting):
        mock_sds_setting.return_value = mock.MagicMock(
            endpoint="https://example.com/geoserver/rest/"
        )
        ret = MapLayout.get_wms_endpoint(public=False)
        self.assertEqual(ret, "https://example.com/geoserver/wms/")
