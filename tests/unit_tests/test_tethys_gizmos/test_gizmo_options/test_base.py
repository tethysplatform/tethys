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
        test_dict = 'key1="value with spaces" key2="value_with_no_spaces"'
        test_class = "Map Type"

        result = basetest.TethysGizmoOptions(test_dict, test_class)

        self.assertIsInstance(result["attributes"], dict)
        self.assertEqual("value with spaces", result["attributes"]["key1"])
        self.assertEqual("value_with_no_spaces", result["attributes"]["key2"])
        self.assertEqual("Map Type", result["classes"])

    def test_get_tethys_gizmos_js(self):
        result = basetest.TethysGizmoOptions.get_tethys_gizmos_js()
        self.assertIn("tethys_gizmos.js", result[0])
        self.assertNotIn(".css", result[0])

    def test_get_tethys_gizmos_css(self):
        result = basetest.TethysGizmoOptions.get_tethys_gizmos_css()
        self.assertIn("tethys_gizmos.css", result[0])
        self.assertNotIn(".js", result[0])

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

    def test_get_gizmo_modals(self):
        result = basetest.TethysGizmoOptions.get_gizmo_modals()
        self.assertFalse(result)

    def test_SecondaryGizmoOptions(self):
        result = basetest.SecondaryGizmoOptions()
        self.assertFalse(result)
