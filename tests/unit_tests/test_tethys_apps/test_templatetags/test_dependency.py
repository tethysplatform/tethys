import unittest
from unittest import mock
from django.test import override_settings
from tethys_apps.templatetags import dependency as d


class TestLocalPath(unittest.TestCase):
    def test_jsdelivr_unscoped(self):
        result = d._local_path(
            "https://cdn.jsdelivr.net/npm/papaparse@5.4.1/papaparse.min.js", "my_app"
        )
        self.assertEqual(result, "my_app/node_modules/papaparse/papaparse.min.js")

    def test_unpkg_unscoped(self):
        result = d._local_path(
            "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js", "my_app"
        )
        self.assertEqual(result, "my_app/node_modules/leaflet/dist/leaflet.js")

    def test_scoped_package(self):
        result = d._local_path(
            "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.6.0/css/all.min.css",
            "my_app",
        )
        self.assertEqual(
            result,
            "my_app/node_modules/@fortawesome/fontawesome-free/css/all.min.css",
        )

    def test_missing_version_raises(self):
        # No "@version" segment, so name/tail cannot be unpacked
        with self.assertRaises(ValueError):
            d._local_path(
                "https://cdn.jsdelivr.net/npm/papaparse/papaparse.min.js", "my_app"
            )

    def test_missing_path_raises(self):
        # Has a version but no "/path" after it, so version/path cannot be unpacked
        with self.assertRaises(ValueError):
            d._local_path("https://cdn.jsdelivr.net/npm/papaparse@5.4.1", "my_app")


@mock.patch(
    "tethys_apps.templatetags.dependency.static",
    side_effect=lambda p: "/static/" + p,
)
class TestResolve(unittest.TestCase):
    JSDELIVR = "https://cdn.jsdelivr.net/npm/papaparse@5.4.1/papaparse.min.js"
    MALFORMED = "https://cdn.jsdelivr.net/npm/papaparse/papaparse.min.js"
    CDNJS = "https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.4.1/papaparse.min.js"
    LOCAL = "my_app/js/papaparse.min.js"
    CONTEXT = {"tethys_app": {"package": "my_app"}}

    @override_settings(STATICFILES_USE_NPM=False)
    def test_online_returns_cdn(self, mock_static):
        result = d._resolve(self.CONTEXT, self.JSDELIVR)
        self.assertEqual(result, self.JSDELIVR)
        mock_static.assert_not_called()

    @override_settings(STATICFILES_USE_NPM=True)
    def test_offline_npm_derived(self, mock_static):
        result = d._resolve(self.CONTEXT, self.JSDELIVR)
        self.assertEqual(
            result, "/static/my_app/node_modules/papaparse/papaparse.min.js"
        )

    @override_settings(STATICFILES_USE_NPM=True)
    def test_offline_malformed_npm_falls_back_to_local_path(self, mock_static):
        result = d._resolve(self.CONTEXT, self.MALFORMED, local_path=self.LOCAL)
        self.assertEqual(result, "/static/" + self.LOCAL)

    @override_settings(STATICFILES_USE_NPM=True)
    def test_offline_malformed_npm_no_local_path_returns_cdn(self, mock_static):
        result = d._resolve(self.CONTEXT, self.MALFORMED)
        self.assertEqual(result, self.MALFORMED)

    @override_settings(STATICFILES_USE_NPM=True)
    def test_offline_non_npm_cdn_uses_local_path(self, mock_static):
        result = d._resolve(self.CONTEXT, self.CDNJS, local_path=self.LOCAL)
        self.assertEqual(result, "/static/" + self.LOCAL)

    @override_settings(STATICFILES_USE_NPM=True)
    def test_offline_non_npm_cdn_no_local_path_returns_cdn(self, mock_static):
        result = d._resolve(self.CONTEXT, self.CDNJS)
        self.assertEqual(result, self.CDNJS)
        mock_static.assert_not_called()

    @override_settings(STATICFILES_USE_NPM=True)
    def test_offline_no_app_in_context_uses_local_path(self, mock_static):
        # tethys_app missing from context exercises the "or {}" fallback
        result = d._resolve({}, self.JSDELIVR, local_path=self.LOCAL)
        self.assertEqual(result, "/static/" + self.LOCAL)


@mock.patch(
    "tethys_apps.templatetags.dependency.static",
    side_effect=lambda p: "/static/" + p,
)
class TestDependencyTags(unittest.TestCase):
    JS = "https://cdn.jsdelivr.net/npm/papaparse@5.4.1/papaparse.min.js"
    CSS = "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css"
    CONTEXT = {"tethys_app": {"package": "my_app"}}

    @override_settings(STATICFILES_USE_NPM=False)
    def test_dependency_script_online(self, mock_static):
        result = d.dependency_script(self.CONTEXT, self.JS)
        self.assertEqual(result, f'<script src="{self.JS}"></script>')

    @override_settings(STATICFILES_USE_NPM=True)
    def test_dependency_script_offline(self, mock_static):
        result = d.dependency_script(self.CONTEXT, self.JS)
        self.assertEqual(
            result,
            '<script src="/static/my_app/node_modules/papaparse/papaparse.min.js">'
            "</script>",
        )

    @override_settings(STATICFILES_USE_NPM=False)
    def test_dependency_link_online(self, mock_static):
        result = d.dependency_link(self.CONTEXT, self.CSS)
        self.assertEqual(result, f'<link rel="stylesheet" href="{self.CSS}">')

    @override_settings(STATICFILES_USE_NPM=True)
    def test_dependency_link_offline(self, mock_static):
        result = d.dependency_link(self.CONTEXT, self.CSS)
        self.assertEqual(
            result,
            '<link rel="stylesheet" '
            'href="/static/my_app/node_modules/leaflet/dist/leaflet.css">',
        )
