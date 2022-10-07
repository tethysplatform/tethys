import unittest
from tethys_gizmos.gizmo_options.slide_sheet import SlideSheet


class TestSlideSheet(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_SlideSheet(self):
        result = SlideSheet(
            id="some-slide-sheet",
            template="path/to/a/template.html",
            title="Some Slide Sheet",
        )

        # Check Result
        self.assertEqual("some-slide-sheet", result["id"])
        self.assertEqual("path/to/a/template.html", result["template"])
        self.assertEqual("Some Slide Sheet", result["title"])

    def test_get_gizmo_js(self):
        ret = SlideSheet.get_gizmo_js()
        self.assertEqual(("tethys_gizmos/js/slide_sheet.js",), ret)

    def test_get_gizmo_css(self):
        ret = SlideSheet.get_gizmo_css()
        self.assertEqual(("tethys_gizmos/css/slide_sheet.css",), ret)
