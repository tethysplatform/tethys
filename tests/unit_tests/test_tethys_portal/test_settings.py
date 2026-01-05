import datetime as dt
from importlib import reload
from unittest import mock, TestCase
from tethys_portal import settings


class TestSettings(TestCase):
    def set_up(self):
        pass

    def tear_down(self):
        pass

    @mock.patch(
        "tethys_portal.settings.yaml.safe_load",
        return_value={"settings": {"test": "test"}},
    )
    def test_portal_config_settings(self, mock_local_settings):
        reload(settings)
        self.assertDictEqual(
            settings.portal_config_settings,
            mock_local_settings.return_value["settings"],
        )

    @mock.patch(
        "tethys_portal.settings.yaml.safe_load", side_effect=FileNotFoundError()
    )
    @mock.patch("tethys_portal.settings.logging.getLogger")
    def test_portal_config_file_not_found_error(self, mock_log, _):
        reload(settings)
        mock_log.return_value.info.assert_called()

    @mock.patch("tethys_portal.settings.yaml.safe_load", side_effect=RuntimeError())
    @mock.patch("tethys_portal.settings.logging.getLogger")
    def test_portal_config_exception(self, mock_log, _):
        reload(settings)
        mock_log.return_value.exception.assert_called()

    @mock.patch(
        "tethys_portal.settings.yaml.safe_load",
        return_value={
            "settings": {"TETHYS_PORTAL_CONFIG": {"test_portal_key": "test"}}
        },
    )
    def test_tethys_portal_config(self, _):
        reload(settings)
        self.assertEqual(settings.test_portal_key, "test")

    @mock.patch(
        "tethys_portal.settings.yaml.safe_load",
        return_value={"settings": {"EMAIL_CONFIG": {"test_email_key": "test"}}},
    )
    def test_email_config(self, _):
        reload(settings)
        self.assertEqual(settings.test_email_key, "test")

    @mock.patch(
        "tethys_portal.settings.yaml.safe_load",
        return_value={"settings": {"OAUTH_CONFIG": {"test_oauth_key": "test"}}},
    )
    def test_oauth_config(self, _):
        reload(settings)
        self.assertEqual(settings.test_oauth_key, "test")

    @mock.patch(
        "tethys_portal.settings.yaml.safe_load",
        return_value={"settings": {"CAPTCHA_CONFIG": {"test_captcha": "test"}}},
    )
    def test_captcha_config(self, _):
        reload(settings)
        self.assertEqual(settings.test_captcha, "test")

    @mock.patch(
        "tethys_portal.settings.yaml.safe_load",
        return_value={"settings": {"ANALYTICS_CONFIG": {"test_analytic": "test"}}},
    )
    def test_analytics_config(self, _):
        reload(settings)
        self.assertEqual(settings.test_analytic, "test")

    @mock.patch(
        "tethys_portal.settings.yaml.safe_load",
        return_value={"settings": {"MFA_CONFIG": {"MFA_REQUIRED": True}}},
    )
    def test_mfa_config(self, _):
        reload(settings)
        self.assertEqual(settings.MFA_REQUIRED, True)

    @mock.patch(
        "tethys_portal.settings.yaml.safe_load",
        return_value={"settings": {"LOCKOUT_CONFIG": {"AXES_COOLOFF_TIME": 1}}},
    )
    def test_lockout_config__cooloff_int(self, _):
        reload(settings)
        self.assertEqual(settings.AXES_COOLOFF_TIME, 1)

    @mock.patch(
        "tethys_portal.settings.yaml.safe_load",
        return_value={"settings": {"LOCKOUT_CONFIG": {"AXES_COOLOFF_TIME": "PT45M"}}},
    )
    def test_lockout_config__cooloff_iso_str(self, _):
        reload(settings)
        self.assertEqual(settings.AXES_COOLOFF_TIME, dt.timedelta(minutes=45))

    @mock.patch(
        "tethys_portal.settings.yaml.safe_load",
        return_value={"settings": {"LOCKOUT_CONFIG": {"AXES_COOLOFF_TIME": "foo"}}},
    )
    def test_lockout_config__cooloff_bad_str(self, _):
        reload(settings)
        self.assertEqual(settings.AXES_COOLOFF_TIME, "foo")

    @mock.patch(
        "tethys_portal.settings.yaml.safe_load",
        return_value={
            "settings": {"SESSION_CONFIG": {"SESSION_EXPIRES_AT_BROWSER_CLOSE": True}}
        },
    )
    def test_session_config(self, _):
        reload(settings)
        self.assertEqual(settings.SESSION_EXPIRES_AT_BROWSER_CLOSE, True)

    @mock.patch(
        "tethys_portal.settings.yaml.safe_load",
        return_value={"settings": {"TEST_SETTING": "test"}},
    )
    def test_other_settings(self, _):
        reload(settings)
        self.assertEqual(settings.test_oauth_key, "test")

    @mock.patch(
        "tethys_portal.settings.yaml.safe_load",
        return_value={
            "settings": {"TETHYS_PORTAL_CONFIG": {"STATICFILES_USE_NPM": True}}
        },
    )
    def test_staticfiles_use_npm__enabled(self, _):
        reload(settings)
        self.assertTrue(settings.STATICFILES_USE_NPM)
        node_modules_in_any_paths = any(
            ["node_modules" in str(path) for path in settings.STATICFILES_DIRS]
        )
        self.assertTrue(node_modules_in_any_paths)

    @mock.patch(
        "tethys_portal.settings.yaml.safe_load",
        return_value={
            "settings": {"TETHYS_PORTAL_CONFIG": {"STATICFILES_USE_NPM": False}}
        },
    )
    def test_staticfiles_use_npm__disabled(self, _):
        reload(settings)
        self.assertFalse(settings.STATICFILES_USE_NPM)
        node_modules_in_any_paths = any(
            ["node_modules" in str(path) for path in settings.STATICFILES_DIRS]
        )
        self.assertFalse(node_modules_in_any_paths)

    @mock.patch(
        "tethys_portal.settings.yaml.safe_load",
        return_value={
            "settings": {"COOKIE_CONFIG": {"CSRF_COOKIE_SAMESITE": "Strict"}}
        },
    )
    def test_cookie_config(self, _):
        reload(settings)
        self.assertEqual(settings.CSRF_COOKIE_SAMESITE, "Strict")

    @mock.patch(
        "tethys_portal.settings.yaml.safe_load",
        return_value={
            "settings": {
                "CORS_CONFIG": {"CORS_ALLOWED_ORIGINS": ["http://example.com"]}
            }
        },
    )
    def test_cors_config(self, _):
        reload(settings)
        self.assertListEqual(settings.CORS_ALLOWED_ORIGINS, ["http://example.com"])

    @mock.patch("tethys_portal.optional_dependencies.has_module", return_value=False)
    @mock.patch(
        "tethys_portal.settings.yaml.safe_load",
        return_value={"settings": {}},
    )
    @mock.patch("tethys_apps.utilities.relative_to_tethys_home")
    def test_db_config_default(self, mock_home, _, __):
        name = mock.MagicMock()
        name.exists.return_value = False
        mock_home.return_value = name
        reload(settings)
        self.assertDictEqual(
            settings.DATABASES["default"],
            {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": name,
            },
        )

    @mock.patch("tethys_portal.optional_dependencies.has_module", return_value=False)
    @mock.patch(
        "tethys_portal.settings.yaml.safe_load",
        return_value={
            "settings": {
                "DATABASES": {"default": {"ENGINE": "django.db.backends.postgresql"}}
            }
        },
    )
    def test_db_config_postgres(self, _, __):
        reload(settings)
        self.assertDictEqual(
            settings.DATABASES["default"],
            {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": "tethys_platform",
                "USER": "tethys_default",
                "PASSWORD": "pass",
                "HOST": "localhost",
                "PORT": 5436,
            },
        )

    @mock.patch(
        "tethys_portal.settings.yaml.safe_load",
        return_value={
            "settings": {
                "DATABASES": {
                    "default": {"ENGINE": "django_tenants.postgresql_backend"}
                }
            }
        },
    )
    def test_db_config_tenants_postgres(self, _):
        reload(settings)
        self.assertDictEqual(
            settings.DATABASES["default"],
            {
                "ENGINE": "django_tenants.postgresql_backend",
                "NAME": "tethys_platform",
                "USER": "tethys_default",
                "PASSWORD": "pass",
                "HOST": "localhost",
                "PORT": 5436,
            },
        )

    # TODO remove compatibility code tests with Tethys5.0 (or 4.2?)
    @mock.patch(
        "tethys_portal.settings.yaml.safe_load",
        return_value={"settings": {"DATABASES": {"default": {"DIR": "test"}}}},
    )
    @mock.patch("tethys_utils.deprecation_warning")
    def test_deprecated_postgres_db_config(self, mock_warning, _):
        reload(settings)
        mock_warning.assert_called_once()

    @mock.patch(
        "tethys_portal.settings.yaml.safe_load",
        return_value={"settings": {}},
    )
    @mock.patch("tethys_utils.deprecation_warning")
    @mock.patch("tethys_apps.utilities.relative_to_tethys_home")
    def test_deprecated_no_config_existing_db(self, mock_home, mock_warning, _):
        mock_home().exists.return_value = True
        reload(settings)
        mock_warning.assert_called_once()
        self.assertEqual(mock_home.call_args_list[2].args[0], "psql")

    @mock.patch(
        "tethys_portal.settings.yaml.safe_load",
        return_value={
            "settings": {
                "PREFIX_URL": "test",
            }
        },
    )
    def test_prefix_to_path_settings(self, _):
        reload(settings)
        self.assertEqual(settings.PREFIX_URL, "test")
        self.assertEqual(settings.STATIC_URL, "/test/static/")
        self.assertEqual(settings.LOGIN_URL, "/test/accounts/login/")

    @mock.patch("tethys_portal.optional_dependencies.has_module", return_value=True)
    def test_bokeh_django_staticfiles_finder(self, _):
        reload(settings)
        self.assertIn(
            "bokeh_django.static.BokehExtensionFinder", settings.STATICFILES_FINDERS
        )

    @mock.patch(
        "tethys_portal.settings.yaml.safe_load",
        return_value={
            "settings": {"TETHYS_PORTAL_CONFIG": {"MULTIPLE_APP_MODE": False}}
        },
    )
    def test_portal_config_settings_standalone_app(self, _):
        reload(settings)

        self.assertTrue(settings.STANDALONE_APP is None)
        self.assertTrue(settings.BYPASS_TETHYS_HOME_PAGE)

    @mock.patch("tethys_portal.optional_dependencies.optional_import")
    def test_bokehjsdir_compatibility(self, mock_oi):
        mock_bokeh_settings = mock.MagicMock()
        mock_oi.return_value = mock_bokeh_settings
        mock_bokeh_settings.bokehjs_path.side_effect = AttributeError()
        reload(settings)
        mock_bokeh_settings.bokehjs_path.assert_called_once()
        mock_bokeh_settings.bokehjsdir.assert_called_once()

    def test_get__all__(self):
        expected = "__all__"
        mock_mod = mock.MagicMock(__all__=expected)
        actual = settings.get__all__(mock_mod)
        self.assertEqual(expected, actual)

    def test_get__all__error(self):
        mock_mod = mock.MagicMock()
        actual = settings.get__all__(mock_mod)
        expected = [a for a in dir(mock_mod) if not a.startswith("__")]
        self.assertListEqual(expected, actual)

    @mock.patch(
        "tethys_portal.settings.yaml.safe_load",
        return_value={
            "settings": {
                "TETHYS_PORTAL_CONFIG": {
                    "ADDITIONAL_SETTINGS_FILES": [
                        "tethysapp.test_app.additional_settings"
                    ]
                }
            }
        },
    )
    def test_additional_settings_files(self, _):
        reload(settings)
        self.assertEqual(settings.TEST_SETTING, "Test Setting")
