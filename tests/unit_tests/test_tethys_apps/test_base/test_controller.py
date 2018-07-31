import unittest
import tethys_apps.base.controller as tethys_controller


class TestController(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_app_controller_maker(self):
        root_url = 'test_root_url'
        result = tethys_controller.app_controller_maker(root_url)
        self.assertEqual(result.root_url, root_url)
        self.assertEqual(result.__module__, 'tethys_apps.base.controller')

    def test_TethysController(self):
        result = tethys_controller.TethysController.as_controller()
        self.assertEqual(result.__module__, 'tethys_apps.base.controller')
