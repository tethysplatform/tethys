import unittest
import tethys_apps.base.testing.environment as base_environment
from os import environ


class TestEnvironment(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_set_testing_environment(self):
        base_environment.set_testing_environment(True)
        self.assertEqual("true", environ["TETHYS_TESTING_IN_PROGRESS"])

        result = base_environment.is_testing_environment()
        self.assertEqual("true", result)

        base_environment.set_testing_environment(False)
        self.assertIsNone(environ.get("TETHYS_TESTING_IN_PROGRESS"))

        result = base_environment.is_testing_environment()
        self.assertIsNone(result)

    def test_get_test_db_name(self):
        expected_result = "tethys-testing_test"
        result = base_environment.get_test_db_name("test")
        self.assertEqual(expected_result, result)

        result = base_environment.get_test_db_name("tethys-testing_test")
        self.assertEqual(expected_result, result)
