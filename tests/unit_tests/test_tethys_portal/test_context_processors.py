import unittest
from django.test import override_settings
from tethys_portal import context_processors


class TestStaticDependency(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @override_settings(MULTIPLE_APP_MODE=False)
    def test_check_single_app_mode_single(self):
        single_app_mode, single_app_name = context_processors.check_single_app_mode()

        self.assertTrue(single_app_mode)
        self.assertTrue(single_app_name == "Test App")

    def test_check_single_app_mode_multiple(self):
        single_app_mode, single_app_name = context_processors.check_single_app_mode()

        self.assertFalse(single_app_mode)
        self.assertTrue(single_app_name is None)
