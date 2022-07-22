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
        url = reverse('accounts:login')
        resolver = resolve(url)
        self.assertEqual('/accounts/login/', url)
        self.assertEqual('login_view', resolver.func.__name__)
        self.assertEqual('tethys_portal.views.accounts', resolver.func.__module__)

    def test_account_urls_accounts_logout(self):
        url = reverse('accounts:logout')
        resolver = resolve(url)
        self.assertEqual('/accounts/logout/', url)
        self.assertEqual('logout_view', resolver.func.__name__)
        self.assertEqual('tethys_portal.views.accounts', resolver.func.__module__)

    def test_account_urls_accounts_register(self):
        url = reverse('accounts:register')
        resolver = resolve(url)
        self.assertEqual('/accounts/register/', url)
        self.assertEqual('register', resolver.func.__name__)
        self.assertEqual('tethys_portal.views.accounts', resolver.func.__module__)

    def test_account_urls_accounts_password_reset(self):
        url = reverse('accounts:password_reset')
        resolver = resolve(url)
        self.assertEqual('/accounts/password/reset/', url)
        self.assertEqual('TethysPasswordResetView', resolver.func.__name__)
        self.assertEqual('tethys_portal.views.email', resolver.func.__module__)

    def test_account_urls_accounts_password_reset_done(self):
        url = reverse('accounts:password_reset_done')
        resolver = resolve(url)
        self.assertEqual('/accounts/password/reset/done/', url)
        self.assertEqual('PasswordResetDoneView', resolver.func.__name__)
        self.assertEqual('django.contrib.auth.views', resolver.func.__module__)

    def test_account_urls_accounts_password_confirm(self):
        url = reverse('accounts:password_confirm', kwargs={'uidb64': 'f00Bar', 'token': 'tok'})
        resolver = resolve(url)
        self.assertEqual('/accounts/password/reset/f00Bar-tok/', url)
        self.assertEqual('PasswordResetConfirmView', resolver.func.__name__)
        self.assertEqual('django.contrib.auth.views', resolver.func.__module__)

    def test_account_urls_accounts_password_done(self):
        url = reverse('accounts:password_done')
        resolver = resolve(url)
        self.assertEqual('/accounts/password/done/', url)
        self.assertEqual('PasswordResetCompleteView', resolver.func.__name__)
        self.assertEqual('django.contrib.auth.views', resolver.func.__module__)

    def test_oauth2_urls_login(self):
        url = reverse('social:begin', kwargs={'backend': 'foo'})
        resolver = resolve(url)
        self.assertEqual('/oauth2/login/foo/', url)
        self.assertEqual('auth', resolver.func.__name__)
        self.assertEqual('tethys_portal.views.psa', resolver.func.__module__)

    def test_oauth2_urls_complete(self):
        url = reverse('social:complete', kwargs={'backend': 'foo'})
        resolver = resolve(url)
        self.assertEqual('/oauth2/complete/foo/', url)
        self.assertEqual('complete', resolver.func.__name__)
        self.assertEqual('tethys_portal.views.psa', resolver.func.__module__)

    def test_oauth2_urls_disconnect(self):
        url = reverse('social:disconnect', kwargs={'backend': 'foo'})
        resolver = resolve(url)
        self.assertEqual('/oauth2/disconnect/foo/', url)
        self.assertEqual('disconnect', resolver.func.__name__)
        self.assertEqual('social_django.views', resolver.func.__module__)

    def test_oauth2_urls_disconnect_individual(self):
        url = reverse('social:disconnect_individual', kwargs={'backend': 'foo', 'association_id': '123'})
        resolver = resolve(url)
        self.assertEqual('/oauth2/disconnect/foo/123/', url)
        self.assertEqual('disconnect', resolver.func.__name__)
        self.assertEqual('social_django.views', resolver.func.__module__)

    def test_oauth2_urls_tenant(self):
        url = reverse('social:tenant', kwargs={'backend': 'foo'})
        resolver = resolve(url)
        self.assertEqual('/oauth2/tenant/foo/', url)
        self.assertEqual('tenant', resolver.func.__name__)
        self.assertEqual('tethys_portal.views.psa', resolver.func.__module__)

    def test_user_urls_profile(self):
        url = reverse('user:profile')
        resolver = resolve(url)

        self.assertEqual('/user/', url)
        self.assertEqual('profile', resolver.func.__name__)
        self.assertEqual('tethys_portal.views.user', resolver.func.__module__)

    def test_user_urls_settings(self):
        url = reverse('user:settings')
        resolver = resolve(url)
        self.assertEqual('/user/settings/', url)
        self.assertEqual('settings', resolver.func.__name__)
        self.assertEqual('tethys_portal.views.user', resolver.func.__module__)

    def test_user_urls_change_password(self):
        url = reverse('user:change_password')
        resolver = resolve(url)
        self.assertEqual('/user/change-password/', url)
        self.assertEqual('change_password', resolver.func.__name__)
        self.assertEqual('tethys_portal.views.user', resolver.func.__module__)

    def test_user_urls_disconnect(self):
        url = reverse('user:change_password')
        resolver = resolve(url)
        self.assertEqual('/user/change-password/', url)
        self.assertEqual('change_password', resolver.func.__name__)
        self.assertEqual('tethys_portal.views.user', resolver.func.__module__)

    def test_user_urls_delete(self):
        url = reverse('user:delete')
        resolver = resolve(url)
        self.assertEqual('/user/delete-account/', url)
        self.assertEqual('delete_account', resolver.func.__name__)
        self.assertEqual('tethys_portal.views.user', resolver.func.__module__)

    def test_urlpatterns_handoff_capabilities(self):
        url = reverse('handoff_capabilities', kwargs={'app_name': 'foo'})
        resolver = resolve(url)
        self.assertEqual('/handoff/foo/', url)
        self.assertEqual('handoff_capabilities', resolver.func.__name__)
        self.assertEqual('tethys_apps.views', resolver.func.__module__)

    def test_urlpatterns_handoff(self):
        url = reverse('handoff', kwargs={'app_name': 'foo', 'handler_name': 'Bar'})
        resolver = resolve(url)
        self.assertEqual('/handoff/foo/Bar/', url)
        self.assertEqual('handoff', resolver.func.__name__)
        self.assertEqual('tethys_apps.views', resolver.func.__module__)

    def test_urlpatterns_update_job_status(self):
        url = reverse('update_job_status', kwargs={'job_id': 'JI001'})
        resolver = resolve(url)
        self.assertEqual('/update-job-status/JI001/', url)
        self.assertEqual('update_job_status', resolver.func.__name__)
        self.assertEqual('tethys_apps.views', resolver.func.__module__)

    def test_urlpatterns_update_dask_job_status(self):
        url = reverse('update_dask_job_status', kwargs={'key': '123456789'})
        resolver = resolve(url)
        self.assertEqual('/update-dask-job-status/123456789/', url)
        self.assertEqual('update_dask_job_status', resolver.func.__name__)
        self.assertEqual('tethys_apps.views', resolver.func.__module__)

    @override_settings(REGISTER_CONTROLLER='test')
    @mock.patch('django.urls.re_path')
    @mock.patch('tethys_apps.base.function_extractor.TethysFunctionExtractor')
    def test_custom_register_controller(self, mock_func_extractor, _):
        import tethys_portal.urls
        from importlib import reload

        reload(tethys_portal.urls)
        self.assertEqual(tethys_portal.urls.register_controller_setting, 'test')
        mock_func_extractor.assert_called_once()

    @override_settings(REGISTER_CONTROLLER='test')
    @mock.patch('django.urls.re_path')
    @mock.patch('tethys_apps.base.function_extractor.TethysFunctionExtractor')
    def test_custom_register_controller_not_class_based_view(self, mock_func_extractor, _):
        import tethys_portal.urls
        from importlib import reload

        mock_controller = mock.MagicMock()
        mock_controller.as_controller.side_effect = AttributeError
        mock_func_extractor.return_value = mock.MagicMock(function=mock_controller)

        reload(tethys_portal.urls)
        self.assertEqual(tethys_portal.urls.register_controller_setting, 'test')
        self.assertEqual(tethys_portal.urls.register_controller, mock_controller)
        mock_func_extractor.assert_called_once()
