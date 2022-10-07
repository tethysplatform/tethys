import re
import unittest
from tethys_apps.templatetags import app_theme


class TestAppTheme(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def is_valid_hex_color(self, hex_color):
        self.assertTrue(re.search(app_theme.hex_regex_pattern, hex_color) is not None)

    def test_lighten_black_0(self):
        ret = app_theme.lighten("#000000", 0)
        self.is_valid_hex_color(ret)
        self.assertEqual("#000000", ret)

    def test_lighten_black_50(self):
        ret = app_theme.lighten("#000000", 50)
        self.is_valid_hex_color(ret)
        self.assertEqual("#7f7f7f", ret)

    def test_lighten_black_100(self):
        ret = app_theme.lighten("#000000", 100)
        self.is_valid_hex_color(ret)
        self.assertEqual("#ffffff", ret)

    def test_lighten_black_neg_50(self):
        ret = app_theme.lighten("#000000", -50)
        self.is_valid_hex_color(ret)
        self.assertEqual("#000000", ret)

    def test_lighten_red_0(self):
        ret = app_theme.lighten("#880000", 0)
        self.is_valid_hex_color(ret)
        self.assertEqual("#880000", ret)

    def test_lighten_red_50(self):
        ret = app_theme.lighten("#880000", 50)
        self.is_valid_hex_color(ret)
        self.assertEqual("#ff7f7f", ret)

    def test_lighten_red_100(self):
        ret = app_theme.lighten("#880000", 100)
        self.is_valid_hex_color(ret)
        self.assertEqual("#ffffff", ret)

    def test_lighten_red_neg_50(self):
        ret = app_theme.lighten("#880000", -50)
        self.is_valid_hex_color(ret)
        self.assertEqual("#080000", ret)

    def test_lighten_green_0(self):
        ret = app_theme.lighten("#008800", 0)
        self.is_valid_hex_color(ret)
        self.assertEqual("#008800", ret)

    def test_lighten_green_50(self):
        ret = app_theme.lighten("#008800", 50)
        self.is_valid_hex_color(ret)
        self.assertEqual("#7fff7f", ret)

    def test_lighten_green_100(self):
        ret = app_theme.lighten("#008800", 100)
        self.is_valid_hex_color(ret)
        self.assertEqual("#ffffff", ret)

    def test_lighten_green_neg_50(self):
        ret = app_theme.lighten("#008800", -50)
        self.is_valid_hex_color(ret)
        self.assertEqual("#000800", ret)

    def test_lighten_blue_0(self):
        ret = app_theme.lighten("#000088", 0)
        self.is_valid_hex_color(ret)
        self.assertEqual("#000088", ret)

    def test_lighten_blue_50(self):
        ret = app_theme.lighten("#000088", 50)
        self.is_valid_hex_color(ret)
        self.assertEqual("#7f7fff", ret)

    def test_lighten_blue_100(self):
        ret = app_theme.lighten("#000088", 100)
        self.is_valid_hex_color(ret)
        self.assertEqual("#ffffff", ret)

    def test_lighten_blue_neg_50(self):
        ret = app_theme.lighten("#000088", -50)
        self.is_valid_hex_color(ret)
        self.assertEqual("#000008", ret)

    def test_lighten_white_0(self):
        ret = app_theme.lighten("#ffffff", 0)
        self.is_valid_hex_color(ret)
        self.assertEqual("#ffffff", ret)

    def test_lighten_white_50(self):
        ret = app_theme.lighten("#ffffff", 50)
        self.is_valid_hex_color(ret)
        self.assertEqual("#ffffff", ret)

    def test_lighten_white_100(self):
        ret = app_theme.lighten("#ffffff", 100)
        self.is_valid_hex_color(ret)
        self.assertEqual("#ffffff", ret)

    def test_lighten_white_neg_50(self):
        ret = app_theme.lighten("#ffffff", -50)
        self.is_valid_hex_color(ret)
        self.assertEqual("#7f7f7f", ret)

    def test_lighten_white_neg_100(self):
        ret = app_theme.lighten("#ffffff", -100)
        self.is_valid_hex_color(ret)
        self.assertEqual("#000000", ret)

    def test_lighten_non_hex_string(self):
        with self.assertRaises(ValueError) as cm:
            app_theme.lighten("dog", 50)

        self.assertEqual(
            'Given "dog", but needs to be in ' 'hex color format (e.g.: "#2d3436").',
            str(cm.exception),
        )

    def test_lighten_invalid_hex_string(self):
        with self.assertRaises(ValueError) as cm:
            app_theme.lighten("#1g3h5i", 50)

        self.assertEqual(
            'Given "#1g3h5i", but needs to be in '
            'hex color format (e.g.: "#2d3436").',
            str(cm.exception),
        )
