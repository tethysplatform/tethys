import unittest
from unittest import mock
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

    @mock.patch('django.views.generic.View.as_view')
    def test_TethysController(self, mock_as_view):
        kwargs = {'foo': 'bar'}
        tethys_controller.TethysController.as_controller(**kwargs)
        mock_as_view.assert_called_with(**kwargs)
