import unittest
from django.test import override_settings
import tethys_gizmos.gizmo_options.cesium_map_view as gizmo_map_view


class TestCesiumMapView(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @override_settings(STATICFILES_USE_NPM=False)
    def test_CesiumMapView(self):
        options = {"options": "options_value"}
        view = {"view": "view_value"}
        layers = ["layer1"]
        primitives = ["primitive1"]
        entities = ["entities1", "entities2"]
        terrain = {"terrain": "terrain_value"}
        models = ["model1", "model2"]
        height = "80%"
        width = "80%"

        gizmo_map_view.CesiumMapView.cesium_version = "1.51"
        result = gizmo_map_view.CesiumMapView(
            height=height,
            width=width,
            options=options,
            view=view,
            layers=layers,
            entities=entities,
            terrain=terrain,
            models=models,
            primitives=primitives,
        )

        # Check Result
        self.assertEqual(height, result["height"])
        self.assertEqual(width, result["width"])
        self.assertEqual(options, result["options"])
        self.assertEqual(view, result["view"])
        self.assertEqual(layers, result["layers"])
        self.assertEqual(entities, result["entities"])
        self.assertEqual(terrain, result["terrain"])
        self.assertEqual(models, result["models"])
        self.assertEqual(primitives, result["primitives"])
        self.assertFalse(result["draw"])

        # Check sources
        self.assertIn(
            "https://cdn.jsdelivr.net/npm/cesium@1.51/Build/Cesium/Cesium.js",
            gizmo_map_view.CesiumMapView.get_vendor_js()[0],
        )
        self.assertIn(
            "https://cdn.jsdelivr.net/npm/cesium@1.51/Build/Cesium/Widgets/widgets.css",
            gizmo_map_view.CesiumMapView.get_vendor_css()[0],
        )
        self.assertIn(".js", gizmo_map_view.CesiumMapView.get_gizmo_js()[0])
        self.assertIn(".css", gizmo_map_view.CesiumMapView.get_vendor_css()[0])
        self.assertIn(".css", gizmo_map_view.CesiumMapView.get_gizmo_css()[0])

    @override_settings(STATICFILES_USE_NPM=True)
    def test_CesiumMapView_build_version(self):
        options = {"options": "options_value"}
        view = {"view": "view_value"}
        layers = ["layer1"]
        primitives = ["primitive1"]
        entities = ["entities1", "entities2"]
        terrain = {"terrain": "terrain_value"}
        models = ["model1", "model2"]

        gizmo_map_view.CesiumMapView.cesium_version = "1.88"
        result = gizmo_map_view.CesiumMapView(
            options=options,
            view=view,
            layers=layers,
            entities=entities,
            terrain=terrain,
            models=models,
            draw=True,
            primitives=primitives,
        )

        # Check Result
        self.assertEqual("100%", result["height"])
        self.assertEqual("100%", result["width"])
        self.assertEqual(options, result["options"])
        self.assertEqual(view, result["view"])
        self.assertEqual(layers, result["layers"])
        self.assertEqual(entities, result["entities"])
        self.assertEqual(terrain, result["terrain"])
        self.assertEqual(models, result["models"])
        self.assertTrue(result["draw"])
        self.assertEqual(primitives, result["primitives"])

        # Check sources
        self.assertIn(
            "/cesium/Build/Cesium/Cesium.js",
            gizmo_map_view.CesiumMapView.get_vendor_js()[0],
        )
        self.assertIn(
            "/cesium/Build/Cesium/Widgets/widgets.css",
            gizmo_map_view.CesiumMapView.get_vendor_css()[0],
        )
        self.assertIn(".js", gizmo_map_view.CesiumMapView.get_gizmo_js()[0])
        self.assertIn(".css", gizmo_map_view.CesiumMapView.get_vendor_css()[0])
        self.assertIn(".css", gizmo_map_view.CesiumMapView.get_gizmo_css()[0])

    def test_CMVEntity(self):
        ent = gizmo_map_view.CMVEntity(
            source="my_source",
            document="my_document",
            legend_title="Legend Title",
        )
        self.assertEqual(ent.source, "my_source")
