import pytest
import datetime as dt
from unittest import mock

from tethys_config.context_processors import tethys_global_settings_context


@mock.patch("termsandconditions.models.TermsAndConditions")
@mock.patch("tethys_config.models.Setting")
@pytest.mark.django_db
def test_tethys_global_settings_context_multiple_app_mode(
    mock_setting, mock_terms, test_app, settings
):
    settings.MULTIPLE_APP_MODE = True
    mock_request = mock.MagicMock()
    mock_setting.as_dict.return_value = dict()
    mock_terms.get_active_terms_list.return_value = ["active_terms"]
    mock_terms.get_active_list.return_value = ["active_list"]

    ret = tethys_global_settings_context(mock_request)

    mock_setting.as_dict.assert_called_once()
    mock_terms.get_active_terms_list.assert_called_once()
    mock_terms.get_active_list.assert_not_called()
    now = dt.datetime.now(dt.timezone.utc)

    expected_context = {
        "site_defaults": {"copyright": f"Copyright © {now:%Y} Your Organization"},
        "site_globals": {
            "background_color": "#fefefe",
            "documents": ["active_terms"],
            "primary_color": "#0a62a9",
            "primary_text_color": "#ffffff",
            "primary_text_hover_color": "#eeeeee",
            "secondary_color": "#a2d6f9",
            "secondary_text_color": "#212529",
            "secondary_text_hover_color": "#aaaaaa",
        },
    }
    assert expected_context == ret


@mock.patch("termsandconditions.models.TermsAndConditions")
@mock.patch("tethys_config.models.Setting")
@pytest.mark.django_db
def test_tethys_global_settings_context_single_app_mode(
    mock_setting, mock_terms, test_app, settings
):
    settings.MULTIPLE_APP_MODE = False
    settings.CONFIGURED_STANDALONE_APP = "test_app"
    mock_request = mock.MagicMock()
    mock_setting.as_dict.return_value = dict()
    mock_terms.get_active_terms_list.return_value = ["active_terms"]
    mock_terms.get_active_list.return_value = ["active_list"]

    ret = tethys_global_settings_context(mock_request)

    mock_setting.as_dict.assert_called_once()
    mock_terms.get_active_terms_list.assert_called_once()
    mock_terms.get_active_list.assert_not_called()
    now = dt.datetime.now(dt.timezone.utc)

    expected_context = {
        "site_defaults": {"copyright": f"Copyright © {now:%Y} Your Organization"},
        "site_globals": {
            "background_color": "#fefefe",
            "documents": ["active_terms"],
            "primary_color": "#0a62a9",
            "primary_text_color": "#ffffff",
            "primary_text_hover_color": "#eeeeee",
            "secondary_color": "#a2d6f9",
            "secondary_text_color": "#212529",
            "secondary_text_hover_color": "#aaaaaa",
            "brand_image": "test_app/images/icon.gif",
            "brand_text": "Test App",
            "site_title": "Test App",
        },
    }
    assert expected_context == ret


@mock.patch("termsandconditions.models.TermsAndConditions")
@mock.patch("tethys_config.models.Setting")
@mock.patch("tethys_config.context_processors.get_configured_standalone_app")
@pytest.mark.django_db
def test_tethys_global_settings_context_single_app_mode_no_app(
    mock_get_configured_standalone_app, mock_setting, mock_terms, test_app, settings
):
    settings.MULTIPLE_APP_MODE = False
    settings.CONFIGURED_STANDALONE_APP = "test_app"
    mock_request = mock.MagicMock()
    mock_setting.as_dict.return_value = dict()
    mock_terms.get_active_terms_list.return_value = ["active_terms"]
    mock_terms.get_active_list.return_value = ["active_list"]
    mock_get_configured_standalone_app.return_value = None

    ret = tethys_global_settings_context(mock_request)

    mock_setting.as_dict.assert_called_once()
    mock_terms.get_active_terms_list.assert_called_once()
    mock_terms.get_active_list.assert_not_called()
    now = dt.datetime.now(dt.timezone.utc)

    expected_context = {
        "site_defaults": {"copyright": f"Copyright © {now:%Y} Your Organization"},
        "site_globals": {
            "background_color": "#fefefe",
            "documents": ["active_terms"],
            "primary_color": "#0a62a9",
            "primary_text_color": "#ffffff",
            "primary_text_hover_color": "#eeeeee",
            "secondary_color": "#a2d6f9",
            "secondary_text_color": "#212529",
            "secondary_text_hover_color": "#aaaaaa",
        },
    }
    assert expected_context == ret
