import unittest
import tethys_gizmos.gizmo_options.google_map_view as gizmo_google_map_view


class TestGoogleMapView(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_GoogleMapView(self):
        height = '600px'
        width = '80%'
        maps_api_key = 'api-key'
        reference_kml_action = 'gizmos:get_kml'
        drawing_types_enabled = ['POLYGONS', 'POINTS', 'POLYLINES']
        initial_drawing_mode = 'POINTS'
        output_format = 'WKT'
        result = gizmo_google_map_view.GoogleMapView(height=height, width=width, maps_api_key=maps_api_key,
                                                     reference_kml_action=reference_kml_action,
                                                     output_format=output_format,
                                                     drawing_types_enabled=drawing_types_enabled,
                                                     initial_drawing_mode=initial_drawing_mode)
        # Check Result
        self.assertIn(height, result['height'])
        self.assertIn(width, result['width'])
        self.assertIn(maps_api_key, result['maps_api_key'])
        self.assertIn(reference_kml_action, result['reference_kml_action'])
        self.assertEqual(drawing_types_enabled, result['drawing_types_enabled'])
        self.assertIn(initial_drawing_mode, result['initial_drawing_mode'])
        self.assertIn(output_format, result['output_format'])

        result = gizmo_google_map_view.GoogleMapView.get_vendor_js()
        # Check Result
        self.assertIn('.js', result[0])
        self.assertNotIn('.css', result[0])

        result = gizmo_google_map_view.GoogleMapView.get_vendor_css()
        # Check Result
        self.assertIn('.css', result[0])
        self.assertNotIn('.js', result[0])

        result = gizmo_google_map_view.GoogleMapView.get_gizmo_js()
        # Check Result
        self.assertIn('.js', result[0])
        self.assertNotIn('.css', result[0])
