import datetime as dt
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
        now = dt.datetime.utcnow()

        expected_context = {
            'site_defaults': {'copyright': f'Copyright © {now:%Y} Your Organization'},
            'site_globals': {
                'background_color': '#fefefe',
                'documents': ['active_terms'],
                'primary_color': '#0a62a9',
                'primary_text_color': '#ffffff',
                'primary_text_hover_color': '#eeeeee',
                'secondary_color': '#a2d6f9',
                'secondary_text_color': '#212529',
                'secondary_text_hover_color': '#aaaaaa'
            }
        }

        self.assertDictEqual(expected_context, ret)
