import unittest
from unittest import mock
from django.test import override_settings
from tethys_portal import dependencies


class TestStaticDependency(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch("tethys_portal.dependencies.StaticDependency._get_tag")
    def test_link_tag(self, mock_get_tag):
        dependency = dependencies.StaticDependency("name", "version")
        dependency.link_tag
        mock_get_tag.assert_called_with("css")

    @mock.patch("tethys_portal.dependencies.StaticDependency._get_tag")
    def test_script_tag(self, mock_get_tag):
        dependency = dependencies.StaticDependency("name", "version")
        dependency.script_tag
        mock_get_tag.assert_called_with("js")

    @override_settings(STATICFILES_USE_NPM=True)
    @override_settings(STATIC_URL="/static")
    def test_get_tag_css(self):
        dependency = dependencies.StaticDependency(
            "name", "version", css_path="css_path"
        )
        result = dependency._get_tag("css")
        self.assertEqual(
            result, '<link rel="stylesheet" href="/static/name/css_path"  />'
        )

    @override_settings(STATICFILES_USE_NPM=True)
    @override_settings(STATIC_URL="/test/static")
    def test_get_tag_css_static_url_setting(self):
        dependency = dependencies.StaticDependency(
            "name", "version", css_path="css_path"
        )
        result = dependency._get_tag("css")
        self.assertEqual(
            result, '<link rel="stylesheet" href="/test/static/name/css_path"  />'
        )

    @override_settings(STATICFILES_USE_NPM=True)
    @override_settings(STATIC_URL="/static")
    def test_get_tag_js(self):
        dependency = dependencies.StaticDependency(
            "name", "version", js_path="js_path", cdn_url="{npm_name}@{version}/{path}"
        )
        result = dependency._get_tag("js")
        self.assertEqual(result, '<script src="/static/name/js_path" ></script>')

    @override_settings(STATICFILES_USE_NPM=True)
    @override_settings(STATIC_URL="/test/static")
    def test_get_tag_js_static_url_setting(self):
        dependency = dependencies.StaticDependency(
            "name", "version", js_path="js_path", cdn_url="{npm_name}@{version}/{path}"
        )
        result = dependency._get_tag("js")
        self.assertEqual(result, '<script src="/test/static/name/js_path" ></script>')

    @override_settings(STATICFILES_USE_NPM=False)
    def test_get_tag_integrity(self):
        dependency = dependencies.StaticDependency(
            "name",
            "version",
            js_path="js_path",
            js_integrity="js_integrity",
            cdn_url="{npm_name}@{version}/{path}",
        )
        result = dependency._get_tag("js")
        self.assertEqual(
            result,
            '<script src="name@version/js_path" integrity="js_integrity" crossorigin="anonymous"></script>',
        )

    def test_default_debug_path_converter(self):
        result = dependencies.StaticDependency.default_debug_path_converter(
            "test/dependency/path.min.js"
        )
        self.assertEqual(result, "test/dependency/path.js")

    @override_settings(STATICFILES_USE_NPM=True)
    @mock.patch("tethys_portal.dependencies.StaticDependency._get_url")
    @mock.patch("tethys_portal.dependencies.logger.warning")
    def test_custom_version_warning(self, mock_warning, mock_url):
        dependency = dependencies.StaticDependency("name", "version", js_path="js_path")
        dependency.get_custom_version_url(url_type="js", version="different_version")
        mock_warning.assert_called_once()
        mock_url.assert_called_with("js", "different_version", debug=None, use_cdn=True)

    @override_settings(STATICFILES_USE_NPM=True)
    def test_get_js_urls(self):
        dependency = dependencies.StaticDependency("name", "version", js_path="js_path")
        result = dependency.get_js_urls()
        self.assertListEqual(result, ["/name/js_path"])

    def test_get_url_None_path(self):
        dependency = dependencies.StaticDependency("name", "version")
        self.assertRaises(ValueError, dependency._get_url, "js")

    @override_settings(STATICFILES_USE_NPM=True)
    @override_settings(DEBUG=True)
    def test_get_url_debug(self):
        dependency = dependencies.StaticDependency(
            "name", "version", js_path="js_path.min.js"
        )
        result = dependency._get_url("js")
        self.assertEqual(result, "/name/js_path.js")

    @override_settings(STATICFILES_USE_NPM=True)
    def test_arcgis_error(self):
        dependency = dependencies.ArcGISStaticDependency("name", "version", js_path="")
        self.assertRaises(ValueError, dependency._get_url, "js")
