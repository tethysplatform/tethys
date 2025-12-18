import sys
from unittest import mock, TestCase
from pathlib import Path

from django.core.exceptions import ObjectDoesNotExist
from tethys_portal import cookies

RESOURCES_DIR = Path(__file__).parent / "resources"


class TestCookiesModule(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_cookie_config_basic_and_purge(self):
        p = RESOURCES_DIR / "basic_cookies.yaml"

        cfg = cookies._get_cookie_config(p, "MyApp")

        # necessary is empty so should be purged, analytics present
        self.assertIn("analytics", cfg)
        self.assertNotIn("necessary", cfg)
        self.assertEqual(cfg["analytics"]["cookies"]["ga"]["description"], "desc")
        # description formatted with name
        self.assertIn("MyApp", cfg["analytics"]["description"])

    def test_get_cookie_config_invalid_group(self):
        p = RESOURCES_DIR / "invalid_cookies.yaml"
        with self.assertRaises(ValueError):
            cookies._get_cookie_config(p, "App")

    def _make_models(self):
        models = mock.MagicMock()
        models.CookieGroup = mock.MagicMock()
        models.Cookie = mock.MagicMock()
        return models

    def test_sync_cookies_from_dict_create_and_delete(self):
        models = self._make_models()

        # Existing DB groups: one obsolete group, one to update
        obsolete = mock.MagicMock()
        obsolete.varname = "app__old"
        obsolete.delete = mock.MagicMock()

        to_update = mock.MagicMock()
        to_update.varname = "app__keep"
        # cookie in DB that is not in config -> should be deleted
        db_cookie = mock.MagicMock()
        db_cookie.name = "old_cookie"
        db_cookie.delete = mock.MagicMock()
        to_update.cookie_set.all.return_value = [db_cookie]

        models.CookieGroup.objects.filter.return_value.all.return_value = [
            obsolete,
            to_update,
        ]

        # Config defines only 'keep' group with one cookie 'new_cookie'
        config = {
            "keep": {
                "name": "Keep",
                "description": "desc",
                "is_required": False,
                "is_deletable": True,
                "ordering": 1,
                "cookies": {
                    "new_cookie": {"description": "d", "path": "/", "domain": ""}
                },
            }
        }

        # to_update.group.get(cookie name) should raise ObjectDoesNotExist to simulate missing cookie
        to_update.cookie_set.get.side_effect = ObjectDoesNotExist(
            "cookie does not exist"
        )

        # CookieGroup.objects.get for existing config group should raise to simulate creation path
        models.CookieGroup.objects.get.side_effect = ObjectDoesNotExist(
            "cookie group does not exist"
        )

        with mock.patch.dict(
            sys.modules,
            {"cookie_consent": mock.MagicMock(), "cookie_consent.models": models},
        ):
            cookies._sync_cookies_from_dict(config, "app", "App Name")

        # obsolete group deleted
        obsolete.delete.assert_called_once()
        # db cookie deleted
        db_cookie.delete.assert_called_once()
        # CookieGroup.create called for new group
        models.CookieGroup.objects.create.assert_called()
        # Cookie.create called for new cookie
        models.Cookie.objects.create.assert_called()

    def test_update_existing_cookie_group_cookie_exists(self):
        models = self._make_models()

        # Existing DB group matching config
        db_group = mock.MagicMock()
        db_group.varname = "app__analytics"
        # Setup cookie_set.get to return existing cookie object
        existing_cookie = mock.MagicMock()
        existing_cookie.name = "ga"
        existing_cookie.save = mock.MagicMock()
        db_group.cookie_set.get.return_value = existing_cookie

        models.CookieGroup.objects.filter.return_value.all.return_value = []
        # When getting the db group by varname, return db_group
        models.CookieGroup.objects.get.return_value = db_group

        config = {
            "analytics": {
                "name": "Analytics",
                "description": "desc",
                "is_required": False,
                "is_deletable": True,
                "ordering": 3,
                "cookies": {
                    "ga": {"description": "newdesc", "path": "/new", "domain": "ex"}
                },
            }
        }

        with mock.patch.dict(
            sys.modules,
            {"cookie_consent": mock.MagicMock(), "cookie_consent.models": models},
        ):
            cookies._sync_cookies_from_dict(config, "app", "App")

        # group fields should be updated and save called
        self.assertIn("App: Analytics", db_group.name)
        self.assertEqual(db_group.description, "desc")
        self.assertEqual(db_group.ordering, 3)
        db_group.save.assert_called_once()

        # existing cookie should have been updated and saved
        self.assertEqual(existing_cookie.description, "newdesc")
        self.assertEqual(existing_cookie.path, "/new")
        self.assertEqual(existing_cookie.domain, "ex")
        existing_cookie.save.assert_called_once()

    def test_update_existing_cookie_group_cookie_does_not_exist(self):
        models = self._make_models()

        # Existing DB group matching config
        db_group = mock.MagicMock()
        db_group.varname = "app__analytics"
        # Setup cookie_set.get to not find cookie
        db_group.cookie_set.get.side_effect = ObjectDoesNotExist

        models.CookieGroup.objects.filter.return_value.all.return_value = []
        # When getting the db group by varname, return db_group
        models.CookieGroup.objects.get.return_value = db_group

        config = {
            "analytics": {
                "name": "Analytics",
                "description": "desc",
                "is_required": False,
                "is_deletable": True,
                "ordering": 3,
                "cookies": {
                    "ga": {"description": "newdesc", "path": "/new", "domain": "ex"}
                },
            }
        }

        with mock.patch.dict(
            sys.modules,
            {"cookie_consent": mock.MagicMock(), "cookie_consent.models": models},
        ):
            cookies._sync_cookies_from_dict(config, "app", "App")

        # group fields should be updated and save called
        self.assertIn("App: Analytics", db_group.name)
        self.assertEqual(db_group.description, "desc")
        self.assertEqual(db_group.ordering, 3)
        db_group.save.assert_called_once()

        # existing cookie should have been updated and saved
        models.Cookie.objects.create.assert_called_once_with(
            cookiegroup=db_group,
            name="ga",
            description="newdesc",
            path="/new",
            domain="ex",
        )

    @mock.patch("tethys_portal.cookies._sync_cookies_from_dict")
    @mock.patch("tethys_portal.cookies._get_cookie_config")
    def test_sync_cookies_from_yaml(self, mock_gcc, mock_scfd):
        yaml_path = "path/to/cookies.yaml"
        namespace = "test"
        name = "Test"
        gcc_return = "mock_dict"
        mock_gcc.return_value = gcc_return
        cookies.sync_cookies_from_yaml(yaml_path, namespace, name)
        mock_gcc.assert_called_once_with(yaml_path, name)
        mock_scfd.assert_called_once_with(gcc_return, namespace, name)

    @mock.patch("tethys_portal.cookies.Path")
    @mock.patch("tethys_portal.cookies.sync_cookies_from_yaml")
    def test_sync_portal_cookies(self, mock_scft, mock_path):
        cookies.sync_portal_cookies()
        mock_scft.assert_called_once_with(
            mock_path().parent.__truediv__().__truediv__(),
            "tethys_portal",
            "Tethys Portal",
        )
