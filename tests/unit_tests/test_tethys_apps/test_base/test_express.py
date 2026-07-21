import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from tethys_apps.base import express

COMPONENT_APP_SOURCE = """
from tethys_sdk.components import ComponentBase


class App(ComponentBase):
    pass


@App.page
def home(lib):
    return None


@App.page
def another_page(lib):
    return None
"""

COMPONENT_APP_WITH_METADATA_SOURCE = """
from tethys_sdk.components import ComponentBase


class App(ComponentBase):
    name = "My Custom Name"
    package = "custom_package"
    root_url = "custom-root-url"
    index = "custom_index"


@App.page
def custom_index(lib):
    return None
"""

NOT_A_COMPONENT_APP_SOURCE = """
class NotAnApp:
    pass
"""


class TestExpressHelpers(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_app_file(self, source, name="test_dashboard.py"):
        app_file = self.temp_path / name
        app_file.write_text(source)
        return app_file

    def test_get_express_app_file_not_set(self):
        with mock.patch.dict(express.environ, {}, clear=True):
            self.assertIsNone(express.get_express_app_file())

    def test_get_express_app_file_set(self):
        app_file = self.write_app_file(COMPONENT_APP_SOURCE)
        with mock.patch.dict(
            express.environ, {express.TETHYS_EXPRESS_APP_ENV: str(app_file)}
        ):
            self.assertEqual(app_file.resolve(), express.get_express_app_file())

    def test_find_component_app_class_node(self):
        app_file = self.write_app_file(COMPONENT_APP_SOURCE)
        node = express.find_component_app_class_node(app_file)
        self.assertIsNotNone(node)
        self.assertEqual("App", node.name)

    def test_find_component_app_class_node_not_component_app(self):
        app_file = self.write_app_file(NOT_A_COMPONENT_APP_SOURCE)
        self.assertIsNone(express.find_component_app_class_node(app_file))

    def test_find_component_app_class_node_invalid_syntax(self):
        app_file = self.write_app_file("def broken(:\n")
        self.assertIsNone(express.find_component_app_class_node(app_file))

    def test_find_component_app_class_node_missing_file(self):
        self.assertIsNone(
            express.find_component_app_class_node(self.temp_path / "no_such.py")
        )

    def test_derive_package_name(self):
        self.assertEqual(
            "my_dashboard", express.derive_package_name(Path("my-dashboard.py"))
        )

    def test_derive_package_name_leading_digit(self):
        self.assertEqual("app_2cool", express.derive_package_name(Path("2cool.py")))

    def test_derive_package_name_generic_app_uses_parent_dir(self):
        self.assertEqual(
            "flood_viewer",
            express.derive_package_name(Path("/tmp/Flood Viewer/app.py")),
        )

    def test_get_express_package_name_derived(self):
        app_file = self.write_app_file(COMPONENT_APP_SOURCE)
        self.assertEqual("test_dashboard", express.get_express_package_name(app_file))

    def test_get_express_package_name_explicit(self):
        app_file = self.write_app_file(COMPONENT_APP_WITH_METADATA_SOURCE)
        self.assertEqual("custom_package", express.get_express_package_name(app_file))


class TestSynthesizeExpressMetadata(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.app_file = Path(self.temp_dir.name) / "test_dashboard.py"
        self.app_file.write_text(COMPONENT_APP_SOURCE)

        self.fake_module = mock.MagicMock(__file__=str(self.app_file))
        sys.modules["_test_express_module"] = self.fake_module

        class DummyApp:
            __module__ = "_test_express_module"
            name = ""
            package = ""
            root_url = ""
            index = ""

        self.DummyApp = DummyApp

    def tearDown(self):
        del sys.modules["_test_express_module"]
        self.temp_dir.cleanup()

    def test_not_express_mode(self):
        with mock.patch.dict(express.environ, {}, clear=True):
            express.synthesize_express_metadata(self.DummyApp)
        self.assertEqual("", self.DummyApp.package)

    def test_synthesizes_missing_metadata(self):
        with mock.patch.dict(
            express.environ, {express.TETHYS_EXPRESS_APP_ENV: str(self.app_file)}
        ):
            express.synthesize_express_metadata(self.DummyApp)
        self.assertEqual("test_dashboard", self.DummyApp.package)
        self.assertEqual("Test Dashboard", self.DummyApp.name)
        self.assertEqual("test-dashboard", self.DummyApp.root_url)
        self.assertEqual("/", self.DummyApp.exit_url)
        self.assertEqual("NavHeader", self.DummyApp.default_layout)
        self.assertEqual("auto", self.DummyApp.nav_links)

    def test_does_not_override_existing_metadata(self):
        self.DummyApp.name = "Existing Name"
        self.DummyApp.package = "existing_package"
        self.DummyApp.default_layout = None
        with mock.patch.dict(
            express.environ, {express.TETHYS_EXPRESS_APP_ENV: str(self.app_file)}
        ):
            express.synthesize_express_metadata(self.DummyApp)
        self.assertEqual("Existing Name", self.DummyApp.name)
        self.assertEqual("existing_package", self.DummyApp.package)
        self.assertIsNone(self.DummyApp.default_layout)

    def test_ignores_classes_from_other_modules(self):
        other_file = Path(self.temp_dir.name) / "other.py"
        other_file.write_text(COMPONENT_APP_SOURCE)
        with mock.patch.dict(
            express.environ, {express.TETHYS_EXPRESS_APP_ENV: str(other_file)}
        ):
            express.synthesize_express_metadata(self.DummyApp)
        self.assertEqual("", self.DummyApp.package)


class TestHarvestExpressApp(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.app_file = Path(self.temp_dir.name) / "test_express_harvest.py"
        self.app_file.write_text(COMPONENT_APP_SOURCE)

    def tearDown(self):
        for name in list(sys.modules):
            if "test_express_harvest" in name:
                del sys.modules[name]

        from tethys_apps.base.component_base import AppSingleton

        AppSingleton._instances.pop("test_express_harvest", None)
        self.temp_dir.cleanup()

    def test_not_express_mode(self):
        with mock.patch.dict(express.environ, {}, clear=True):
            self.assertIsNone(express.harvest_express_app())

    def test_loads_and_registers_app(self):
        with mock.patch.dict(
            express.environ, {express.TETHYS_EXPRESS_APP_ENV: str(self.app_file)}
        ):
            package = express.harvest_express_app()

        self.assertEqual("test_express_harvest", package)
        self.assertIn("tethysapp.test_express_harvest", sys.modules)
        self.assertIn("tethysapp.test_express_harvest.app", sys.modules)

        module = sys.modules["tethysapp.test_express_harvest.app"]
        self.assertEqual("test_express_harvest", module.App.package)
        # Index defaults to the first page defined in the file
        self.assertEqual("home", module.App.index)

    def test_load_is_idempotent(self):
        with mock.patch.dict(
            express.environ, {express.TETHYS_EXPRESS_APP_ENV: str(self.app_file)}
        ):
            express.harvest_express_app()
            first_module = sys.modules["tethysapp.test_express_harvest.app"]
            express.harvest_express_app()
            self.assertIs(
                first_module, sys.modules["tethysapp.test_express_harvest.app"]
            )

    def test_no_app_class_exits(self):
        self.app_file.write_text(NOT_A_COMPONENT_APP_SOURCE)
        with mock.patch.dict(
            express.environ, {express.TETHYS_EXPRESS_APP_ENV: str(self.app_file)}
        ):
            with self.assertRaises(SystemExit):
                express.harvest_express_app()
        self.assertNotIn("tethysapp.test_express_harvest", sys.modules)
        self.assertNotIn("tethysapp.test_express_harvest.app", sys.modules)
