import inspect
from json import dumps
from pathlib import Path
from tethys_components import custom, layouts
from tethys_components.library import ComponentLibrary
from unittest import TestCase, mock


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
            "HeaderWithNavBar": ["app", "user"],
            "NavHeader": ["app", "user"],
        }

    def json_serializer(self, obj):
        val = str(obj)
        if "EventHandler" in val:
            val = "EventHandler"
        return val

    def _do_test(self, module):
        for attr in dir(module):
            module_name = module.__name__.split(".")[-1]
            if attr.startswith("_"):
                continue
            component = getattr(module, attr)
            if not callable(component):
                continue
            if list(inspect.signature(component).parameters.items())[0][0] != "lib":
                continue

            expected_vdom_json_fpath = (
                CUSTOM_EVAL_DIR / f"{module_name}__{attr}_expected.json"
            )
            kwargs = {}
            if attr in self.required_kwargs_mapping:
                kwargs = {k: self.mock_all for k in self.required_kwargs_mapping[attr]}
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

    def test_get_db_object(self):
        app = mock.MagicMock(db_object="expected")
        val = custom._get_db_object(app)
        self.assertEqual(val, "expected")
