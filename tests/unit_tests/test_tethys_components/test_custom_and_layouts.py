import inspect
from json import dumps
from pathlib import Path
from tethys_components import custom, layouts
from tethys_components.library import ComponentLibrary
from unittest import TestCase, mock
from django.test import override_settings
from tethys_portal.settings import STATIC_URL
from asgiref.sync import async_to_sync

THIS_DIR = Path(__file__).parent
CUSTOM_EVAL_DIR = THIS_DIR / "test_resources" / "test_custom_and_layouts"


class A:
    def __getattribute__(self, name):
        if name == "navigation_links":
            return [{"href": "https://test.com", "title": "Test"}]
        return "MOCK"


class B:
    @property
    def navigation_links(self):
        return [{"href": "https://test.com", "title": "Test"}]


class TestCustomComponents(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = ComponentLibrary("components-test-lib")
        cls.mock_all = A()
        cls.lib.hooks = mock.MagicMock()
        cls.lib.hooks.use_query.return_value = mock.MagicMock(data=None)
        cls.lib.hooks.use_location.return_value = A()
        cls.lib.hooks.use_state.return_value = ("MOCK", lambda x: x)
        cls.required_kwargs_mapping = {
            "HeaderWithNavBar": [{"app": cls.mock_all, "user": cls.mock_all}],
            "NavHeader": [{"app": cls.mock_all, "user": cls.mock_all}],
            "Chart": [{"data": [{"x": 1, "y": 2}, {"x": 2, "y": 10}]}, {"data": None}],
            "Display": [{"style": {"color": "black"}}],
            "AppNavLinks": [{"app": cls.mock_all}, {"app": B}],
        }

    def json_serializer(self, obj):
        val = str(obj)
        if "EventHandler" in val:
            val = "EventHandler"
        return val

    def _do_test(self, module):
        for attr in dir(module):
            with self.subTest(module=module, attr=attr):
                module_name = module.__name__.split(".")[-1]
                if attr.startswith("_"):
                    continue
                component = getattr(module, attr)
                if not callable(component):
                    continue
                if list(inspect.signature(component).parameters.items())[0][0] != "lib":
                    continue

                cases = [{}]
                if attr in self.required_kwargs_mapping:
                    cases = self.required_kwargs_mapping[attr]
                for case_num, case in enumerate(cases, 1):
                    expected_vdom_json_fpath = (
                        CUSTOM_EVAL_DIR
                        / f"{module_name}__{attr}_{case_num}_expected.json"
                    )
                    kwargs = case
                    raw_vdom = component(self.lib, **kwargs)
                    json_vdom = dumps(raw_vdom, default=self.json_serializer)

                    # # Uncomment to create expected files when writing new test
                    # expected_vdom_json_fpath.write_text(json_vdom)

                    expected_json_vdom = expected_vdom_json_fpath.read_text()
                    self.assertEqual(json_vdom, expected_json_vdom)

    def test_all_custom_components(self):
        self._do_test(custom)

    def test_all_layouts(self):
        self._do_test(layouts)

    def test_panel_special_case_1(self):
        mock_lib = mock.MagicMock()
        mock_lib.hooks.use_state.return_value = [mock.MagicMock(), mock.MagicMock()]
        with self.assertRaises(ValueError):
            custom.Panel(mock_lib, anchor="fail")

    def test_panel_special_case_2(self):
        mock_lib = mock.MagicMock()
        style = mock.MagicMock()
        custom.Panel(mock_lib, anchor="top", style=style)
        style.__setitem__.assert_called_once_with("height", "500px")

    def test_panel_special_case_3(self):
        proof = mock.MagicMock()

        def test_on_close(val):
            proof(val)

        panel = custom.Panel(self.lib, on_close=test_on_close)
        async_to_sync(
            panel["children"][0]["children"][1]["eventHandlers"]["onClick"].function
        )(["ignored"])
        proof.assert_called_once_with("ignored")

    def test_navheader_special_case_1(self):
        content = "not_list"
        layout = layouts.NavHeader(
            self.lib, app=self.mock_all, user=self.mock_all, content=content
        )
        vdom_content = layout["children"][1]["children"]
        self.assertIsInstance(vdom_content, list)
        self.assertListEqual([content], vdom_content)

    def test_map_invalid_projection_dict(self):
        with self.assertRaises(ValueError):
            custom.Map(self.lib, projection={})


class FakeApp:
    """Minimal stand-in for a ComponentBase app with only the attributes the header reads."""

    name = "Test App"
    root_url = "test-app"
    color = "#2c3e50"
    exit_url = "/"
    icon = ""
    navigation_links = [{"href": "/", "title": "Home"}]


def _find_nodes(vdom, predicate):
    """Depth-first search of a VDOM tree for element dicts matching predicate."""
    found = []
    if isinstance(vdom, dict):
        if predicate(vdom):
            found.append(vdom)
        for value in vdom.values():
            found.extend(_find_nodes(value, predicate))
    elif isinstance(vdom, (list, tuple)):
        for item in vdom:
            found.extend(_find_nodes(item, predicate))
    return found


def _attr(node, name):
    return node.get("attributes", {}).get(name)


class TestHeaderWithNavBarUrls(TestCase):
    """The header must work both under /apps/<root_url>/ and at the site root (single-app mode)."""

    def setUp(self):
        self.lib = ComponentLibrary("components-test-lib-header")
        self.lib.hooks = mock.MagicMock()
        self.lib.hooks.use_query.return_value = mock.MagicMock(data=None)
        self.lib.hooks.use_location.return_value = mock.MagicMock(pathname="/")
        self.lib.hooks.use_state.return_value = (0, lambda x: x)
        self.user = mock.MagicMock(is_staff=False)

    def render(self, app):
        return custom.HeaderWithNavBar(self.lib, app=app, user=self.user)

    def brand_and_nav(self, vdom):
        brand = _find_nodes(vdom, lambda n: n.get("tagName") == "bs_NavbarBrand")
        nav = _find_nodes(vdom, lambda n: n.get("tagName") == "bs_Nav")
        self.assertEqual(1, len(brand))
        self.assertEqual(1, len(nav))
        return brand[0], nav[0]

    @override_settings(MULTIPLE_APP_MODE=True)
    def test_brand_links_to_app_url_in_multiple_app_mode(self):
        brand, nav = self.brand_and_nav(self.render(FakeApp()))
        self.assertEqual("/apps/test-app/", _attr(brand, "href"))
        self.assertEqual("/apps/test-app", _attr(nav, "defaultActiveKey"))

    @override_settings(MULTIPLE_APP_MODE=False)
    def test_brand_links_to_root_in_single_app_mode(self):
        brand, nav = self.brand_and_nav(self.render(FakeApp()))
        self.assertEqual("/", _attr(brand, "href"))
        self.assertEqual("/", _attr(nav, "defaultActiveKey"))

