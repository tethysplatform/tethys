import unittest
import tethys_apps.base.app_base as tethys_app_base
import mock


class TestTethysBase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_url_maps(self):
        result = tethys_app_base.TethysBase().url_maps()
        self.assertFalse(result)
        # TODO: Ask Nathan how to test abstract base class

    @mock.patch('tethys_apps.base.app_base.tethys_log.error')
    @mock.patch('tethys_apps.base.app_base.TethysBase.url_maps')
    def test_url_patterns(self, mock_url_maps, mock_log):
        mock_url_maps.return_value = [mock.MagicMock(name='home', url='my-first-app',
                                                     controller='my_first_app.controllers.home')]

        # self.assertRaises(ImportError, tethys_app_base.TethysBase().url_patterns)
        # mock_log.assert_called_with("No module named my_first_app.controllers")

        pass

    def test_sync_with_tethys_db(self):
        self.assertRaises(NotImplementedError, tethys_app_base.TethysBase().sync_with_tethys_db)

    def test_remove_from_db(self):
        self.assertRaises(NotImplementedError, tethys_app_base.TethysBase().remove_from_db)
