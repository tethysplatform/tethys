import unittest
from tethys_portal import optional_dependencies


class TestStaticDependency(unittest.TestCase):
    def setUp(self):
        self.module = "test_module"
        self.import_error = "error"
        self.failed_import = optional_dependencies.FailedImport(
            self.module, self.import_error
        )

    def tearDown(self):
        pass

    def test_failed_import_init(self):
        module = "test_module"
        import_error = "error"
        failed_import = optional_dependencies.FailedImport(module, import_error)
        self.assertEqual(failed_import.module_name, module)
        self.assertEqual(failed_import.error, import_error)

    def test_failed_import_call(self):
        self.assertRaises(ImportError, lambda: self.failed_import.test())

    def test_failed_import_getattr(self):
        self.assertRaises(ImportError, lambda: self.failed_import.test)

    def test_failed_import_getitem(self):
        self.assertRaises(ImportError, lambda: self.failed_import["test"])

    def test__attempt_import_error(self):
        module = optional_dependencies._attempt_import(
            self.module, from_module=None, error_message=None
        )
        self.assertIsInstance(module, optional_dependencies.FailedImport)

    def test_verify_import(self):
        self.assertRaises(
            ImportError, optional_dependencies.verify_import, self.failed_import
        )
