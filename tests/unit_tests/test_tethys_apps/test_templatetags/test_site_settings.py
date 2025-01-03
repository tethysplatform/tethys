import unittest
from unittest import mock
from tethys_apps.templatetags import site_settings as ss


class TestSiteSettings(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch("tethys_apps.templatetags.site_settings.settings")
    @mock.patch("tethys_apps.templatetags.site_settings.Path.is_file")
    def test_get_css_in_static_root(self, mock_isfile, mock_settings):
        mock_isfile.return_value = True
        mock_settings.STATIC_ROOT = "test_base_path"

        ret = ss.load_custom_css("/test.css")  # test slash stripping
        self.assertEqual(
            ret,
            '<link href="/static/test.css" rel="stylesheet" />',
        )

    @mock.patch("tethys_apps.templatetags.site_settings.settings")
    @mock.patch("tethys_apps.templatetags.site_settings.Path.is_file")
    def test_get_css_in_staticfiles_dirs(self, mock_isfile, mock_settings):
        mock_isfile.side_effect = [False, True]
        mock_settings.STATIC_ROOT = "test_base_path1"
        mock_settings.STATICFILES_DIRS = ["test_base_path2"]

        ret = ss.load_custom_css("test.css")
        self.assertEqual(
            ret,
            '<link href="/static/test.css" rel="stylesheet" />',
        )

    @mock.patch("tethys_apps.templatetags.site_settings.settings")
    @mock.patch("tethys_apps.templatetags.site_settings.Path.is_file")
    def test_get_css_is_code(self, mock_isfile, mock_settings):
        mock_isfile.return_value = False
        mock_settings.STATIC_ROOT = "test_base_path1"
        mock_settings.STATICFILES_DIRS = ["test_base_path2"]

        ret = ss.load_custom_css(".navbar-brand { background-color: darkred; }")
        self.assertEqual(
            ret, "<style>.navbar-brand { background-color: darkred; }</style>"
        )

    def test_long_css_text(self):
        long_css_text = """
            .site-header { margin: 0 50px 0 0; background-color: red; }
            .site-header .navbar-brand {
                background-color: darkred;
                color: black;
                font-style: italic;
                font-variant: small-caps;
                font-family: cursive;
                font-size: 24px;
            }
        """

        ret = ss.load_custom_css(long_css_text)
        self.assertEqual(ret, f"<style>{long_css_text}</style>")
