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

        self.assertIn(basemap, result['basemap'])
        self.assertEqual(layers, result['layers'])

        result = gizmo_esri_map.ESRIMap.get_vendor_js()
        self.assertIn('js', result[0])

        result = gizmo_esri_map.ESRIMap.get_gizmo_js()
        self.assertIn('js', result[0])

        result = gizmo_esri_map.ESRIMap.get_vendor_css()
        self.assertIn('css', result[0])

    def test_EMView(self):
        center = ['40.276039', '-111.651120']
        zoom = 4

        result = gizmo_esri_map.EMView(center=center, zoom=zoom)

        self.assertEqual(zoom, result['zoom'])
        self.assertEqual(center, result['center'])

    def test_EMLayer(self):
        type = 'ImageryLayer'
        url = 'www.aquaveo.com'

        result = gizmo_esri_map.EMLayer(type=type, url=url)

        self.assertEqual(type, result['type'])
        self.assertEqual(url, result['url'])
