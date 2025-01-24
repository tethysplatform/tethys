import logging

from django.conf import settings
from django.templatetags.static import static

logger = logging.getLogger("tethys." + __name__)


class StaticDependency:
    cdn_url = None
    static_url = "/{npm_name}/{path}"

    def __init__(
        self,
        npm_name,
        version,
        css_path=None,
        js_path=None,
        css_integrity=None,
        js_integrity=None,
        js_paths=None,
        debug_path_converter=None,
        cdn_url=None,
    ):
        self.npm_name = npm_name
        self.version = version
        self.css_path = css_path
        self.js_path = js_path
        self.js_paths = js_paths
        self.css_integrity = css_integrity
        self.js_integrity = js_integrity
        self.debug_path_converter = (
            debug_path_converter or self.default_debug_path_converter
        )
        self.cdn_url = cdn_url or self.cdn_url

    @property
    def use_cdn(self):
        return not settings.STATICFILES_USE_NPM

    @property
    def css_url(self):
        return self._get_url(url_type_or_path="css")

    @property
    def js_url(self):
        return self._get_url(url_type_or_path="js")

    @property
    def link_tag(self):
        return self._get_tag("css")

    @property
    def script_tag(self):
        return self._get_tag("js")

    @staticmethod
    def default_debug_path_converter(path):
        return path.replace("min.", "")

    def get_custom_version_url(self, url_type, version, debug=None):
        use_cdn = self.use_cdn
        if version == self.version:
            pass
        elif not self.use_cdn:
            logger.warning(
                f'The "STATICFILES_USE_NPM" setting is set to True, but the custom version "{self.npm_name}={version}" '
                f"is not supported. A CDN will be used to attempt to provide the custom version ({self.version})."
            )
            use_cdn = True
        return self._get_url(url_type, version, debug=debug, use_cdn=use_cdn)

    def get_js_urls(self, version=None):
        version = version or self.version
        if self.js_paths is None:
            return [self.get_custom_version_url("js", version)]
        else:
            return [self._get_url(url, version) for url in self.js_paths]

    def _get_url(self, url_type_or_path, version=None, debug=None, use_cdn=None):
        version = version or self.version
        debug = debug if debug is not None else settings.DEBUG
        use_cdn = use_cdn or self.use_cdn

        path = {
            url_type_or_path: url_type_or_path,
            "css": self.css_path,
            "js": self.js_path,
        }[url_type_or_path]

        if path is None:
            raise ValueError(
                f'The {url_type_or_path} url of the static dependency "{self.npm_name}" it is not defined.'
            )

        if debug:
            path = self.debug_path_converter(path)

        if use_cdn:
            return self.cdn_url.format(
                npm_name=self.npm_name, version=version, path=path
            )
        else:
            return self.static_url.format(npm_name=self.npm_name, path=path)

    def _get_tag(self, url_type):
        if url_type == "css":
            integrity = self.css_integrity
            url_template = '<link rel="stylesheet" href="{url}" {other_attrs} />'
            url = self.css_url
        else:
            integrity = self.js_integrity
            url_template = '<script src="{url}" {other_attrs}></script>'
            url = self.js_url

        if self.use_cdn:
            other_attrs = ""
            if integrity and not settings.DEBUG:
                other_attrs = f'integrity="{integrity}" crossorigin="anonymous"'
        else:
            other_attrs = ""
            url = static(url)
        return url_template.format(url=url, other_attrs=other_attrs)


class JsDelivrStaticDependency(StaticDependency):
    cdn_url = "https://cdn.jsdelivr.net/npm/{npm_name}@{version}/{path}"


class ArcGISStaticDependency(StaticDependency):
    cdn_url = "https://js.arcgis.com/{version}/{path}"

    def _get_url(self, url_type_or_path, version=None, debug=None, use_cdn=None):
        use_cdn = use_cdn or self.use_cdn
        if not use_cdn:
            raise ValueError(
                "The ArcGIS JS API is only available via CDN. "
                "It Can be downloaded using an API key from https://developers.arcgis.com/downloads/#javascript."
            )
        return super()._get_url(url_type_or_path, version, debug=debug)


vendor_static_dependencies = {
    "arcgis": ArcGISStaticDependency(
        npm_name="arcgis-js-api",  # Not sure if this is the right package
        version="4.24",
        js_path="/",
        css_path="esri/css/main.css",
    ),
    "bootstrap": JsDelivrStaticDependency(
        npm_name="bootstrap",
        version="5.1.3",
        css_path="dist/css/bootstrap.min.css",
        js_path="dist/js/bootstrap.bundle.min.js",
        css_integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3",
        js_integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p",
    ),
    "bootstrap-datepicker": JsDelivrStaticDependency(
        npm_name="bootstrap-datepicker",
        version="1.9.0",
        js_path="dist/js/bootstrap-datepicker.min.js",
        css_path="dist/css/bootstrap-datepicker3.min.css",
    ),
    "bootstrap_icons": JsDelivrStaticDependency(
        npm_name="bootstrap-icons",
        version="1.11.3",
        css_path="font/bootstrap-icons.min.css",
    ),
    "bootstrap-switch": JsDelivrStaticDependency(
        npm_name="bootstrap-switch",
        version="4.0.0-alpha.1",
        js_path="dist/js/bootstrap-switch.min.js",
        css_path="dist/css/bootstrap-switch.min.css",
    ),
    "cesiumjs": JsDelivrStaticDependency(
        npm_name="cesium",
        version="1.88",
        css_path="Build/Cesium/Widgets/widgets.css",
        js_path="Build/Cesium/Cesium.js",
        debug_path_converter=lambda path: path.replace("Cesium/", "CesiumUnminified/"),
    ),
    "d3": JsDelivrStaticDependency(
        npm_name="d3",
        version="7.3.0",
        js_path="dist/d3.min.js",
    ),
    "d3-tip": JsDelivrStaticDependency(
        npm_name="d3-v6-tip", version="1.0.9", js_path="build/d3-v6-tip.min.js"
    ),
    "dagre": JsDelivrStaticDependency(
        npm_name="dagre", version="0.8.5", js_path="dist/dagre.core.min.js"
    ),
    "dagre-d3": JsDelivrStaticDependency(
        npm_name="dagre-d3",
        version="0.6.4",
        js_path="dist/dagre-d3.core.min.js",
    ),
    "datatables": JsDelivrStaticDependency(
        npm_name="datatables.net",
        version="1.11.4",
        js_path="js/jquery.dataTables.min.js",
        # SRI for version 1.11.4
        js_integrity="sha256-hMOOju/zavxcwBsZt0hWn5kBaKk6QOfAKiAUgCJvUi0=",
    ),
    "datatables_bs5": JsDelivrStaticDependency(
        npm_name="datatables.net-bs5",
        version="1.11.4",
        css_path="css/dataTables.bootstrap5.min.css",
        js_path="js/dataTables.bootstrap5.min.js",
        # SRI for version 1.11.4
        css_integrity="sha256-Ba3RbD9Gjy82eeINezPTRD9kvWeLFx6fqpUGwrUTH1w=",
        js_integrity="sha256-2iYlCYmJTHCqEILUjOjrGFWPHIy4n6+CvHzOYZT2Sto=",
    ),
    "doc_cookies": JsDelivrStaticDependency(
        npm_name="doc-cookies",
        version="1.1.0",
        js_path="cookies_min.js",
        debug_path_converter=lambda path: path.replace("_min", ""),
    ),
    "graphlib": JsDelivrStaticDependency(
        npm_name="graphlib",
        version="2.1.8",
        js_path="dist/graphlib.core.min.js",
    ),
    "highcharts": JsDelivrStaticDependency(
        npm_name="highcharts",
        version="9.3.2",
        js_paths=["highcharts.js", "highcharts-more.js", "modules/exporting.js"],
    ),
    "jquery": JsDelivrStaticDependency(
        npm_name="jquery",
        version="3.6.0",
        js_path="dist/jquery.min.js",
        # SRI for version 3.6.0
        js_integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=",
    ),
    "lodash": JsDelivrStaticDependency(
        npm_name="lodash",
        version="4.17.21",
        js_path="lodash.min.js",
    ),
    "openlayers": JsDelivrStaticDependency(
        npm_name="openlayers-dist",
        version="6.12.0",
        js_path="ol.js",
        css_path="ol.css",
    ),
    "select2": JsDelivrStaticDependency(
        npm_name="select2",
        version="4.1.0-rc.0",
        js_path="dist/js/select2.min.js",
        css_path="dist/css/select2.min.css",
        # SRIs for version 4.1.0-rc.0
        js_integrity="sha256-9yRP/2EFlblE92vzCA10469Ctd0jT48HnmmMw5rJZrA=",
        css_integrity="sha256-zaSoHBhwFdle0scfGEFUCwggPN7F+ip9XRglo8IWb4w=",
    ),
}
