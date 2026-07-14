import warnings

import pytest
import unittest
from unittest import mock
import django
from django.db.backends.utils import CursorWrapper
import tethys_apps
from tethys_apps.apps import TethysAppsConfig


class TestApps(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_TethysAppsConfig(self):
        self.assertEqual("tethys_apps", TethysAppsConfig.name)
        self.assertEqual("Tethys Apps", TethysAppsConfig.verbose_name)

    @mock.patch("tethys_apps.apps.sync_portal_cookies")
    @mock.patch("tethys_apps.apps.has_module", return_value=False)
    @mock.patch("tethys_apps.apps.SingletonHarvester")
    @pytest.mark.django_db
    def test_ready(self, mock_singleton_harvester, _, mock_sync_portal_cookies):
        # simulate a non-migrate command (like runserver)
        with mock.patch("sys.argv", ["manage.py", "runserver"]):
            tethys_app_config_obj = TethysAppsConfig("tethys_apps", tethys_apps)
            tethys_app_config_obj.ready()
        mock_sync_portal_cookies.assert_not_called()
        mock_singleton_harvester().harvest.assert_called()

    @mock.patch("tethys_apps.apps.sync_portal_cookies")
    @mock.patch("tethys_apps.apps.has_module", return_value=True)
    @mock.patch("tethys_apps.apps.SingletonHarvester")
    @pytest.mark.django_db
    def test_ready_with_portal_cookies(
        self, mock_singleton_harvester, _, mock_sync_portal_cookies
    ):
        # simulate a non-migrate command (like runserver)
        with mock.patch("sys.argv", ["manage.py", "runserver"]):
            tethys_app_config_obj = TethysAppsConfig("tethys_apps", tethys_apps)
            tethys_app_config_obj.ready()
        mock_sync_portal_cookies.assert_called_once()
        mock_singleton_harvester().harvest.assert_called()

    @pytest.mark.skipif(
        django.VERSION < (5, 0),
        reason="app initialization warning introduced in Django 5.0",
    )
    @mock.patch("tethys_apps.apps.sync_portal_cookies")
    @mock.patch("tethys_apps.apps.has_module", return_value=False)
    @pytest.mark.django_db
    def test_ready_suppresses_db_init_warning(self, _, __):
        # harvesting intentionally queries the database during app initialization,
        # so Django's RuntimeWarning about it should be suppressed (see issue #1060)
        with mock.patch("tethys_apps.apps.SingletonHarvester") as mock_harvester:
            mock_harvester().harvest.side_effect = lambda: warnings.warn(
                CursorWrapper.APPS_NOT_READY_WARNING_MSG,
                category=RuntimeWarning,
                stacklevel=2,
            )
            with warnings.catch_warnings(record=True) as recorded:
                warnings.simplefilter("always")
                with mock.patch("sys.argv", ["manage.py", "runserver"]):
                    TethysAppsConfig("tethys_apps", tethys_apps).ready()
        self.assertListEqual(recorded, [])

    @mock.patch("tethys_apps.apps.sync_portal_cookies")
    @mock.patch("tethys_apps.apps.has_module", return_value=True)
    @mock.patch("tethys_apps.apps.SingletonHarvester")
    @pytest.mark.django_db
    def test_ready_migrate(self, mock_singleton_harvester, _, mock_sync_portal_cookies):
        # simulate a the migrate command
        with mock.patch("sys.argv", ["manage.py", "migrate"]):
            tethys_app_config_obj = TethysAppsConfig("tethys_apps", tethys_apps)
            tethys_app_config_obj.ready()
        mock_sync_portal_cookies.assert_not_called()
        mock_singleton_harvester().harvest.assert_not_called()
