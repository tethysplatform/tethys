import unittest
from unittest import mock
import tethys_apps.base.controller as tethys_controller


class TestController(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('django.views.generic.View.as_view')
    def test_TethysController(self, mock_as_view):
        kwargs = {'foo': 'bar'}
        tethys_controller.TethysController.as_controller(**kwargs)
        mock_as_view.assert_called_with(**kwargs)
