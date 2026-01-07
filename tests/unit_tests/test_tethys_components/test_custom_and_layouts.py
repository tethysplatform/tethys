import inspect
from json import dumps
from pathlib import Path
from tethys_components import custom, layouts
from tethys_components.library import ComponentLibrary
from unittest import TestCase, mock
from asgiref.sync import async_to_sync


THIS_DIR = Path(__file__).parent
CUSTOM_EVAL_DIR = THIS_DIR / "test_resources" / "test_custom_and_layouts"


class A:
    def __getattribute__(self, name):
        return "MOCK"


class TestCustomComponents(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = ComponentLibrary("components-test-lib")
        cls.mock_all = A()
        cls.lib.hooks = mock.MagicMock()
        cls.lib.hooks.use_query.return_value = mock.MagicMock(data=None)
        cls.lib.hooks.use_location.return_value = "MOCK"
        cls.lib.hooks.use_state.return_value = ("MOCK", lambda x: x)
        cls.required_kwargs_mapping = {
            "HeaderWithNavBar": [{"app": cls.mock_all, "user": cls.mock_all}],
            "NavHeader": [{"app": cls.mock_all, "user": cls.mock_all}],
            "PageLoader": [{"content": "TEST"}],
            "Chart": [{"data": [{"x": 1, "y": 2}, {"x": 2, "y": 10}]}, {"data": None}],
            "Display": [{"style": {"color": "black"}}],
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
