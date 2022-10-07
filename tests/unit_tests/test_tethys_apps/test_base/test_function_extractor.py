import unittest
import types
import tethys_apps.base.function_extractor as tethys_function_extractor


def test_func():
    pass


class TestTethysFunctionExtractor(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        path = "tethysapp-test_app.tethysapp.test_app.controller.home"
        result = tethys_function_extractor.TethysFunctionExtractor(path=path)

        # Check Result
        self.assertEqual(path, result.path)
        self.assertEqual("tethysapp", result.prefix)

    def test_init_func(self):
        result = tethys_function_extractor.TethysFunctionExtractor(path=test_func)

        # Check Result
        self.assertIs(test_func, result.function)
        self.assertTrue(result.valid)

    def test_valid(self):
        path = "test_app.model.test_initializer"
        result = tethys_function_extractor.TethysFunctionExtractor(path=path).valid

        # Check Result
        self.assertTrue(result)

    def test_function(self):
        path = "test_app.model.test_initializer"
        result = tethys_function_extractor.TethysFunctionExtractor(path=path).function

        # Check Result
        self.assertIsInstance(result, types.FunctionType)

    def test_function_error(self):
        path = "test_app1.foo"
        app = tethys_function_extractor.TethysFunctionExtractor(path=path, throw=True)

        def test_function_import():
            return app.function

        self.assertRaises(ImportError, test_function_import)
