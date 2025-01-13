import copy
import unittest
from unittest import mock
from collections import OrderedDict

from tethys_gizmos.gizmo_options import MVLayer
from tethys_layouts.mixins.map_layout import (
    MapLayoutMixin,
    _COLOR_RAMPS,
    _DEFAULT_TILE_GRID,
    _THREDDS_PALETTES,
)


class TestMapLayoutMixin(unittest.TestCase):
    def setUp(self):
        self.style_map = {
            "Point": {
                "ol.style.Style": {
                    "image": {
                        "ol.style.Circle": {
                            "radius": 5,
                            "fill": {
                                "ol.style.Fill": {
                                    "color": "red",
                                }
                            },
                            "stroke": {"ol.style.Stroke": {"color": "red", "width": 2}},
                        }
                    }
                }
            },
            "LineString": {
                "ol.style.Style": {
                    "stroke": {"ol.style.Stroke": {"color": "green", "width": 3}}
                }
            },
            "Polygon": {
                "ol.style.Style": {
                    "stroke": {"ol.style.Stroke": {"color": "blue", "width": 1}},
                    "fill": {"ol.style.Fill": {"color": "rgba(0, 0, 255, 0.1)"}},
                }
            },
        }
        self.geojson_object = {
            "type": "FeatureCollection",
            "crs": {"type": "name", "properties": {"name": "EPSG:3857"}},
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[4e6, -2e6], [8e6, 2e6]],
                    },
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[-5e6, -1e6], [-4e6, 1e6], [-3e6, -1e6]]],
                    },
                },
            ],
        }

    def test_COLOR_RAMPS(self):
        self.assertEqual(MapLayoutMixin.COLOR_RAMPS, _COLOR_RAMPS)

    def test_THREDDS_PALETTES(self):
        self.assertEqual(MapLayoutMixin.THREDDS_PALETTES, _THREDDS_PALETTES)

    def test_DEFAULT_TILE_GRID(self):
        self.assertEqual(MapLayoutMixin.DEFAULT_TILE_GRID, _DEFAULT_TILE_GRID)

    def test_get_vector_style_map(self):
        with self.assertRaises(NotImplementedError):
            MapLayoutMixin.get_vector_style_map()

    def test__build_mv_layer_default(self):
        class CustomMapLayoutThing(MapLayoutMixin):
            map_extent = [-65.69, 23.81, -129.17, 49.38]

        source_options = {
            "url": "http://example.com/geoserver/wms",
            "params": {"LAYERS": "foo:bar"},
            "serverType": "geoserver",
        }

        ret = CustomMapLayoutThing._build_mv_layer(
            layer_source="TileWMS",
            layer_name="foo:bar",
            layer_title="Foo Bar",
            layer_variable="baz",
            options=source_options,
        )

        self.assertIsInstance(ret, MVLayer)
        self.assertEqual(ret.legend_title, "Foo Bar")
        self.assertListEqual(ret.legend_extent, [-65.69, 23.81, -129.17, 49.38])
        self.assertIsNone(ret.times)
        self.assertFalse(ret.feature_selection)
        self.assertDictEqual(ret.options, source_options)
        self.assertListEqual(ret.legend_classes, [])
        self.assertDictEqual(
            ret.layer_options,
            {
                "visible": True,
                "show_download": False,
            },
        )
        self.assertDictEqual(
            ret.data,
            {
                "layer_id": "foo:bar",
                "layer_name": "foo:bar",
                "popup_title": "Foo Bar",
                "layer_variable": "baz",
                "toggle_status": True,
                "excluded_properties": ["id", "type", "layer_name"],
                "removable": False,
                "renamable": False,
                "show_legend": True,
                "legend_url": None,
            },
        )

    def test__build_mv_layer_custom_args(self):
        source_options = {
            "url": "http://example.com/geoserver/wms",
            "params": {"LAYERS": "foo:bar"},
            "serverType": "geoserver",
        }

        ret = MapLayoutMixin._build_mv_layer(
            layer_source="TileWMS",
            layer_name="foo:bar",
            layer_title="Foo Bar",
            layer_variable="baz",
            options=source_options,
            layer_id="12345",
            extent=[-50, 25, -130, 50],
            visible=False,
            public=False,
            selectable=True,
            plottable=True,
            has_action=True,
            excluded_properties=["foo", "bar"],
            popup_title="Goo Baz",
            geometry_attribute="foo",
            style_map=copy.deepcopy(self.style_map),
            show_download=True,
            times=["20210322T112511Z", "20210322T122511Z", "20210322T132511Z"],
            removable=True,
            renamable=True,
            show_legend=False,
            label_options={"label_property": "qux"},
        )

        self.assertIsInstance(ret, MVLayer)
        self.assertEqual(ret.legend_title, "Foo Bar")
        self.assertListEqual(ret.legend_extent, [-50, 25, -130, 50])
        self.assertListEqual(
            ret.times, ["20210322T112511Z", "20210322T122511Z", "20210322T132511Z"]
        )
        self.assertTrue(ret.feature_selection)
        self.assertListEqual(ret.legend_classes, [])
        self.assertDictEqual(ret.options, source_options)
        self.assertDictEqual(
            ret.layer_options,
            {
                "visible": False,
                "show_download": True,
                "style_map": self.style_map,
                "label_options": {"label_property": "qux"},
            },
        )
        self.assertDictEqual(
            ret.data,
            {
                "layer_id": "12345",
                "layer_name": "foo:bar",
                "popup_title": "Goo Baz",
                "layer_variable": "baz",
                "toggle_status": False,
                "plottable": True,
                "has_action": True,
                "excluded_properties": [
                    "id",
                    "type",
                    "layer_name",
                    "plot",
                    "foo",
                    "bar",
                ],
                "removable": True,
                "renamable": True,
                "show_legend": False,
                "legend_url": None,
            },
        )

    def test_build_layer_group_default(self):
        layers = [{"layer_name": "foo:bar"}, {"layer_name": "foo:baz"}]

        ret = MapLayoutMixin.build_layer_group(
            id="foo_bar", display_name="Foo Bar", layers=layers
        )

        self.assertDictEqual(
            ret,
            {
                "id": "foo_bar",
                "display_name": "Foo Bar",
                "control": "checkbox",
                "layers": layers,
                "visible": True,
                "toggle_status": True,
                "removable": False,
                "renamable": False,
                "collapsed": False,
            },
        )

    def test_build_layer_group_custom_args(self):
        layers = [{"layer_name": "foo:bar"}, {"layer_name": "foo:baz"}]

        ret = MapLayoutMixin.build_layer_group(
            id="foo_bar",
            display_name="Foo Bar",
            layers=layers,
            layer_control="radio",
            visible=False,
            public=False,
            removable=True,
            renamable=True,
            collapsed=True,
        )

        self.assertDictEqual(
            ret,
            {
                "id": "foo_bar",
                "display_name": "Foo Bar",
                "control": "radio",
                "layers": layers,
                "visible": False,
                "toggle_status": False,
                "removable": True,
                "renamable": True,
                "collapsed": True,
            },
        )

    def test_build_layer_group_invalid_layer_control(self):
        layers = [{"layer_name": "foo:bar"}, {"layer_name": "foo:baz"}]

        with self.assertRaises(ValueError) as cm:
            MapLayoutMixin.build_layer_group(
                id="foo_bar",
                display_name="Foo Bar",
                layers=layers,
                layer_control="invalid",
            )

        self.assertEqual(
            'Invalid layer_control. Must be on of "checkbox" or "radio".',
            str(cm.exception),
        )

    def test_build_custom_layer_group_default(self):
        ret = MapLayoutMixin.build_custom_layer_group()

        self.assertDictEqual(
            ret,
            {
                "id": "custom_layers",
                "display_name": "Custom Layers",
                "control": "checkbox",
                "layers": [],
                "visible": True,
                "toggle_status": True,
                "removable": False,
                "renamable": False,
                "collapsed": False,
            },
        )

    def test_build_custom_layer_group_custom_args(self):
        layers = [{"layer_name": "foo:bar"}, {"layer_name": "foo:baz"}]

        ret = MapLayoutMixin.build_custom_layer_group(
            display_name="Foo Bar",
            layers=layers,
            layer_control="radio",
            visible=False,
            renamable=True,
            removable=True,
            collapsed=True,
        )

        self.assertDictEqual(
            ret,
            {
                "id": "custom_layers",
                "display_name": "Foo Bar",
                "control": "radio",
                "layers": layers,
                "visible": False,
                "toggle_status": True,
                "removable": True,
                "renamable": True,
                "collapsed": True,
            },
        )

    def test_build_param_string(self):
        kwargs = {
            "c3": "#fff100",
            "c4": "#ff8c00",
            "c5": "#e81123",
            "c6": "#ec008c",
            "c7": "#68217a",
            "v3": "0.5",
            "v4": "4.0",
            "v5": "7.5",
            "v6": "11.0",
            "v7": "14.5",
            "val_no_data": "-999",
        }
        ret = MapLayoutMixin.build_param_string(**kwargs)
        self.assertEqual(
            "c3:#fff100;c4:#ff8c00;c5:#e81123;c6:#ec008c;c7:#68217a;"
            "v3:0.5;v4:4.0;v5:7.5;v6:11.0;v7:14.5;val_no_data:-999",
            ret,
        )

    def test_build_param_string_no_kwargs(self):
        ret = MapLayoutMixin.build_param_string()
        self.assertEqual("", ret)

    def test_build_legend_color_ramp_division_kwargs_and_layer_id(self):
        layer = MVLayer(
            source="TileWMS",
            options={
                "url": "http://example.com/thredds/wms",
                "params": {
                    "LAYERS": "foo_bar.nc",
                },
                "serverType": "geoserver",
            },
            legend_title="Foo Bar",
            data={
                "layer_id": "12345",
                "layer_name": "foo:bar",
                "color_ramp_division_kwargs": dict(
                    min_value=0,
                    max_value=15,
                    num_divisions=5,
                    value_precision=1,
                    first_division=3,
                    top_offset=0.5,
                    bottom_offset=0.5,
                    prefix="v",
                    color_ramp="Galaxy Berry",
                    color_prefix="c",
                    no_data_value="-999",
                ),
                "legend_url": None,
            },
        )

        ret = MapLayoutMixin.build_legend(layer, units="ft")

        self.assertDictEqual(
            ret,
            {
                "color_list": [
                    "Default",
                    "Blue",
                    "Blue and Red",
                    "Elevated",
                    "Flower Field",
                    "Galaxy Berries",
                    "Heat Map",
                    "Olive Harmony",
                    "Mother Earth",
                    "Rainbow",
                    "Rainforest Frogs",
                    "Retro FLow",
                    "Sunset Fade",
                ],
                "color_prefix": "c",
                "color_ramp": "Galaxy Berry",
                "divisions": OrderedDict(
                    [
                        (0.5, "#fff100"),
                        (4.0, "#ff8c00"),
                        (7.5, "#e81123"),
                        (11.0, "#ec008c"),
                        (14.5, "#68217a"),
                    ]
                ),
                "first_division": 3,
                "initial_option": "Galaxy Berry",
                "layer_id": "12345",
                "legend_id": "legend-for-12345",
                "max_value": 15,
                "min_value": 0,
                "prefix": "v",
                "select_options": [
                    ("Default", "Default"),
                    ("Blue", "Blue"),
                    ("Blue and Red", "Blue and Red"),
                    ("Elevated", "Elevated"),
                    ("Flower Field", "Flower Field"),
                    ("Galaxy Berries", "Galaxy Berries"),
                    ("Heat Map", "Heat Map"),
                    ("Olive Harmony", "Olive Harmony"),
                    ("Mother Earth", "Mother Earth"),
                    ("Rainbow", "Rainbow"),
                    ("Rainforest Frogs", "Rainforest Frogs"),
                    ("Retro FLow", "Retro FLow"),
                    ("Sunset Fade", "Sunset Fade"),
                ],
                "title": "Foo Bar",
                "type": "custom-divisions",
                "units": "ft",
            },
        )

    def test_build_legend_color_ramp_division_kwargs_minimal_and_units(self):
        layer = MVLayer(
            source="TileWMS",
            options={
                "url": "http://example.com/thredds/wms",
                "params": {
                    "LAYERS": "foo_bar.nc",
                },
                "serverType": "geoserver",
            },
            legend_title="Foo Bar",
            data={
                "layer_name": "foo:bar",
                "color_ramp_division_kwargs": dict(
                    min_value=0,
                    max_value=15,
                ),
            },
        )

        ret = MapLayoutMixin.build_legend(layer, units="ft")

        self.assertDictEqual(
            ret,
            {
                "color_list": [
                    "Default",
                    "Blue",
                    "Blue and Red",
                    "Elevated",
                    "Flower Field",
                    "Galaxy Berries",
                    "Heat Map",
                    "Olive Harmony",
                    "Mother Earth",
                    "Rainbow",
                    "Rainforest Frogs",
                    "Retro FLow",
                    "Sunset Fade",
                ],
                "color_prefix": "color",
                "color_ramp": "Default",
                "divisions": OrderedDict(
                    [
                        (-0.0, "#fff100"),
                        (1.67, "#ff8c00"),
                        (3.33, "#e81123"),
                        (5.0, "#ec008c"),
                        (6.67, "#68217a"),
                        (8.33, "#00188f"),
                        (10.0, "#00bcf2"),
                        (11.67, "#00b294"),
                        (13.33, "#009e49"),
                        (15.0, "#bad80a"),
                    ]
                ),
                "first_division": 1,
                "initial_option": "Default",
                "layer_id": "foo:bar",
                "legend_id": "legend-for-foo_bar",
                "max_value": 15,
                "min_value": 0,
                "prefix": "val",
                "select_options": [
                    ("Default", "Default"),
                    ("Blue", "Blue"),
                    ("Blue and Red", "Blue and Red"),
                    ("Elevated", "Elevated"),
                    ("Flower Field", "Flower Field"),
                    ("Galaxy Berries", "Galaxy Berries"),
                    ("Heat Map", "Heat Map"),
                    ("Olive Harmony", "Olive Harmony"),
                    ("Mother Earth", "Mother Earth"),
                    ("Rainbow", "Rainbow"),
                    ("Rainforest Frogs", "Rainforest Frogs"),
                    ("Retro FLow", "Retro FLow"),
                    ("Sunset Fade", "Sunset Fade"),
                ],
                "title": "Foo Bar",
                "type": "custom-divisions",
                "units": "ft",
            },
        )

    def test_build_legend_thredds_and_no_layer_id(self):
        layer = MVLayer(
            source="TileWMS",
            legend_title="Foo Bar",
            data={
                "layer_name": "foo_bar.nc",
                "layer_variable": "baz",
            },
            options={
                "url": "http://example.com/thredds/wms",
                "params": {"LAYERS": "foo_bar.nc"},
                "serverType": "thredds",
            },
        )

        ret = MapLayoutMixin.build_legend(layer)

        self.assertDictEqual(
            ret,
            {
                "default_palette": "Default",
                "initial_option": "Default",
                "layer_id": "foo_bar.nc",
                "legend_id": "legend-for-foo_bar.nc",
                "palettes": [
                    "boxfill/alg",
                    "boxfill/alg2",
                    "boxfill/ferret",
                    "boxfill/greyscale",
                    "boxfill/ncview",
                    "boxfill/occam",
                    "boxfill/occam_pastel-30",
                    "boxfill/rainbow",
                    "boxfill/redblue",
                    "boxfill/sst_36",
                ],
                "select_options": [
                    ("Default", ""),
                    ("Alg", "boxfill/alg"),
                    ("Alg2", "boxfill/alg2"),
                    ("Ferret", "boxfill/ferret"),
                    ("Greyscale", "boxfill/greyscale"),
                    ("Ncview", "boxfill/ncview"),
                    ("Occam", "boxfill/occam"),
                    ("Occam_Pastel-30", "boxfill/occam_pastel-30"),
                    ("Rainbow", "boxfill/rainbow"),
                    ("Redblue", "boxfill/redblue"),
                    ("Sst_36", "boxfill/sst_36"),
                ],
                "title": "Foo Bar",
                "type": "thredds-wms-legend",
                "url": "http://example.com/thredds/wms?REQUEST=GetLegendGraphic&LAYER=foo_bar.nc",
            },
        )

    @mock.patch("tethys_layouts.mixins.map_layout.log")
    def test_build_legend_thredds_no_params(self, mock_log):
        layer = MVLayer(
            source="TileWMS",
            legend_title="Foo Bar",
            data={"layer_name": "foo_bar.nc", "layer_variable": "baz"},
            options={
                "url": "http://example.com/thredds/wms",
                "serverType": "thredds",
            },
        )

        ret = MapLayoutMixin.build_legend(layer, units="ft")

        self.assertIsNone(ret)
        mock_log.error.assert_called_with(
            "Legend Creation Error: No params found for given layer: {'source': 'TileWMS', 'legend_title': "
            "'Foo Bar', 'options': {'url': 'http://example.com/thredds/wms', "
            "'serverType': 'thredds'}, 'editable': True, 'layer_options': None, "
            "'legend_classes': None, 'legend_extent': None, 'legend_extent_projection': "
            "'EPSG:4326', 'feature_selection': None, 'geometry_attribute': None, "
            "'data': {'layer_name': 'foo_bar.nc', 'layer_variable': 'baz'}, "
            "'times': None}"
        )

    def test_build_legend_geoserver_with_layer_id(self):
        layer = MVLayer(
            source="TileWMS",
            legend_title="Foo Bar",
            data={"layer_name": "foo_bar", "layer_variable": "baz", "layer_id": "baz"},
            options={
                "url": "http://example.com:8181/geoserver/wms",
                "params": {"LAYERS": "foo_bar"},
                "serverType": "geoserver",
            },
        )

        ret = MapLayoutMixin.build_legend(layer)
        self.assertDictEqual(
            ret,
            {
                "initial_option": None,
                "layer_id": "baz",
                "legend_id": "legend-for-baz",
                "select_options": None,
                "title": "Foo Bar",
                "type": "geoserver-wms-legend",
                "url": "http://example.com:8181/geoserver/wms?REQUEST=GetLegendGraphic"
                "&VERSION=1.0.0&FORMAT=image/png&LEGEND_OPTIONS=bgColor:0xEFEFEF;labelMargin:10;dpi:100"
                "&LAYER=foo_bar",
            },
        )

    def test_build_legend_geoserver_with_layer_id_with_colon(self):
        layer = MVLayer(
            source="TileWMS",
            legend_title="Foo Bar",
            data={
                "layer_name": "foo_bar",
                "layer_variable": "baz",
                "layer_id": "baz:foo",
            },
            options={
                "url": "http://example.com:8181/geoserver/wms",
                "params": {"LAYERS": "foo_bar"},
                "serverType": "geoserver",
            },
        )

        ret = MapLayoutMixin.build_legend(layer)
        self.assertDictEqual(
            ret,
            {
                "initial_option": None,
                "layer_id": "baz:foo",
                "legend_id": "legend-for-baz_foo",
                "select_options": None,
                "title": "Foo Bar",
                "type": "geoserver-wms-legend",
                "url": "http://example.com:8181/geoserver/wms?REQUEST=GetLegendGraphic"
                "&VERSION=1.0.0&FORMAT=image/png&LEGEND_OPTIONS=bgColor:0xEFEFEF;labelMargin:10;dpi:100"
                "&LAYER=foo_bar",
            },
        )

    def test_build_legend_geoserver_with_layer_id_with_comma(self):
        layer = MVLayer(
            source="TileWMS",
            legend_title="Foo Bar",
            data={
                "layer_name": "foo_bar",
                "layer_variable": "baz",
                "layer_id": "baz,foo",
            },
            options={
                "url": "http://example.com:8181/geoserver/wms",
                "params": {"LAYERS": "foo_bar"},
                "serverType": "geoserver",
            },
        )

        ret = MapLayoutMixin.build_legend(layer)
        self.assertDictEqual(
            ret,
            {
                "initial_option": None,
                "layer_id": "baz,foo",
                "legend_id": "legend-for-baz_foo",
                "select_options": None,
                "title": "Foo Bar",
                "type": "geoserver-wms-legend",
                "url": "http://example.com:8181/geoserver/wms?REQUEST=GetLegendGraphic"
                "&VERSION=1.0.0&FORMAT=image/png&LEGEND_OPTIONS=bgColor:0xEFEFEF;labelMargin:10;dpi:100"
                "&LAYER=foo_bar",
            },
        )

    def test_build_legend_geoserver_with_multiple_styles(self):
        layer = MVLayer(
            source="TileWMS",
            legend_title="Foo Bar",
            data={"layer_name": "foo_bar", "layer_variable": "baz", "layer_id": "baz"},
            options={
                "url": "http://example.com:8181/geoserver/wms",
                "params": {"LAYERS": "foo_bar", "STYLES": "foo_style,bar_style"},
                "serverType": "geoserver",
            },
        )

        ret = MapLayoutMixin.build_legend(layer)
        self.assertDictEqual(
            ret,
            {
                "initial_option": "Default",
                "layer_id": "baz",
                "legend_id": "legend-for-baz",
                "select_options": [
                    ("Default", ""),
                    ("Foo Style", "foo_style"),
                    ("Bar Style", "bar_style"),
                ],
                "title": "Foo Bar",
                "type": "geoserver-wms-legend",
                "url": "http://example.com:8181/geoserver/wms?REQUEST=GetLegendGraphic"
                "&VERSION=1.0.0&FORMAT=image/png&LEGEND_OPTIONS=bgColor:0xEFEFEF;labelMargin:10;dpi:100"
                "&LAYER=foo_bar",
            },
        )

    def test_build_legend_geoserver_with_multiple_styles_with_workspaces(self):
        layer = MVLayer(
            source="TileWMS",
            legend_title="Foo Bar",
            data={"layer_name": "foo_bar", "layer_variable": "baz", "layer_id": "baz"},
            options={
                "url": "http://example.com:8181/geoserver/wms",
                "params": {
                    "LAYERS": "foo_bar",
                    "STYLES": "baz:foo_style,baz:bar_style",
                },
                "serverType": "geoserver",
            },
        )

        ret = MapLayoutMixin.build_legend(layer)
        self.assertDictEqual(
            ret,
            {
                "initial_option": "Default",
                "layer_id": "baz",
                "legend_id": "legend-for-baz",
                "select_options": [
                    ("Default", ""),
                    ("Foo Style", "baz:foo_style"),
                    ("Bar Style", "baz:bar_style"),
                ],
                "title": "Foo Bar",
                "type": "geoserver-wms-legend",
                "url": "http://example.com:8181/geoserver/wms?REQUEST=GetLegendGraphic"
                "&VERSION=1.0.0&FORMAT=image/png&LEGEND_OPTIONS=bgColor:0xEFEFEF;labelMargin:10;dpi:100"
                "&LAYER=foo_bar",
            },
        )

    def test_build_legend_geoserver_with_one_style(self):
        layer = MVLayer(
            source="TileWMS",
            legend_title="Foo Bar",
            data={"layer_name": "foo_bar", "layer_variable": "baz", "layer_id": "baz"},
            options={
                "url": "http://example.com:8181/geoserver/wms",
                "params": {"LAYERS": "foo_bar", "STYLES": "foo_style"},
                "serverType": "geoserver",
            },
        )

        ret = MapLayoutMixin.build_legend(layer)
        self.assertDictEqual(
            ret,
            {
                "initial_option": None,
                "layer_id": "baz",
                "legend_id": "legend-for-baz",
                "select_options": None,
                "title": "Foo Bar",
                "type": "geoserver-wms-legend",
                "url": "http://example.com:8181/geoserver/wms?REQUEST=GetLegendGraphic"
                "&VERSION=1.0.0&FORMAT=image/png&LEGEND_OPTIONS=bgColor:0xEFEFEF;labelMargin:10;dpi:100"
                "&LAYER=foo_bar",
            },
        )

    def test_build_legend_image_url(self):
        layer = MVLayer(
            source="TileWMS",
            legend_title="Foo Bar",
            data={
                "layer_name": "foo_bar",
                "layer_variable": "baz",
                "layer_id": "baz",
                "legend_url": "http://example.com/legend.png",
            },
            options={
                "url": "http://example.com:8181/geoserver/wms",
                "params": {"LAYERS": "foo_bar", "STYLES": "foo_style"},
                "serverType": "geoserver",
            },
        )
        ret = MapLayoutMixin.build_legend(layer)
        self.assertDictEqual(
            ret,
            {
                "layer_id": "baz",
                "legend_id": "legend-for-baz",
                "title": "Foo Bar",
                "type": "image-url-legend",
                "url": "http://example.com/legend.png",
            },
        )

    def test_build_geojson_layer_default(self):
        class CustomMapLayoutThing(MapLayoutMixin):
            map_extent = [-65.69, 23.81, -129.17, 49.38]

            @classmethod
            def get_vector_style_map(cls):
                return copy.deepcopy(self.style_map)

        ret = CustomMapLayoutThing.build_geojson_layer(
            geojson=copy.deepcopy(self.geojson_object),
            layer_name="foo:bar",
            layer_title="Foo Bar",
            layer_variable="baz",
        )

        self.assertIsInstance(ret, MVLayer)
        self.assertEqual(ret.source, "GeoJSON")
        self.assertEqual(ret.legend_title, "Foo Bar")
        self.assertListEqual(ret.legend_classes, [])
        self.assertDictEqual(
            ret.layer_options,
            {"visible": True, "show_download": False, "style_map": self.style_map},
        )
        self.assertDictEqual(
            ret.data,
            {
                "layer_id": "foo:bar",
                "layer_name": "foo:bar",
                "popup_title": "Foo Bar",
                "layer_variable": "baz",
                "toggle_status": True,
                "excluded_properties": ["id", "type", "layer_name"],
                "removable": False,
                "renamable": False,
                "show_legend": True,
                "legend_url": None,
            },
        )
        self.assertEqual(ret.options["type"], "FeatureCollection")
        self.assertEqual(len(ret.options["features"]), 3)
        for feature in ret.options["features"]:
            self.assertEqual(feature["properties"]["layer_name"], "foo:bar")

    def test_build_wms_layer_default(self):
        class CustomMapLayoutThing(MapLayoutMixin):
            map_extent = [-65.69, 23.81, -129.17, 49.38]

        ret = CustomMapLayoutThing.build_wms_layer(
            endpoint="http://example.com/geoserver/wms",
            layer_name="foo:bar",
            layer_title="Foo Bar",
            layer_variable="baz",
        )

        self.assertIsInstance(ret, MVLayer)
        self.assertEqual(ret.source, "TileWMS")
        self.assertEqual(ret.legend_title, "Foo Bar")
        self.assertListEqual(ret.legend_extent, [-65.69, 23.81, -129.17, 49.38])
        self.assertFalse(ret.feature_selection)
        self.assertListEqual(ret.legend_classes, [])
        self.assertDictEqual(
            ret.options,
            {
                "url": "http://example.com/geoserver/wms",
                "params": {
                    "LAYERS": "foo:bar",
                    "TILED": True,
                    "TILESORIGIN": "0.0,0.0",
                },
                "serverType": "geoserver",
                "crossOrigin": None,
                "tileGrid": _DEFAULT_TILE_GRID,
            },
        )
        self.assertDictEqual(
            ret.layer_options, {"visible": True, "show_download": False}
        )
        self.assertDictEqual(
            ret.data,
            {
                "layer_id": "foo:bar",
                "layer_name": "foo:bar",
                "popup_title": "Foo Bar",
                "layer_variable": "baz",
                "toggle_status": True,
                "excluded_properties": ["id", "type", "layer_name"],
                "removable": False,
                "renamable": False,
                "show_legend": True,
                "legend_url": None,
            },
        )

    def test_build_wms_layer_not_tiled(self):
        class CustomMapLayoutThing(MapLayoutMixin):
            map_extent = [-65.69, 23.81, -129.17, 49.38]

        ret = CustomMapLayoutThing.build_wms_layer(
            endpoint="http://example.com/geoserver/wms",
            layer_name="foo:bar",
            layer_title="Foo Bar",
            layer_variable="baz",
            tiled=False,
        )

        self.assertIsInstance(ret, MVLayer)
        self.assertEqual(ret.source, "ImageWMS")
        self.assertEqual(ret.legend_title, "Foo Bar")
        self.assertListEqual(ret.legend_extent, [-65.69, 23.81, -129.17, 49.38])
        self.assertFalse(ret.feature_selection)
        self.assertListEqual(ret.legend_classes, [])
        self.assertDictEqual(
            ret.options,
            {
                "url": "http://example.com/geoserver/wms",
                "params": {
                    "LAYERS": "foo:bar",
                },
                "serverType": "geoserver",
                "crossOrigin": None,
            },
        )
        self.assertDictEqual(
            ret.layer_options, {"visible": True, "show_download": False}
        )
        self.assertDictEqual(
            ret.data,
            {
                "layer_id": "foo:bar",
                "layer_name": "foo:bar",
                "popup_title": "Foo Bar",
                "layer_variable": "baz",
                "toggle_status": True,
                "excluded_properties": ["id", "type", "layer_name"],
                "removable": False,
                "renamable": False,
                "show_legend": True,
                "legend_url": None,
            },
        )

    def test_build_wms_layer_env_viewparams_style(self):
        class CustomMapLayoutThing(MapLayoutMixin):
            map_extent = [-65.69, 23.81, -129.17, 49.38]

        ret = CustomMapLayoutThing.build_wms_layer(
            endpoint="http://example.com/geoserver/wms",
            layer_name="foo:bar",
            layer_title="Foo Bar",
            layer_variable="baz",
            env="foo:1;bar:baz",
            viewparams="low:2000000;high:5000000",
            styles="foobar",
        )

        self.assertIsInstance(ret, MVLayer)
        self.assertEqual(ret.source, "TileWMS")
        self.assertEqual(ret.legend_title, "Foo Bar")
        self.assertListEqual(ret.legend_extent, [-65.69, 23.81, -129.17, 49.38])
        self.assertFalse(ret.feature_selection)
        self.assertListEqual(ret.legend_classes, [])
        self.assertDictEqual(
            ret.options,
            {
                "url": "http://example.com/geoserver/wms",
                "params": {
                    "LAYERS": "foo:bar",
                    "TILED": True,
                    "TILESORIGIN": "0.0,0.0",
                    "VIEWPARAMS": "low:2000000;high:5000000",
                    "ENV": "foo:1;bar:baz",
                    "STYLES": "foobar",
                },
                "serverType": "geoserver",
                "crossOrigin": None,
                "tileGrid": _DEFAULT_TILE_GRID,
            },
        )
        self.assertDictEqual(
            ret.layer_options, {"visible": True, "show_download": False}
        )
        self.assertDictEqual(
            ret.data,
            {
                "layer_id": "foo:bar",
                "layer_name": "foo:bar",
                "popup_title": "Foo Bar",
                "layer_variable": "baz",
                "toggle_status": True,
                "excluded_properties": ["id", "type", "layer_name"],
                "removable": False,
                "renamable": False,
                "show_legend": True,
                "legend_url": None,
            },
        )

    def test_build_wms_layer_color_ramp_division_kwargs(self):
        class CustomMapLayoutThing(MapLayoutMixin):
            map_extent = [-65.69, 23.81, -129.17, 49.38]

        ret = CustomMapLayoutThing.build_wms_layer(
            endpoint="http://example.com/geoserver/wms",
            layer_name="foo:bar",
            layer_title="Foo Bar",
            layer_variable="baz",
            color_ramp_division_kwargs=dict(
                min_value=0,
                max_value=15,
                num_divisions=3,
            ),
        )

        self.assertIsInstance(ret, MVLayer)
        self.assertEqual(ret.source, "TileWMS")
        self.assertEqual(ret.legend_title, "Foo Bar")
        self.assertListEqual(ret.legend_extent, [-65.69, 23.81, -129.17, 49.38])
        self.assertFalse(ret.feature_selection)
        self.assertListEqual(ret.legend_classes, [])
        self.assertDictEqual(
            ret.options,
            {
                "url": "http://example.com/geoserver/wms",
                "params": {
                    "LAYERS": "foo:bar",
                    "TILED": True,
                    "TILESORIGIN": "0.0,0.0",
                    "ENV": "val1:0.00;color1:#fff100;val2:7.50;color2:#ff8c00;val3:15.00;color3:#e81123",
                },
                "serverType": "geoserver",
                "crossOrigin": None,
                "tileGrid": _DEFAULT_TILE_GRID,
            },
        )
        self.assertDictEqual(
            ret.layer_options, {"visible": True, "show_download": False}
        )
        self.assertDictEqual(
            ret.data,
            {
                "layer_id": "foo:bar",
                "layer_name": "foo:bar",
                "popup_title": "Foo Bar",
                "layer_variable": "baz",
                "toggle_status": True,
                "excluded_properties": ["id", "type", "layer_name"],
                "removable": False,
                "renamable": False,
                "show_legend": True,
                "legend_url": None,
            },
        )

    def test_build_wms_layer_color_ramp_division_kwargs_and_env(self):
        class CustomMapLayoutThing(MapLayoutMixin):
            map_extent = [-65.69, 23.81, -129.17, 49.38]

        ret = CustomMapLayoutThing.build_wms_layer(
            endpoint="http://example.com/geoserver/wms",
            layer_name="foo:bar",
            layer_title="Foo Bar",
            layer_variable="baz",
            env="foo:1;bar:baz",
            color_ramp_division_kwargs=dict(
                min_value=0,
                max_value=15,
                num_divisions=3,
            ),
        )

        self.assertIsInstance(ret, MVLayer)
        self.assertEqual(ret.source, "TileWMS")
        self.assertEqual(ret.legend_title, "Foo Bar")
        self.assertListEqual(ret.legend_extent, [-65.69, 23.81, -129.17, 49.38])
        self.assertFalse(ret.feature_selection)
        self.assertListEqual(ret.legend_classes, [])
        self.assertDictEqual(
            ret.options,
            {
                "url": "http://example.com/geoserver/wms",
                "params": {
                    "LAYERS": "foo:bar",
                    "TILED": True,
                    "TILESORIGIN": "0.0,0.0",
                    "ENV": "foo:1;bar:baz;val1:0.00;color1:#fff100;val2:7.50;color2:#ff8c00;val3:15.00;color3:#e81123",
                },
                "serverType": "geoserver",
                "crossOrigin": None,
                "tileGrid": _DEFAULT_TILE_GRID,
            },
        )
        self.assertDictEqual(
            ret.layer_options, {"visible": True, "show_download": False}
        )
        self.assertDictEqual(
            ret.data,
            {
                "layer_id": "foo:bar",
                "layer_name": "foo:bar",
                "popup_title": "Foo Bar",
                "layer_variable": "baz",
                "toggle_status": True,
                "excluded_properties": ["id", "type", "layer_name"],
                "removable": False,
                "renamable": False,
                "show_legend": True,
                "legend_url": None,
            },
        )

    def test_build_wms_layer_times(self):
        class CustomMapLayoutThing(MapLayoutMixin):
            map_extent = [-65.69, 23.81, -129.17, 49.38]

        ret = CustomMapLayoutThing.build_wms_layer(
            endpoint="http://example.com/geoserver/wms",
            layer_name="foo:bar",
            layer_title="Foo Bar",
            layer_variable="baz",
            env="foo:1;bar:baz",
            times=["20210322T112511Z", "20210322T122511Z", "20210322T132511Z"],
        )

        self.assertIsInstance(ret, MVLayer)
        self.assertEqual(ret.source, "TileWMS")
        self.assertEqual(ret.legend_title, "Foo Bar")
        self.assertListEqual(ret.legend_extent, [-65.69, 23.81, -129.17, 49.38])
        self.assertFalse(ret.feature_selection)
        self.assertListEqual(ret.legend_classes, [])
        self.assertEqual(
            ret.times, '["20210322T112511Z", "20210322T122511Z", "20210322T132511Z"]'
        )
        self.assertDictEqual(
            ret.options,
            {
                "url": "http://example.com/geoserver/wms",
                "params": {
                    "LAYERS": "foo:bar",
                    "TILED": True,
                    "TILESORIGIN": "0.0,0.0",
                    "ENV": "foo:1;bar:baz",
                },
                "serverType": "geoserver",
                "crossOrigin": None,
                "tileGrid": _DEFAULT_TILE_GRID,
            },
        )
        self.assertDictEqual(
            ret.layer_options, {"visible": True, "show_download": False}
        )
        self.assertDictEqual(
            ret.data,
            {
                "layer_id": "foo:bar",
                "layer_name": "foo:bar",
                "popup_title": "Foo Bar",
                "layer_variable": "baz",
                "toggle_status": True,
                "excluded_properties": ["id", "type", "layer_name"],
                "removable": False,
                "renamable": False,
                "show_legend": True,
                "legend_url": None,
            },
        )

    def test_build_wms_layer_cql_filter(self):
        class CustomMapLayoutThing(MapLayoutMixin):
            map_extent = [-65.69, 23.81, -129.17, 49.38]

        ret = CustomMapLayoutThing.build_wms_layer(
            endpoint="http://example.com/geoserver/wms",
            layer_name="foo:bar",
            layer_title="Foo Bar",
            layer_variable="baz",
            env="foo:1;bar:baz",
            cql_filter="baz > 1",
        )

        self.assertIsInstance(ret, MVLayer)
        self.assertEqual(ret.source, "TileWMS")
        self.assertEqual(ret.legend_title, "Foo Bar")
        self.assertListEqual(ret.legend_extent, [-65.69, 23.81, -129.17, 49.38])
        self.assertFalse(ret.feature_selection)
        self.assertListEqual(ret.legend_classes, [])
        self.assertDictEqual(
            ret.options,
            {
                "url": "http://example.com/geoserver/wms",
                "params": {
                    "LAYERS": "foo:bar",
                    "TILED": True,
                    "TILESORIGIN": "0.0,0.0",
                    "ENV": "foo:1;bar:baz",
                    "CQL_FILTER": "baz > 1",
                },
                "serverType": "geoserver",
                "crossOrigin": None,
                "tileGrid": _DEFAULT_TILE_GRID,
            },
        )
        self.assertDictEqual(
            ret.layer_options, {"visible": True, "show_download": False}
        )
        self.assertDictEqual(
            ret.data,
            {
                "layer_id": "foo:bar",
                "layer_name": "foo:bar",
                "popup_title": "Foo Bar",
                "layer_variable": "baz",
                "toggle_status": True,
                "excluded_properties": ["id", "type", "layer_name"],
                "removable": False,
                "renamable": False,
                "show_legend": True,
                "legend_url": None,
            },
        )

    def test_build_arc_gis_layer_default(self):
        class CustomMapLayoutThing(MapLayoutMixin):
            map_extent = [-65.69, 23.81, -129.17, 49.38]

        ret = CustomMapLayoutThing.build_arc_gis_layer(
            endpoint="https://sampleserver1.arcgisonline.com"
            "/ArcGIS/rest/services/Specialty/ESRI_StateCityHighway_USA/MapServer",
            layer_name="foo:bar",
            layer_title="Foo Bar",
            layer_variable="baz",
        )

        self.assertIsInstance(ret, MVLayer)
        self.assertEqual(ret.source, "TileArcGISRest")
        self.assertEqual(ret.legend_title, "Foo Bar")
        self.assertEqual(
            ret.options["url"],
            "https://sampleserver1.arcgisonline.com"
            "/ArcGIS/rest/services/Specialty/ESRI_StateCityHighway_USA/MapServer",
        )
        self.assertListEqual(ret.legend_classes, [])
        self.assertDictEqual(
            ret.layer_options, {"visible": True, "show_download": False}
        )
        self.assertDictEqual(
            ret.data,
            {
                "layer_id": "foo:bar",
                "layer_name": "foo:bar",
                "popup_title": "Foo Bar",
                "layer_variable": "baz",
                "toggle_status": True,
                "excluded_properties": ["id", "type", "layer_name"],
                "removable": False,
                "renamable": False,
                "show_legend": True,
                "legend_url": None,
            },
        )

    def test_build_custom_layer_geoserver_wms(self):
        class CustomMapLayoutThing(MapLayoutMixin):
            map_extent = [-65.69, 23.81, -129.17, 49.38]

        ret = CustomMapLayoutThing.build_custom_layer(
            service_type="WMS",
            service_endpoint="http://example.com/geoserver/wms",
            layer_name="foo:bar",
            layer_title="Foo Bar",
            layer_id="12345",
        )

        self.assertIsInstance(ret, MVLayer)
        self.assertEqual(ret.source, "TileWMS")
        self.assertEqual(ret.legend_title, "Foo Bar")
        self.assertListEqual(ret.legend_extent, [-65.69, 23.81, -129.17, 49.38])
        self.assertFalse(ret.feature_selection)
        self.assertListEqual(ret.legend_classes, [])
        self.assertDictEqual(
            ret.options,
            {
                "url": "http://example.com/geoserver/wms",
                "params": {
                    "LAYERS": "foo:bar",
                    "TILED": True,
                    "TILESORIGIN": "0.0,0.0",
                },
                "serverType": "geoserver",
                "crossOrigin": None,
                "tileGrid": _DEFAULT_TILE_GRID,
            },
        )
        self.assertDictEqual(
            ret.layer_options, {"visible": True, "show_download": False}
        )
        self.assertDictEqual(
            ret.data,
            {
                "layer_id": "12345",
                "layer_name": "foo:bar",
                "popup_title": "Foo Bar",
                "layer_variable": "custom",
                "toggle_status": True,
                "excluded_properties": ["id", "type", "layer_name"],
                "removable": True,
                "renamable": False,
                "show_legend": True,
                "legend_url": None,
            },
        )

    def test_build_custom_layer_thredds_wms(self):
        class CustomMapLayoutThing(MapLayoutMixin):
            map_extent = [-65.69, 23.81, -129.17, 49.38]

        ret = CustomMapLayoutThing.build_custom_layer(
            service_type="WMS",
            service_endpoint="https://tethys.byu.edu/thredds/wms/tethys/grace/GRC_jpl_tot.nc",
            layer_name="foobar",
            layer_title="Foo Bar",
            layer_id="12345",
        )

        self.assertIsInstance(ret, MVLayer)
        self.assertEqual(ret.source, "TileWMS")
        self.assertEqual(ret.legend_title, "Foo Bar")
        self.assertListEqual(ret.legend_extent, [-65.69, 23.81, -129.17, 49.38])
        self.assertFalse(ret.feature_selection)
        self.assertListEqual(ret.legend_classes, [])
        self.assertDictEqual(
            ret.options,
            {
                "url": "https://tethys.byu.edu/thredds/wms/tethys/grace/GRC_jpl_tot.nc",
                "params": {
                    "LAYERS": "foobar",
                    "TILED": True,
                    "TILESORIGIN": "0.0,0.0",
                },
                "serverType": "thredds",
                "crossOrigin": None,
                "tileGrid": _DEFAULT_TILE_GRID,
            },
        )
        self.assertDictEqual(
            ret.layer_options, {"visible": True, "show_download": False}
        )
        self.assertDictEqual(
            ret.data,
            {
                "layer_id": "12345",
                "layer_name": "foobar",
                "popup_title": "Foo Bar",
                "layer_variable": "custom",
                "toggle_status": True,
                "excluded_properties": ["id", "type", "layer_name"],
                "removable": True,
                "renamable": False,
                "show_legend": True,
                "legend_url": None,
            },
        )

    def test_build_custom_layer_arcgis(self):
        class CustomMapLayoutThing(MapLayoutMixin):
            map_extent = [-65.69, 23.81, -129.17, 49.38]

        ret = CustomMapLayoutThing.build_custom_layer(
            service_type="TileArcGISRest",
            service_endpoint="https://sampleserver1.arcgisonline.com"
            "/ArcGIS/rest/services/Specialty/ESRI_StateCityHighway_USA/MapServer",
            layer_name="foo:bar",
            layer_title="Foo Bar",
            layer_id="12345",
        )

        self.assertIsInstance(ret, MVLayer)
        self.assertEqual(ret.source, "TileArcGISRest")
        self.assertEqual(ret.legend_title, "Foo Bar")
        self.assertEqual(
            ret.options["url"],
            "https://sampleserver1.arcgisonline.com"
            "/ArcGIS/rest/services/Specialty/ESRI_StateCityHighway_USA/MapServer",
        )
        self.assertListEqual(ret.legend_classes, [])
        self.assertDictEqual(
            ret.layer_options, {"visible": True, "show_download": False}
        )
        self.assertDictEqual(
            ret.data,
            {
                "layer_id": "12345",
                "layer_name": "foo:bar",
                "popup_title": "Foo Bar",
                "layer_variable": "custom",
                "toggle_status": True,
                "excluded_properties": ["id", "type", "layer_name"],
                "removable": True,
                "renamable": False,
                "show_legend": True,
                "legend_url": None,
            },
        )

    def test_generate_custom_color_ramp_divisions_default(self):
        ret = MapLayoutMixin.generate_custom_color_ramp_divisions(
            min_value=0,
            max_value=15,
        )

        self.assertDictEqual(
            ret,
            {
                "color1": "#fff100",
                "color10": "#bad80a",
                "color2": "#ff8c00",
                "color3": "#e81123",
                "color4": "#ec008c",
                "color5": "#68217a",
                "color6": "#00188f",
                "color7": "#00bcf2",
                "color8": "#00b294",
                "color9": "#009e49",
                "val1": "-0.00",
                "val10": "15.00",
                "val2": "1.67",
                "val3": "3.33",
                "val4": "5.00",
                "val5": "6.67",
                "val6": "8.33",
                "val7": "10.00",
                "val8": "11.67",
                "val9": "13.33",
            },
        )

    def test_generate_custom_color_ramp_divisions_unknown_color_ramp_name(self):
        ret = MapLayoutMixin.generate_custom_color_ramp_divisions(
            min_value=0, max_value=15, color_ramp="doesnotexist"
        )

        self.assertDictEqual(
            ret,
            {
                "color1": "#fff100",
                "color10": "#bad80a",
                "color2": "#ff8c00",
                "color3": "#e81123",
                "color4": "#ec008c",
                "color5": "#68217a",
                "color6": "#00188f",
                "color7": "#00bcf2",
                "color8": "#00b294",
                "color9": "#009e49",
                "val1": "-0.00",
                "val10": "15.00",
                "val2": "1.67",
                "val3": "3.33",
                "val4": "5.00",
                "val5": "6.67",
                "val6": "8.33",
                "val7": "10.00",
                "val8": "11.67",
                "val9": "13.33",
            },
        )

    def test_generate_custom_color_ramp_divisions_custom_args(self):
        ret = MapLayoutMixin.generate_custom_color_ramp_divisions(
            min_value=0,
            max_value=15,
            num_divisions=5,
            value_precision=1,
            first_division=3,
            top_offset=0.5,
            bottom_offset=0.5,
            prefix="v",
            color_ramp="Galaxy Berries",
            color_prefix="c",
            no_data_value="-999",
        )

        self.assertDictEqual(
            ret,
            {
                "c3": "#0040bf",
                "c4": "#a3cc52",
                "c5": "#b9a087",
                "c6": "#a01fcc",
                "c7": "#5bb698",
                "v3": "0.5",
                "v4": "4.0",
                "v5": "7.5",
                "v6": "11.0",
                "v7": "14.5",
                "val_no_data": "-999",
            },
        )
