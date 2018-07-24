"""
********************************************************************************
* Name: base.py
* Author: nswain
* Created On: July 23, 2018
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""
import unittest
import tethys_gizmos.gizmo_options.base as basetest


class TestTethysGizmosBase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_TethysGizmoOptions(self):
        test_dict = ' key="value with spaces"'
        test_class = 'Map Type'

        result = basetest.TethysGizmoOptions(test_dict, test_class)

        self.assertIsInstance(result['attributes'], dict)
        self.assertIn('key', result['attributes'])
        self.assertEqual('value with spaces', result['attributes']['key'])
        self.assertEqual('Map Type', result['classes'])

    def test_get_tethys_gizmos_js(self):
        result = basetest.TethysGizmoOptions.get_tethys_gizmos_js()
        self.assertIn('tethys_gizmos/js/tethys_gizmos.js', result)

    def test_get_tethys_gizmos_css(self):
        result = basetest.TethysGizmoOptions.get_tethys_gizmos_css()
        self.assertIn('tethys_gizmos/css/tethys_gizmos.css', result)

    def test_get_vendor_js(self):
        result = basetest.TethysGizmoOptions.get_vendor_js()
        self.assertFalse(result)

    def test_get_gizmo_js(self):
        result = basetest.TethysGizmoOptions.get_gizmo_js()
        self.assertFalse(result)

    def test_get_vendor_css(self):
        result = basetest.TethysGizmoOptions.get_vendor_css()
        self.assertFalse(result)

    def test_get_gizmo_css(self):
        result = basetest.TethysGizmoOptions.get_gizmo_css()
        self.assertFalse(result)

    def test_SecondaryGizmoOptions(self):
        result = basetest.SecondaryGizmoOptions()
        self.assertFalse(result)
