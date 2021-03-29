import unittest
import tethys_gizmos.gizmo_options.map_view as gizmo_map_view
from unittest import mock


class MockObject:
    def __init__(self, debug=True):
        self.DEBUG = debug


class TestMapView(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_MapView(self):
        height = '500px'
        width = '90%'
        basemap = 'Aerial'
        controls = ['ZoomSlider', 'Rotate', 'FullScreen', 'ScaleLine']

        result = gizmo_map_view.MapView(height=height, width=width, basemap=basemap, controls=controls)

        # Check Result
        self.assertIn(height, result['height'])
        self.assertIn(width, result['width'])
        self.assertIn(basemap, result['basemap'])
        self.assertEqual(controls, result['controls'])

        self.assertIn('.js', gizmo_map_view.MapView.get_vendor_js()[0])
        self.assertIn('.js', gizmo_map_view.MapView.get_gizmo_js()[0])
        self.assertIn('.css', gizmo_map_view.MapView.get_vendor_css()[0])
        self.assertIn('.css', gizmo_map_view.MapView.get_gizmo_css()[0])

    @mock.patch('tethys_gizmos.gizmo_options.map_view.settings')
    def test_MapView_debug(self, mock_settings):
        ms = mock_settings()
        ms.return_value = MockObject()
        gizmo_map_view.MapView.ol_version = '4.6.5'
        self.assertIn('-debug.js', gizmo_map_view.MapView.get_vendor_js()[0])

    def test_MVView(self):
        projection = 'EPSG:4326'
        center = [-100, 40]
        zoom = 10
        maxZoom = 20
        minZoom = 2

        result = gizmo_map_view.MVView(projection=projection, center=center, zoom=zoom,
                                       maxZoom=maxZoom, minZoom=minZoom)

        # Check result
        self.assertIn(projection, result['projection'])
        self.assertEqual(center, result['center'])
        self.assertEqual(zoom, result['zoom'])
        self.assertEqual(maxZoom, result['maxZoom'])
        self.assertEqual(minZoom, result['minZoom'])

    def test_MVDraw(self):
        controls = ['Modify', 'Delete', 'Move', 'Point', 'LineString', 'Polygon', 'Box']
        initial = 'Point'
        output_format = 'GeoJSON'
        fill_color = 'rgba(255,255,255,0.2)'
        line_color = '#663399'
        point_color = '#663399'

        result = gizmo_map_view.MVDraw(controls=controls, initial=initial, output_format=output_format,
                                       line_color=line_color, fill_color=fill_color, point_color=point_color)

        # Check result
        self.assertEqual(controls, result['controls'])
        self.assertEqual(initial, result['initial'])
        self.assertEqual(output_format, result['output_format'])
        self.assertEqual(fill_color, result['fill_color'])
        self.assertEqual(line_color, result['line_color'])
        self.assertEqual(point_color, result['point_color'])

    def test_MVDraw_add_snapping_layer_special_cases(self):
        special_options = ['data', 'legend_title', 'legend_extent', 'legend_extent_projection',
                           'legend_classes', 'editable']

        for option in special_options:
            snapping_layer = {'{}.foo'.format(option): 'bar'}
            result = gizmo_map_view.MVDraw(snapping_layer=snapping_layer)

            # Check result
            self.assertDictEqual({'tethys_{}.foo'.format(option): 'bar'}, result.snapping_layer)

    def test_MVDraw_add_snapping_layer(self):
        snapping_layer = {'not_data.foo': 'bar'}
        result = gizmo_map_view.MVDraw(snapping_layer=snapping_layer)

        # Check result
        self.assertDictEqual({'not_data.foo': 'bar'}, result.snapping_layer)

    def test_MVDraw_invalid_initial_control(self):

        # Raise Error if Initial is not in Controls list
        self.assertRaises(ValueError, gizmo_map_view.MVDraw, initial='foo')

    def test_MVDraw_invalid_snapping_layer(self):
        test_snapping_layer = {'foo': 1, 'bar': 1}
        # Raise Error if Initial is not in Controls list
        self.assertRaises(ValueError, gizmo_map_view.MVDraw, snapping_layer=test_snapping_layer)

    def test_MVLayer(self):
        source = 'KML'
        legend_title = 'Park City Watershed'
        options = {'url': '/static/tethys_gizmos/data/model.kml'}
        times = ["20210322T112511Z", "20210322T122511Z", "20210322T132511Z"]

        result = gizmo_map_view.MVLayer(source=source, legend_title=legend_title, options=options, times=times)

        # Check Result
        self.assertEqual(source, result['source'])
        self.assertEqual(legend_title, result['legend_title'])
        self.assertEqual(options, result['options'])
        self.assertEqual(times, result['times'])

    @mock.patch('tethys_gizmos.gizmo_options.map_view.log.warning')
    def test_MVLayer_warning(self, mock_log):
        source = 'KML'
        legend_title = 'Park City Watershed'
        options = {'url': '/static/tethys_gizmos/data/model.kml'}
        feature_selection = True

        gizmo_map_view.MVLayer(source=source, legend_title=legend_title, options=options,
                               feature_selection=feature_selection)

        mock_log.assert_called_with("geometry_attribute not defined -using default value 'the_geom'")

    def test_MVLegendClass(self):
        # Point
        type_value = 'point'
        value = 'Point Legend'
        fill = '#00ff00'

        result = gizmo_map_view.MVLegendClass(type=type_value, value=value, fill=fill)

        # Check Result
        self.assertEqual(value, result['value'])
        self.assertEqual(fill, result['fill'])
        self.assertEqual(value, result['value'])

        # Point with No Fill
        self.assertRaises(ValueError, gizmo_map_view.MVLegendClass, type=type_value, value=value)

        # Not Valid Type
        self.assertRaises(ValueError, gizmo_map_view.MVLegendClass, type='points', value=value)

        # Line
        type_value = 'line'
        value = 'Line Legend'
        stroke = '#00ff01'
        result = gizmo_map_view.MVLegendClass(type=type_value, value=value, stroke=stroke)

        # Check Result
        self.assertEqual(type_value, result['type'])
        self.assertEqual(stroke, result['stroke'])
        self.assertEqual(value, result['value'])

        # Line with No Stroke
        self.assertRaises(ValueError, gizmo_map_view.MVLegendClass, type=type_value, value=value)

        # Polygon
        type_value = 'polygon'
        value = 'Polygon Legend'
        fill = '#00ff00'
        stroke = '#00ff01'

        result = gizmo_map_view.MVLegendClass(type=type_value, value=value, stroke=stroke, fill=fill)

        # Check Result
        self.assertEqual(type_value, result['type'])
        self.assertEqual(stroke, result['stroke'])
        self.assertEqual(fill, result['fill'])
        self.assertEqual(value, result['value'])

        # Polygon with no Stroke
        result = gizmo_map_view.MVLegendClass(type=type_value, value=value, fill=fill)

        # Check Result
        self.assertEqual(type_value, result['type'])
        self.assertEqual(fill, result['fill'])
        self.assertEqual(fill, result['line'])

        # Polygon with no fill
        self.assertRaises(ValueError, gizmo_map_view.MVLegendClass, type=type_value, value=value)

        # Raster
        type_value = 'raster'
        value = 'Raster Legend'
        ramp = ['#00ff00', '#00ff01', '#00ff02']

        result = gizmo_map_view.MVLegendClass(type=type_value, value=value, ramp=ramp)

        # Check Result
        self.assertEqual(type_value, result['type'])
        self.assertEqual(ramp, result['ramp'])

        # Raster without ramp
        self.assertRaises(ValueError, gizmo_map_view.MVLegendClass, type=type_value, value=value)

    def test_MVLegendImageClass(self):
        value = 'image legend'
        image_url = 'www.aquaveo.com/image.png'

        result = gizmo_map_view.MVLegendImageClass(value=value, image_url=image_url)

        # Check Result
        self.assertEqual(value, result['value'])
        self.assertEqual(image_url, result['image_url'])

    def test_MVLegendGeoServerImageClass(self):
        value = 'Cities'
        geoserver_url = 'http://localhost:8181/geoserver'
        style = 'green'
        layer = 'rivers'
        width = 20
        height = 10

        image_url = "{0}/wms?REQUEST=GetLegendGraphic&VERSION=1.0.0&" \
                    "STYLE={1}&FORMAT=image/png&WIDTH={2}&HEIGHT={3}&" \
                    "LEGEND_OPTIONS=forceRule:true&" \
                    "LAYER={4}".format(geoserver_url, style, width, height, layer)

        result = gizmo_map_view.MVLegendGeoServerImageClass(value=value, geoserver_url=geoserver_url,
                                                            style=style, layer=layer, width=width, height=height)

        # Check Result
        self.assertEqual(value, result['value'])
        self.assertEqual(image_url, result['image_url'])
