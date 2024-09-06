import unittest
import tethys_gizmos.gizmo_options.map_view as gizmo_map_view
from unittest import mock


class TestMapView(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch("tethys_gizmos.gizmo_options.map_view.deprecation_warning")
    def test_MapView(self, mock_deprecation):
        height = "500px"
        width = "90%"
        basemap = [
            "Aerial",
            "OpenStreetMap",
            "CartoDB",
            [
                {"CartoDB": {"style": "dark"}},
                {
                    "CartoDB": {
                        "style": "light",
                        "labels": False,
                        "control_label": "CartoDB-light-no-labels",
                    }
                },
            ],
            {
                "XYZ": {
                    "url": "https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png",
                    "control_label": "Wikimedia",
                }
            },
            "ESRI",
            "BING",
        ]
        controls = ["ZoomSlider", "Rotate", "FullScreen", "ScaleLine"]

        result = gizmo_map_view.MapView(
            height=height, width=width, basemap=basemap, controls=controls
        )

        # Check Result
        self.assertIn(height, result["height"])
        self.assertIn(width, result["width"])
        self.assertListEqual(basemap, result["basemap"])
        self.assertEqual(controls, result["controls"])

        self.assertIn(".js", gizmo_map_view.MapView.get_vendor_js()[0])
        self.assertIn(".js", gizmo_map_view.MapView.get_gizmo_js()[0])
        self.assertIn(".css", gizmo_map_view.MapView.get_vendor_css()[0])
        self.assertIn(".css", gizmo_map_view.MapView.get_gizmo_css()[0])
        mock_deprecation.assert_called_once()

    def test_MVView(self):
        projection = "EPSG:4326"
        center = [-100, 40]
        zoom = 10
        maxZoom = 20
        minZoom = 2

        result = gizmo_map_view.MVView(
            projection=projection,
            center=center,
            zoom=zoom,
            maxZoom=maxZoom,
            minZoom=minZoom,
        )

        # Check result
        self.assertIn(projection, result["projection"])
        self.assertListEqual(center, result["center"])
        self.assertEqual(zoom, result["zoom"])
        self.assertEqual(maxZoom, result["maxZoom"])
        self.assertEqual(minZoom, result["minZoom"])

    def test_MVView_center_defaults(self):
        center = [-100, 40]

        result = gizmo_map_view.MVView(center=center)

        # Check result
        self.assertEqual("EPSG:4326", result["projection"])
        self.assertListEqual(center, result["center"])
        self.assertEqual(4, result["zoom"])
        self.assertEqual(28, result["maxZoom"])
        self.assertEqual(0, result["minZoom"])
        self.assertIsNone(result["extent"])

    def test_MVView_extent_defaults(self):
        extent = [-100, 40, -80, 60]

        result = gizmo_map_view.MVView(extent=extent)

        # Check result
        self.assertEqual("EPSG:4326", result["projection"])
        self.assertListEqual(extent, result["extent"])
        self.assertEqual(4, result["zoom"])
        self.assertEqual(28, result["maxZoom"])
        self.assertEqual(0, result["minZoom"])
        self.assertIsNone(result["center"])

    def test_MVView_neither_extent_center(self):
        with self.assertRaises(ValueError) as cm:
            gizmo_map_view.MVView()

        # Check result
        self.assertEqual(
            'Either the "center" argument or the "extent" argument is required: neither were provided.',
            str(cm.exception),
        )

    def test_MVView_both_extent_center(self):
        with self.assertRaises(ValueError) as cm:
            gizmo_map_view.MVView(
                center=[-100, 40],
                extent=[-100, 40, -80, 60],
            )

        # Check result
        self.assertEqual(
            'The "center" and "extent" arguments are mutually exclusive: provide one or the other, not both.',
            str(cm.exception),
        )

    def test_MVDraw(self):
        controls = ["Modify", "Delete", "Move", "Point", "LineString", "Polygon", "Box"]
        initial = "Point"
        output_format = "GeoJSON"
        fill_color = "rgba(255,255,255,0.2)"
        line_color = "#663399"
        point_color = "#663399"

        result = gizmo_map_view.MVDraw(
            controls=controls,
            initial=initial,
            output_format=output_format,
            line_color=line_color,
            fill_color=fill_color,
            point_color=point_color,
        )

        # Check result
        self.assertEqual(controls, result["controls"])
        self.assertEqual(initial, result["initial"])
        self.assertEqual(output_format, result["output_format"])
        self.assertEqual(fill_color, result["fill_color"])
        self.assertEqual(line_color, result["line_color"])
        self.assertEqual(point_color, result["point_color"])

    def test_MVDraw_add_snapping_layer_special_cases(self):
        special_options = [
            "data",
            "legend_title",
            "legend_extent",
            "legend_extent_projection",
            "legend_classes",
            "editable",
        ]

        for option in special_options:
            snapping_layer = {"{}.foo".format(option): "bar"}
            result = gizmo_map_view.MVDraw(snapping_layer=snapping_layer)

            # Check result
            self.assertDictEqual(
                {"tethys_{}.foo".format(option): "bar"}, result.snapping_layer
            )

    def test_MVDraw_add_snapping_layer(self):
        snapping_layer = {"not_data.foo": "bar"}
        result = gizmo_map_view.MVDraw(snapping_layer=snapping_layer)

        # Check result
        self.assertDictEqual({"not_data.foo": "bar"}, result.snapping_layer)

    def test_MVDraw_invalid_initial_control(self):
        # Raise Error if Initial is not in Controls list
        self.assertRaises(ValueError, gizmo_map_view.MVDraw, initial="foo")

    def test_MVDraw_invalid_snapping_layer(self):
        test_snapping_layer = {"foo": 1, "bar": 1}
        # Raise Error if Initial is not in Controls list
        self.assertRaises(
            ValueError, gizmo_map_view.MVDraw, snapping_layer=test_snapping_layer
        )

    def test_MVLayer(self):
        source = "KML"
        legend_title = "Park City Watershed"
        options = {"url": "/static/tethys_gizmos/data/model.kml"}
        times = ["20210322T112511Z", "20210322T122511Z", "20210322T132511Z"]

        result = gizmo_map_view.MVLayer(
            source=source, legend_title=legend_title, options=options, times=times
        )

        # Check Result
        self.assertEqual(source, result["source"])
        self.assertEqual(legend_title, result["legend_title"])
        self.assertEqual(options, result["options"])
        self.assertEqual(times, result["times"])

    @mock.patch("tethys_gizmos.gizmo_options.map_view.log.warning")
    def test_MVLayer_warning(self, mock_log):
        source = "KML"
        legend_title = "Park City Watershed"
        options = {"url": "/static/tethys_gizmos/data/model.kml"}
        feature_selection = True

        gizmo_map_view.MVLayer(
            source=source,
            legend_title=legend_title,
            options=options,
            feature_selection=feature_selection,
        )

        mock_log.assert_called_with(
            "geometry_attribute not defined for layer 'Park City Watershed' "
            "-using default value 'the_geom'"
        )

    def test_MVLayer_geojson_source_geometry_attribute(self):
        source = "GeoJSON"
        legend_title = "GeoJSON Layer"
        geojson = {
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

        ret = gizmo_map_view.MVLayer(
            source=source, legend_title=legend_title, options=geojson
        )

        self.assertEqual("geometry", ret.geometry_attribute)

    @mock.patch("tethys_gizmos.gizmo_options.map_view.log.warning")
    def test_MVLayer_geojson_source_geometry_attribute_feature_selection(
        self, mock_warning
    ):
        source = "GeoJSON"
        legend_title = "GeoJSON Layer"
        feature_selection = True
        geojson = {
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

        ret = gizmo_map_view.MVLayer(
            source=source,
            legend_title=legend_title,
            options=geojson,
            feature_selection=feature_selection,
        )

        self.assertEqual("geometry", ret.geometry_attribute)

        mock_warning.assert_not_called()

    def test_MVLegendClass(self):
        # Point
        type_value = "point"
        value = "Point Legend"
        fill = "#00ff00"

        result = gizmo_map_view.MVLegendClass(type=type_value, value=value, fill=fill)

        # Check Result
        self.assertEqual(value, result["value"])
        self.assertEqual(fill, result["fill"])
        self.assertEqual(value, result["value"])

        # Point with No Fill
        self.assertRaises(
            ValueError, gizmo_map_view.MVLegendClass, type=type_value, value=value
        )

        # Not Valid Type
        self.assertRaises(
            ValueError, gizmo_map_view.MVLegendClass, type="points", value=value
        )

        # Line
        type_value = "line"
        value = "Line Legend"
        stroke = "#00ff01"
        result = gizmo_map_view.MVLegendClass(
            type=type_value, value=value, stroke=stroke
        )

        # Check Result
        self.assertEqual(type_value, result["type"])
        self.assertEqual(stroke, result["stroke"])
        self.assertEqual(value, result["value"])

        # Line with No Stroke
        self.assertRaises(
            ValueError, gizmo_map_view.MVLegendClass, type=type_value, value=value
        )

        # Polygon
        type_value = "polygon"
        value = "Polygon Legend"
        fill = "#00ff00"
        stroke = "#00ff01"

        result = gizmo_map_view.MVLegendClass(
            type=type_value, value=value, stroke=stroke, fill=fill
        )

        # Check Result
        self.assertEqual(type_value, result["type"])
        self.assertEqual(stroke, result["stroke"])
        self.assertEqual(fill, result["fill"])
        self.assertEqual(value, result["value"])

        # Polygon with no Stroke
        result = gizmo_map_view.MVLegendClass(type=type_value, value=value, fill=fill)

        # Check Result
        self.assertEqual(type_value, result["type"])
        self.assertEqual(fill, result["fill"])
        self.assertEqual(fill, result["line"])

        # Polygon with no fill
        self.assertRaises(
            ValueError, gizmo_map_view.MVLegendClass, type=type_value, value=value
        )

        # Raster
        type_value = "raster"
        value = "Raster Legend"
        ramp = ["#00ff00", "#00ff01", "#00ff02"]

        result = gizmo_map_view.MVLegendClass(type=type_value, value=value, ramp=ramp)

        # Check Result
        self.assertEqual(type_value, result["type"])
        self.assertEqual(ramp, result["ramp"])

        # Raster without ramp
        self.assertRaises(
            ValueError, gizmo_map_view.MVLegendClass, type=type_value, value=value
        )

    def test_MVLegendImageClass(self):
        value = "image legend"
        image_url = "www.aquaveo.com/image.png"

        result = gizmo_map_view.MVLegendImageClass(value=value, image_url=image_url)

        # Check Result
        self.assertEqual(value, result["value"])
        self.assertEqual(image_url, result["image_url"])

    def test_MVLegendGeoServerImageClass(self):
        value = "Cities"
        geoserver_url = "http://localhost:8181/geoserver"
        style = "green"
        layer = "rivers"
        width = 20
        height = 10

        image_url = (
            "{0}/wms?REQUEST=GetLegendGraphic&VERSION=1.0.0&"
            "STYLE={1}&FORMAT=image/png&WIDTH={2}&HEIGHT={3}&"
            "LEGEND_OPTIONS=forceRule:true&"
            "LAYER={4}".format(geoserver_url, style, width, height, layer)
        )

        result = gizmo_map_view.MVLegendGeoServerImageClass(
            value=value,
            geoserver_url=geoserver_url,
            style=style,
            layer=layer,
            width=width,
            height=height,
        )

        # Check Result
        self.assertEqual(value, result["value"])
        self.assertEqual(image_url, result["image_url"])
