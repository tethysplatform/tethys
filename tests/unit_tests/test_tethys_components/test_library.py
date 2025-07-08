import sys
from json import dumps
from unittest import TestCase, mock
from pathlib import Path
from tethys_components import library
import reactpy

THIS_DIR = Path(__file__).parent
LIBRARY_EVAL_DIR = THIS_DIR / "test_resources" / "test_library"


class TestComponentLibrary(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_pages = list(LIBRARY_EVAL_DIR.glob("test_page_*.py"))
        sys.path.append(str(LIBRARY_EVAL_DIR))

    @classmethod
    def tearDownClass(cls):
        sys.path.remove(str(LIBRARY_EVAL_DIR))

    def json_serializer(self, obj):
        if isinstance(obj, reactpy.types.Component):
            return obj.render()

    def test_building_complex_page(self):
        for test_page in self.test_pages:
            test_page_name = test_page.name[:-3]
            with self.subTest(page=test_page_name):
                expected_vdom_json_fpath = (
                    LIBRARY_EVAL_DIR / f"{test_page_name}_expected.json"
                )
                expected_js_module_fpath = (
                    LIBRARY_EVAL_DIR / f"{test_page_name}_expected.js"
                )

                lib = library.ComponentLibrary(test_page_name)
                lib.hooks = mock.MagicMock()
                lib.hooks.use_state.return_value = [mock.MagicMock(), mock.MagicMock()]
                test_module = __import__(test_page_name, fromlist=["test"])
                raw_vdom = test_module.test(lib)
                js_string = lib.render_js_template()
                json_vdom = dumps(raw_vdom, default=self.json_serializer)

                alternate_lib = library.ComponentLibrary(f"{test_page_name}_alternate")
                alternate_lib.load_dependencies_from_source_code(test_module.test)
                alternate_lib_js_string = lib.render_js_template()
                self.assertEqual(js_string, alternate_lib_js_string)

                # # Uncomment to create expected files when writing new test
                # expected_vdom_json_fpath.write_text(json_vdom)
                # expected_js_module_fpath.write_text(js_string)

                expected_json_vdom = expected_vdom_json_fpath.read_text()
                expected_js_string = expected_js_module_fpath.read_text()
                self.assertEqual(json_vdom, expected_json_vdom)
                self.assertEqual(js_string, expected_js_string)

    def test_cannot_instantiate_ComponentLibraryManager(self):
        with self.assertRaises(RuntimeError):
            library.ComponentLibraryManager()

    def test_package_version_mismatch(self):
        with self.assertRaises(ValueError):
            library.Package("this-lib@1.2.3", version="2.5.3")

    def test_package_manager_add_packages_invalid(self):
        pm = library.PackageManager()
        with self.assertRaises(TypeError):
            pm.add_packages("fail")

    def test_package_manager_check_non_package(self):
        pm = library.PackageManager()
        with self.assertRaises(TypeError):
            pm.check_package("foo", "incorrect type")

    def test_package_manager_check_accessor_taken(self):
        pm = library.PackageManager()
        pm.taken = "package"
        with self.assertRaises(ValueError):
            pm.check_package("taken", library.Package("test"))

    def test_library_package_already_registered_at_accessor(self):
        lib = library.ComponentLibrary("test123")
        lib.register("package", "foo")
        lib.register("package", "foo")  # This would fail if not programmed correctly
        with self.assertRaises(EnvironmentError):
            lib.register("another", "foo")

    def test_load_dependencies_from_source_code_skips_bad_match(self):
        lib = library.ComponentLibrary("test456")
        lib.load_dependencies_from_source_code("foo bar lib.does_not_exist(999)")
        self.assertFalse(hasattr(lib, "does_not_exist"))

    def test_attempt_at_incorrect_tethys_component(self):
        lib = library.ComponentLibrary("another_test")
        ccm = library.CustomComponentManager(lib)
        with self.assertRaises(AttributeError):
            ccm.tethys.does_not_exist

    def test_lib_hooks_are_reactpy_hooks(self):
        from tethys_components import hooks

        lib = library.ComponentLibrary("hooks_test")
        self.assertEqual(lib.hooks, hooks)
