import sys
from unittest import TestCase, mock

import tethys_cli.cookie_commands as cookie_commands


class TestCookieCommands(TestCase):
    def setUp(self):
        # Patch out Django setup and CLI output functions
        self.p_setup = mock.patch("tethys_cli.cookie_commands.setup_django")
        self.mock_setup = self.p_setup.start()

        self.p_write_success = mock.patch("tethys_cli.cookie_commands.write_success")
        self.mock_write_success = self.p_write_success.start()

        self.p_write_error = mock.patch("tethys_cli.cookie_commands.write_error")
        self.mock_write_error = self.p_write_error.start()

        self.p_write_info = mock.patch("tethys_cli.cookie_commands.write_info")
        self.mock_write_info = self.p_write_info.start()

        self.addCleanup(self.p_setup.stop)
        self.addCleanup(self.p_write_success.stop)
        self.addCleanup(self.p_write_error.stop)
        self.addCleanup(self.p_write_info.stop)

    def tearDown(self):
        pass

    def _make_models_module(self):
        # Create a fresh fake cookie_consent.models module for each test
        models_mod = mock.MagicMock()
        models_mod.CookieGroup = mock.MagicMock()
        models_mod.Cookie = mock.MagicMock()
        return models_mod

    def test_cli_add_cookie_group_success(self):
        models_mod = self._make_models_module()
        # create should succeed
        models_mod.CookieGroup.objects.create = mock.MagicMock()

        with mock.patch.dict(
            sys.modules,
            {"cookie_consent": mock.MagicMock(), "cookie_consent.models": models_mod},
        ):
            args = mock.MagicMock(
                varname="analytics",
                description="desc",
                is_required=False,
                is_deletable=True,
                ordering=5,
            )
            args.name = "Analytics"
            cookie_commands.cli_add_cookie_group(args)

        models_mod.CookieGroup.objects.create.assert_called_with(
            varname="analytics",
            name="Analytics",
            description="desc",
            is_required=False,
            is_deletable=True,
            ordering=5,
        )
        self.mock_write_success.assert_called_once()

    @mock.patch("tethys_cli.cookie_commands.exit")
    def test_cli_add_cookie_group_duplicate(self, mock_exit):
        mock_exit.side_effect = SystemExit
        models_mod = self._make_models_module()

        def raise_unique(*a, **k):
            raise Exception("UNIQUE constraint failed")

        models_mod.CookieGroup.objects.create = mock.MagicMock(side_effect=raise_unique)

        with mock.patch.dict(
            sys.modules,
            {"cookie_consent": mock.MagicMock(), "cookie_consent.models": models_mod},
        ):
            args = mock.MagicMock(
                varname="analytics",
                name="Analytics",
                description="",
                is_required=False,
                is_deletable=True,
                ordering=0,
            )
            with self.assertRaises(SystemExit):
                cookie_commands.cli_add_cookie_group(args)

        self.mock_write_error.assert_called_once()
        mock_exit.assert_called_with(1)

    def test_cli_add_cookie_success(self):
        models_mod = self._make_models_module()
        models_mod.Cookie.objects.create = mock.MagicMock()
        # CookieGroup.objects.get used to fetch foreign key
        fake_group = mock.MagicMock()
        models_mod.CookieGroup.objects.get = mock.MagicMock(return_value=fake_group)

        with mock.patch.dict(
            sys.modules,
            {"cookie_consent": mock.MagicMock(), "cookie_consent.models": models_mod},
        ):
            args = mock.MagicMock(
                cookiegroup="analytics", description="d", path="/", domain="example.com"
            )
            args.name = "ga"
            cookie_commands.cli_add_cookie(args)

        models_mod.Cookie.objects.create.assert_called_with(
            cookiegroup=fake_group,
            name="ga",
            description="d",
            path="/",
            domain="example.com",
        )
        self.mock_write_success.assert_called_once()

    @mock.patch("tethys_cli.cookie_commands.exit")
    def test_cli_add_cookie_group_missing_group(self, mock_exit):
        mock_exit.side_effect = SystemExit
        models_mod = self._make_models_module()
        # Simulate CookieGroup.objects.get raising an exception with "does not exist"
        models_mod.CookieGroup.objects.get = mock.MagicMock(
            side_effect=Exception("CookieGroup matching query does not exist")
        )

        with mock.patch.dict(
            sys.modules,
            {"cookie_consent": mock.MagicMock(), "cookie_consent.models": models_mod},
        ):
            args = mock.MagicMock(
                cookiegroup="nope", name="ga", description="d", path="/", domain=""
            )
            with self.assertRaises(SystemExit):
                cookie_commands.cli_add_cookie(args)

        self.mock_write_error.assert_called_once()
        mock_exit.assert_called_with(1)

    def test_cli_delete_cookie_group_success(self):
        models_mod = self._make_models_module()
        # No cookies in group
        models_mod.Cookie.objects.filter.return_value.exists.return_value = False
        fake_group = mock.MagicMock()
        fake_group.delete = mock.MagicMock()
        models_mod.CookieGroup.objects.get.return_value = fake_group

        with mock.patch.dict(
            sys.modules,
            {"cookie_consent": mock.MagicMock(), "cookie_consent.models": models_mod},
        ):
            args = mock.MagicMock(varname="analytics", cascade=False)
            cookie_commands.cli_delete_cookie_group(args)

        models_mod.CookieGroup.objects.get.assert_called_with(varname="analytics")
        fake_group.delete.assert_called_once()
        self.mock_write_success.assert_called_once()

    @mock.patch("tethys_cli.cookie_commands.exit")
    def test_cli_delete_cookie_group_has_cookies_no_cascade(self, mock_exit):
        mock_exit.side_effect = SystemExit
        models_mod = self._make_models_module()
        models_mod.Cookie.objects.filter.return_value.exists.return_value = True

        with mock.patch.dict(
            sys.modules,
            {"cookie_consent": mock.MagicMock(), "cookie_consent.models": models_mod},
        ):
            args = mock.MagicMock(varname="analytics", cascade=False)
            with self.assertRaises(SystemExit):
                cookie_commands.cli_delete_cookie_group(args)

        # Should have written an error and exited
        self.mock_write_error.assert_called_once()
        mock_exit.assert_called_with(1)

    def test_cli_delete_cookie_group_missing(self):
        models_mod = self._make_models_module()
        models_mod.Cookie.objects.filter.return_value.exists.return_value = False
        models_mod.CookieGroup.objects.get.side_effect = Exception("does not exist")

        with mock.patch.dict(
            sys.modules,
            {"cookie_consent": mock.MagicMock(), "cookie_consent.models": models_mod},
        ):
            args = mock.MagicMock(varname="nope", cascade=False)
            cookie_commands.cli_delete_cookie_group(args)

        self.mock_write_error.assert_called_once()

    def test_cli_delete_cookie_success(self):
        models_mod = self._make_models_module()
        fake_group = mock.MagicMock()
        models_mod.CookieGroup.objects.get.return_value = fake_group
        fake_cookie = mock.MagicMock()
        fake_cookie.delete = mock.MagicMock()
        models_mod.Cookie.objects.get.return_value = fake_cookie

        with mock.patch.dict(
            sys.modules,
            {"cookie_consent": mock.MagicMock(), "cookie_consent.models": models_mod},
        ):
            args = mock.MagicMock(group="analytics")
            args.name = "ga"
            cookie_commands.cli_delete_cookie(args)

        models_mod.CookieGroup.objects.get.assert_called_with(varname="analytics")
        models_mod.Cookie.objects.get.assert_called_with(
            cookiegroup=fake_group, name="ga"
        )
        fake_cookie.delete.assert_called_once()
        self.mock_write_success.assert_called_once()

    @mock.patch("tethys_cli.cookie_commands.exit")
    def test_cli_delete_cookie_group_not_found_error(self, mock_exit):
        mock_exit.side_effect = SystemExit
        models_mod = self._make_models_module()
        models_mod.CookieGroup.objects.get.side_effect = Exception(
            "CookieGroup matching query does not exist"
        )

        with mock.patch.dict(
            sys.modules,
            {"cookie_consent": mock.MagicMock(), "cookie_consent.models": models_mod},
        ):
            args = mock.MagicMock(group="nope", name="x")
            with self.assertRaises(SystemExit):
                cookie_commands.cli_delete_cookie(args)

        self.mock_write_error.assert_called_once()
        mock_exit.assert_called_with(1)

    @mock.patch("tethys_cli.cookie_commands.exit")
    def test_cli_delete_cookie_not_found_error(self, mock_exit):
        mock_exit.side_effect = SystemExit
        models_mod = self._make_models_module()
        fake_group = mock.MagicMock()
        models_mod.CookieGroup.objects.get.return_value = fake_group
        models_mod.Cookie.objects.get.side_effect = Exception(
            "Cookie matching query does not exist"
        )

        with mock.patch.dict(
            sys.modules,
            {"cookie_consent": mock.MagicMock(), "cookie_consent.models": models_mod},
        ):
            args = mock.MagicMock(group="analytics", name="nope")
            with self.assertRaises(SystemExit):
                cookie_commands.cli_delete_cookie(args)

        self.mock_write_error.assert_called_once()
        mock_exit.assert_called_with(1)

    def test_cli_list_cookies_with_and_without_cookies(self):
        models_mod = self._make_models_module()

        # Group without cookies
        group1 = mock.MagicMock()
        group1.name = "Necessary"
        group1.varname = "necessary"
        group1.description = "req"
        group1.is_required = True
        group1.is_deletable = False
        group1.ordering = 1
        group1.created = "2020-01-01"
        group1.cookie_set.all.return_value = []

        # Group with cookies
        group2 = mock.MagicMock()
        group2.name = "Analytics"
        group2.varname = "analytics"
        group2.description = "desc"
        group2.is_required = False
        group2.is_deletable = True
        group2.ordering = 2
        group2.created = "2020-02-02"
        cookie = mock.MagicMock()
        cookie.name = "ga"
        cookie.description = "google"
        cookie.path = "/"
        cookie.domain = "example.com"
        group2.cookie_set.all.return_value = [cookie]

        # Make the queryset chain .all().order_by(...) return our list
        class AllQSet:
            def __init__(self, items):
                self._items = items

            def order_by(self, *_):
                return self._items

        models_mod.CookieGroup.objects.all.return_value = AllQSet([group1, group2])

        with mock.patch.dict(
            sys.modules,
            {"cookie_consent": mock.MagicMock(), "cookie_consent.models": models_mod},
        ):
            cookie_commands.cli_list_cookies(None)

        # There should be many write_info calls; assert some expected messages were written
        calls = [c[0][0] for c in self.mock_write_info.call_args_list]
        self.assertIn("Necessary (necessary):", calls)
        self.assertIn("  - No cookies in this group.", calls)
        self.assertIn("Analytics (analytics):", calls)
        self.assertIn("   -  Name: ga", calls)

    def test_cli_purge_cookies(self):
        models_mod = self._make_models_module()
        # Ensure delete calls exist
        models_mod.Cookie.objects.all.return_value.delete = mock.MagicMock()
        models_mod.CookieGroup.objects.all.return_value.delete = mock.MagicMock()

        with mock.patch.dict(
            sys.modules,
            {"cookie_consent": mock.MagicMock(), "cookie_consent.models": models_mod},
        ):
            cookie_commands.cli_purge_cookies(None)

        models_mod.Cookie.objects.all.return_value.delete.assert_called_once()
        models_mod.CookieGroup.objects.all.return_value.delete.assert_called_once()
        self.mock_write_success.assert_called_once_with(
            "All cookie groups and cookies have been deleted."
        )
