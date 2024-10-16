from unittest import mock
from django.test import override_settings


from django.urls import reverse, resolve
from tethys_sdk.testing import TethysTestCase


class TestUrls(TethysTestCase):
    def set_up(self):
        pass

    def tear_down(self):
        pass

    def test_account_urls_account_login(self):
        url = reverse("accounts:login")
        resolver = resolve(url)
        self.assertEqual("/accounts/login/", url)
        self.assertEqual("tethys_portal.views.accounts.login_view", resolver._func_path)

    def test_account_urls_accounts_logout(self):
        url = reverse("accounts:logout")
        resolver = resolve(url)
        self.assertEqual("/accounts/logout/", url)
        self.assertEqual(
            "tethys_portal.views.accounts.logout_view", resolver._func_path
        )

    def test_account_urls_accounts_register(self):
        url = reverse("accounts:register")
        resolver = resolve(url)
        self.assertEqual("/accounts/register/", url)
        self.assertEqual("tethys_portal.views.accounts.register", resolver._func_path)

    def test_account_urls_accounts_password_reset(self):
        url = reverse("accounts:password_reset")
        resolver = resolve(url)
        self.assertEqual("/accounts/password/reset/", url)
        self.assertEqual(
            "tethys_portal.views.email.TethysPasswordResetView", resolver._func_path
        )

    def test_account_urls_accounts_password_reset_done(self):
        url = reverse("accounts:password_reset_done")
        resolver = resolve(url)
        self.assertEqual("/accounts/password/reset/done/", url)
        self.assertEqual(
            "django.contrib.auth.views.PasswordResetDoneView", resolver._func_path
        )

    def test_account_urls_accounts_password_confirm(self):
        url = reverse(
            "accounts:password_confirm", kwargs={"uidb64": "f00Bar", "token": "tok"}
        )
        resolver = resolve(url)
        self.assertEqual("/accounts/password/reset/f00Bar-tok/", url)
        self.assertEqual(
            "django.contrib.auth.views.PasswordResetConfirmView", resolver._func_path
        )

    def test_account_urls_accounts_password_done(self):
        url = reverse("accounts:password_done")
        resolver = resolve(url)
        self.assertEqual("/accounts/password/done/", url)
        self.assertEqual(
            "django.contrib.auth.views.PasswordResetCompleteView", resolver._func_path
        )

    def test_oauth2_urls_login(self):
        url = reverse("social:begin", kwargs={"backend": "foo"})
        resolver = resolve(url)
        self.assertEqual("/oauth2/login/foo/", url)
        self.assertEqual("tethys_portal.views.psa.auth", resolver._func_path)

    def test_oauth2_urls_complete(self):
        url = reverse("social:complete", kwargs={"backend": "foo"})
        resolver = resolve(url)
        self.assertEqual("/oauth2/complete/foo/", url)
        self.assertEqual("tethys_portal.views.psa.complete", resolver._func_path)

    def test_oauth2_urls_disconnect(self):
        url = reverse("social:disconnect", kwargs={"backend": "foo"})
        resolver = resolve(url)
        self.assertEqual("/oauth2/disconnect/foo/", url)
        self.assertEqual("social_django.views.disconnect", resolver._func_path)

    def test_oauth2_urls_disconnect_individual(self):
        url = reverse(
            "social:disconnect_individual",
            kwargs={"backend": "foo", "association_id": "123"},
        )
        resolver = resolve(url)
        self.assertEqual("/oauth2/disconnect/foo/123/", url)
        self.assertEqual("social_django.views.disconnect", resolver._func_path)

    def test_oauth2_urls_tenant(self):
        url = reverse("social:tenant", kwargs={"backend": "foo"})
        resolver = resolve(url)
        self.assertEqual("/oauth2/tenant/foo/", url)
        self.assertEqual("tethys_portal.views.psa.tenant", resolver._func_path)

    def test_user_urls_profile(self):
        url = reverse("user:profile")
        resolver = resolve(url)

        self.assertEqual("/user/", url)
        self.assertEqual("tethys_portal.views.user.profile", resolver._func_path)

    def test_user_urls_settings(self):
        url = reverse("user:settings")
        resolver = resolve(url)
        self.assertEqual("/user/settings/", url)
        self.assertEqual("tethys_portal.views.user.settings", resolver._func_path)

    def test_user_urls_change_password(self):
        url = reverse("user:change_password")
        resolver = resolve(url)
        self.assertEqual("/user/change-password/", url)
        self.assertEqual(
            "tethys_portal.views.user.change_password", resolver._func_path
        )

    def test_user_urls_disconnect(self):
        url = reverse("user:change_password")
        resolver = resolve(url)
        self.assertEqual("/user/change-password/", url)
        self.assertEqual(
            "tethys_portal.views.user.change_password", resolver._func_path
        )

    def test_user_urls_delete(self):
        url = reverse("user:delete")
        resolver = resolve(url)
        self.assertEqual("/user/delete-account/", url)
        self.assertEqual("tethys_portal.views.user.delete_account", resolver._func_path)

    def test_urlpatterns_handoff_capabilities(self):
        url = reverse("handoff_capabilities", kwargs={"app_name": "foo"})
        resolver = resolve(url)
        self.assertEqual("/handoff/foo/", url)
        self.assertEqual("tethys_apps.views.handoff_capabilities", resolver._func_path)

    def test_urlpatterns_handoff(self):
        url = reverse("handoff", kwargs={"app_name": "foo", "handler_name": "Bar"})
        resolver = resolve(url)
        self.assertEqual("/handoff/foo/Bar/", url)
        self.assertEqual("tethys_apps.views.handoff", resolver._func_path)

    def test_urlpatterns_update_job_status(self):
        url = reverse("update_job_status", kwargs={"job_id": "JI001"})
        resolver = resolve(url)
        self.assertEqual("/update-job-status/JI001/", url)
        self.assertEqual(
            "tethys_compute.views.update_status.update_job_status", resolver._func_path
        )

    def test_urlpatterns_update_dask_job_status(self):
        url = reverse("update_dask_job_status", kwargs={"key": "123456789"})
        resolver = resolve(url)
        self.assertEqual("/update-dask-job-status/123456789/", url)
        self.assertEqual(
            "tethys_compute.views.update_status.update_dask_job_status",
            resolver._func_path,
        )

    @override_settings(REGISTER_CONTROLLER="test")
    @mock.patch("django.urls.re_path")
    @mock.patch("tethys_apps.base.function_extractor.TethysFunctionExtractor")
    def test_custom_register_controller(self, mock_func_extractor, _):
        import tethys_portal.urls
        from importlib import reload

        reload(tethys_portal.urls)
        self.assertEqual(tethys_portal.urls.register_controller_setting, "test")
        mock_func_extractor.assert_called_once()

    @override_settings(REGISTER_CONTROLLER="test")
    @mock.patch("django.urls.re_path")
    @mock.patch("tethys_apps.base.function_extractor.TethysFunctionExtractor")
    def test_custom_register_controller_not_class_based_view(
        self, mock_func_extractor, _
    ):
        import tethys_portal.urls
        from importlib import reload

        mock_controller = mock.MagicMock()
        mock_controller.as_controller.side_effect = AttributeError
        mock_func_extractor.return_value = mock.MagicMock(function=mock_controller)

        reload(tethys_portal.urls)
        self.assertEqual(tethys_portal.urls.register_controller_setting, "test")
        self.assertEqual(tethys_portal.urls.register_controller, mock_controller)
        mock_func_extractor.assert_called_once()


@override_settings(PREFIX_URL="test/prefix")
@override_settings(LOGIN_URL="/test/prefix/test/login/")
class TestUrlsWithPrefix(TethysTestCase):
    import sys
    from importlib import reload, import_module
    from django.conf import settings
    from django.urls import clear_url_caches

    @classmethod
    def reload_urlconf(self, urlconf=None):
        self.clear_url_caches()
        if urlconf is None:
            urlconf = self.settings.ROOT_URLCONF
        if urlconf in self.sys.modules:
            self.reload(self.sys.modules[urlconf])
        else:
            self.import_module(urlconf)

    def set_up(self):
        self.reload_urlconf()
        pass

    @override_settings(PREFIX_URL="/")
    def tearDown(self):
        self.reload_urlconf()
        pass

    def test_account_urls_account_login(self):
        url = reverse("accounts:login")
        resolver = resolve(url)
        self.assertEqual("/test/prefix/accounts/login/", url)
        self.assertEqual("tethys_portal.views.accounts.login_view", resolver._func_path)

    def test_admin_urls_account_login(self):
        url = reverse("login_prefix")
        resolver = resolve(url)
        self.assertEqual("/test/prefix/test/login/", url)
        self.assertEqual("tethys_portal.views.accounts.login_view", resolver._func_path)

    def test_account_urls_accounts_logout(self):
        url = reverse("accounts:logout")
        resolver = resolve(url)
        self.assertEqual("/test/prefix/accounts/logout/", url)
        self.assertEqual(
            "tethys_portal.views.accounts.logout_view", resolver._func_path
        )

    def test_account_urls_accounts_register(self):
        url = reverse("accounts:register")
        resolver = resolve(url)
        self.assertEqual("/test/prefix/accounts/register/", url)
        self.assertEqual("tethys_portal.views.accounts.register", resolver._func_path)

    def test_account_urls_accounts_password_reset(self):
        url = reverse("accounts:password_reset")
        resolver = resolve(url)
        self.assertEqual("/test/prefix/accounts/password/reset/", url)
        self.assertEqual(
            "tethys_portal.views.email.TethysPasswordResetView", resolver._func_path
        )

    def test_account_urls_accounts_password_reset_done(self):
        url = reverse("accounts:password_reset_done")
        resolver = resolve(url)
        self.assertEqual("/test/prefix/accounts/password/reset/done/", url)
        self.assertEqual(
            "django.contrib.auth.views.PasswordResetDoneView", resolver._func_path
        )

    def test_account_urls_accounts_password_confirm(self):
        url = reverse(
            "accounts:password_confirm", kwargs={"uidb64": "f00Bar", "token": "tok"}
        )
        resolver = resolve(url)
        self.assertEqual("/test/prefix/accounts/password/reset/f00Bar-tok/", url)
        self.assertEqual(
            "django.contrib.auth.views.PasswordResetConfirmView", resolver._func_path
        )

    def test_account_urls_accounts_password_done(self):
        url = reverse("accounts:password_done")
        resolver = resolve(url)
        self.assertEqual("/test/prefix/accounts/password/done/", url)
        self.assertEqual(
            "django.contrib.auth.views.PasswordResetCompleteView", resolver._func_path
        )

    def test_oauth2_urls_login(self):
        url = reverse("social:begin", kwargs={"backend": "foo"})
        resolver = resolve(url)
        self.assertEqual("/test/prefix/oauth2/login/foo/", url)
        self.assertEqual("tethys_portal.views.psa.auth", resolver._func_path)

    def test_oauth2_urls_complete(self):
        url = reverse("social:complete", kwargs={"backend": "foo"})
        resolver = resolve(url)
        self.assertEqual("/test/prefix/oauth2/complete/foo/", url)
        self.assertEqual("tethys_portal.views.psa.complete", resolver._func_path)

    def test_oauth2_urls_disconnect(self):
        url = reverse("social:disconnect", kwargs={"backend": "foo"})
        resolver = resolve(url)
        self.assertEqual("/test/prefix/oauth2/disconnect/foo/", url)
        self.assertEqual("social_django.views.disconnect", resolver._func_path)

    def test_oauth2_urls_disconnect_individual(self):
        url = reverse(
            "social:disconnect_individual",
            kwargs={"backend": "foo", "association_id": "123"},
        )
        resolver = resolve(url)
        self.assertEqual("/test/prefix/oauth2/disconnect/foo/123/", url)
        self.assertEqual("social_django.views.disconnect", resolver._func_path)

    def test_oauth2_urls_tenant(self):
        url = reverse("social:tenant", kwargs={"backend": "foo"})
        resolver = resolve(url)
        self.assertEqual("/test/prefix/oauth2/tenant/foo/", url)
        self.assertEqual("tethys_portal.views.psa.tenant", resolver._func_path)

    def test_user_urls_profile(self):
        url = reverse("user:profile")
        resolver = resolve(url)

        self.assertEqual("/test/prefix/user/", url)
        self.assertEqual("tethys_portal.views.user.profile", resolver._func_path)

    def test_user_urls_settings(self):
        url = reverse("user:settings")
        resolver = resolve(url)
        self.assertEqual("/test/prefix/user/settings/", url)
        self.assertEqual("tethys_portal.views.user.settings", resolver._func_path)

    def test_user_urls_change_password(self):
        url = reverse("user:change_password")
        resolver = resolve(url)
        self.assertEqual("/test/prefix/user/change-password/", url)
        self.assertEqual(
            "tethys_portal.views.user.change_password", resolver._func_path
        )

    def test_user_urls_disconnect(self):
        url = reverse("user:change_password")
        resolver = resolve(url)
        self.assertEqual("/test/prefix/user/change-password/", url)
        self.assertEqual(
            "tethys_portal.views.user.change_password", resolver._func_path
        )

    def test_user_urls_delete(self):
        url = reverse("user:delete")
        resolver = resolve(url)
        self.assertEqual("/test/prefix/user/delete-account/", url)
        self.assertEqual("tethys_portal.views.user.delete_account", resolver._func_path)

    def test_urlpatterns_handoff_capabilities(self):
        url = reverse("handoff_capabilities", kwargs={"app_name": "foo"})
        resolver = resolve(url)
        self.assertEqual("/test/prefix/handoff/foo/", url)
        self.assertEqual("tethys_apps.views.handoff_capabilities", resolver._func_path)

    def test_urlpatterns_handoff(self):
        url = reverse("handoff", kwargs={"app_name": "foo", "handler_name": "Bar"})
        resolver = resolve(url)
        self.assertEqual("/test/prefix/handoff/foo/Bar/", url)
        self.assertEqual("tethys_apps.views.handoff", resolver._func_path)

    def test_urlpatterns_update_job_status(self):
        url = reverse("update_job_status", kwargs={"job_id": "JI001"})
        resolver = resolve(url)
        self.assertEqual("/test/prefix/update-job-status/JI001/", url)
        self.assertEqual(
            "tethys_compute.views.update_status.update_job_status", resolver._func_path
        )

    def test_urlpatterns_update_dask_job_status(self):
        url = reverse("update_dask_job_status", kwargs={"key": "123456789"})
        resolver = resolve(url)
        self.assertEqual("/test/prefix/update-dask-job-status/123456789/", url)
        self.assertEqual(
            "tethys_compute.views.update_status.update_dask_job_status",
            resolver._func_path,
        )

    @override_settings(REGISTER_CONTROLLER="test")
    @mock.patch("django.urls.re_path")
    @mock.patch("tethys_apps.base.function_extractor.TethysFunctionExtractor")
    def test_custom_register_controller(self, mock_func_extractor, _):
        import tethys_portal.urls
        from importlib import reload

        reload(tethys_portal.urls)
        self.assertEqual(tethys_portal.urls.register_controller_setting, "test")
        mock_func_extractor.assert_called_once()

    @override_settings(REGISTER_CONTROLLER="test")
    @mock.patch("django.urls.re_path")
    @mock.patch("tethys_apps.base.function_extractor.TethysFunctionExtractor")
    def test_custom_register_controller_not_class_based_view(
        self, mock_func_extractor, _
    ):
        import tethys_portal.urls
        from importlib import reload

        mock_controller = mock.MagicMock()
        mock_controller.as_controller.side_effect = AttributeError
        mock_func_extractor.return_value = mock.MagicMock(function=mock_controller)

        reload(tethys_portal.urls)
        self.assertEqual(tethys_portal.urls.register_controller_setting, "test")
        self.assertEqual(tethys_portal.urls.register_controller, mock_controller)
        mock_func_extractor.assert_called_once()

    @override_settings(
        ADDITIONAL_URLPATTERNS=["my.test.urlpatterns"],
        PREFIX_URL=None,
        LOGIN_URL=None,
    )
    @mock.patch(
        "importlib.import_module", return_value=mock.MagicMock(urlpatterns=["re_path"])
    )
    def test_additional_urls(
        self,
        mock_import_module,
    ):
        import tethys_portal.urls
        from importlib import reload

        reload(tethys_portal.urls)
        mock_import_module.assert_called_with("my.test")
        self.assertEqual(tethys_portal.urls.additional_url_patterns, ["re_path"])
        self.assertEqual(tethys_portal.urls.urlpatterns[0], "re_path")

    @override_settings(ADDITIONAL_URLPATTERNS=["my.test.urlpatterns"])
    @mock.patch("tethys_portal.urls.logging.getLogger")
    def test_additional_urls_exception(
        self,
        mock_logger,
    ):
        import tethys_portal.urls
        from importlib import reload

        reload(tethys_portal.urls)
        self.assertEqual(mock_logger().exception.call_count, 2)
