import unittest
from unittest import mock

from tethys_config.context_processors import tethys_global_settings_context


class TestTethysConfigContextProcessors(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('termsandconditions.models.TermsAndConditions')
    @mock.patch('tethys_config.models.Setting')
    def test_tethys_global_settings_context(self, mock_setting, mock_terms):
        mock_request = mock.MagicMock()
        mock_setting.as_dict.return_value = dict()
        mock_terms.get_active_terms_list.return_value = ['active_terms']
        mock_terms.get_active_list.return_value = ['active_list']

        ret = tethys_global_settings_context(mock_request)

        mock_setting.as_dict.assert_called_once()
        mock_terms.get_active_terms_list.assert_called_once()
        mock_terms.get_active_list.assert_not_called()

        self.assertEqual({'site_globals': {'documents': ['active_terms']}}, ret)
