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
    def test_load_custom_css_empty_str(self, mock_isfile, mock_settings):
        mock_isfile.return_value = True
        mock_settings.STATIC_ROOT = "test_base_path"

        ret = ss.load_custom_css("")  # test empty str value
        self.assertEqual(ret, "")

    @mock.patch("tethys_apps.templatetags.site_settings.settings")
    @mock.patch("tethys_apps.templatetags.site_settings.Path.is_file")
    def test_load_custom_css_in_static_root(self, mock_isfile, mock_settings):
        mock_isfile.return_value = True
        mock_settings.STATIC_ROOT = "test_base_path"

        ret = ss.load_custom_css("/test.css")  # test slash stripping
        self.assertEqual(
            ret,
            '<link href="/static/test.css" rel="stylesheet" />',
        )

    @mock.patch("tethys_apps.templatetags.site_settings.settings")
    @mock.patch("tethys_apps.templatetags.site_settings.Path.is_file")
    def test_load_custom_css_in_staticfiles_dirs(self, mock_isfile, mock_settings):
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
    def test_load_custom_css_is_code(self, mock_isfile, mock_settings):
        mock_isfile.return_value = False
        mock_settings.STATIC_ROOT = "test_base_path1"
        mock_settings.STATICFILES_DIRS = ["test_base_path2"]

        ret = ss.load_custom_css(".navbar-brand { background-color: darkred; }")
        self.assertEqual(
            ret, "<style>.navbar-brand { background-color: darkred; }</style>"
        )

    def test_load_custom_css_long_css_text(self):
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

    @mock.patch("tethys_apps.templatetags.site_settings.log")
    @mock.patch("tethys_apps.templatetags.site_settings.settings")
    @mock.patch("tethys_apps.templatetags.site_settings.Path.is_file")
    def test_load_custom_css_long_path(self, mock_isfile, mock_settings, mock_log):
        mock_settings.STATIC_ROOT = "test_base_path1"
        mock_settings.STATICFILES_DIRS = ["test_base_path2"]
        long_path = "im/a/very/long/path/to/a/file/that/does/not/exist.css"
        mock_isfile.side_effect = OSError("TEST OUTPUT: File path too long")

        ret = ss.load_custom_css(long_path)
        self.assertEqual(ret, "")
        mock_log.warning.assert_called_with(
            f"Could not load file '{long_path}' for custom styles: TEST OUTPUT: File path too long"
        )
