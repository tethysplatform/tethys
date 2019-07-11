import unittest
import tethys_gizmos.gizmo_options.esri_map as gizmo_esri_map


class TestESRI(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_ESRIMap(self):
        layers = ['layer1', 'layer2']
        basemap = 'Aerial'
        result = gizmo_esri_map.ESRIMap(basemap=basemap, layers=layers)
        # Check Result
        self.assertIn(basemap, result['basemap'])
        self.assertEqual(layers, result['layers'])

        result = gizmo_esri_map.ESRIMap.get_vendor_js()
        # Check Result
        self.assertIn('js', result[0])
        self.assertNotIn('css', result[0])

        result = gizmo_esri_map.ESRIMap.get_gizmo_js()
        # Check Result
        self.assertIn('.js', result[0])
        self.assertNotIn('.css', result[0])

        result = gizmo_esri_map.ESRIMap.get_vendor_css()
        # Check Result
        self.assertIn('.css', result[0])
        self.assertNotIn('.js', result[0])

    def test_EMView(self):
        center = ['40.276039', '-111.651120']
        zoom = 4

        result = gizmo_esri_map.EMView(center=center, zoom=zoom)
        # Check Result
        self.assertEqual(zoom, result['zoom'])
        self.assertEqual(center, result['center'])

    def test_EMLayer(self):
        type = 'ImageryLayer'
        url = 'www.aquaveo.com'

        result = gizmo_esri_map.EMLayer(type=type, url=url)
        # Check Result
        self.assertEqual(type, result['type'])
        self.assertEqual(url, result['url'])
