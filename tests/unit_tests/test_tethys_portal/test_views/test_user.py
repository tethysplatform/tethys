import unittest
from unittest import mock
from django.test import override_settings
from django.contrib.auth.models import User

# Fixes the Cache-Control error in tests. Must appear before view imports.
mock.patch('django.views.decorators.cache.never_cache', lambda x: x).start()

from tethys_portal.views.user import profile, settings, change_password, social_disconnect, delete_account, \
    manage_storage, clear_workspace  # noqa: E402
from tethys_apps.models import TethysApp  # noqa: E402


class TethysPortalUserTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @override_settings(MFA_REQUIRED=False)
    @mock.patch('tethys_quotas.utilities.log')
    @mock.patch('tethys_portal.views.user.has_mfa')
    @mock.patch('tethys_portal.views.user._convert_storage_units')
    @mock.patch('tethys_portal.views.user.get_quota')
    @mock.patch('tethys_portal.views.user.render')
    @mock.patch('tethys_portal.views.user.Token.objects.get_or_create')
    @mock.patch('tethys_portal.views.user.User.objects.get')
    def test_profile(self, mock_get_user, mock_token_get_create, mock_render, mock_get_quota, mock_convert_units,
                     mock_has_mfa, _):
        mock_request = mock.MagicMock()

        mock_user_token = mock.MagicMock()
        mock_token_created = mock.MagicMock()
        mock_token_get_create.return_value = mock_user_token, mock_token_created
        mock_convert_units.return_value = '0 bytes'
        mock_get_quota.return_value = {'quota': None}
        mock_has_mfa.return_value = False

        expected_context = {
            'user_token': mock_user_token.key,
            'current_use': '0 bytes',
            'quota': None,
            'has_mfa': False,
            'mfa_required': False,
            'show_user_token_mfa': True
        }

        profile(mock_request)

        mock_render.assert_called_with(mock_request, 'tethys_portal/user/profile.html', expected_context)

    @override_settings(MFA_REQUIRED=False)
    @mock.patch('tethys_quotas.utilities.log')
    @mock.patch('tethys_portal.views.user.has_mfa')
    @mock.patch('tethys_portal.views.user._convert_storage_units')
    @mock.patch('tethys_portal.views.user.get_quota')
    @mock.patch('tethys_portal.views.user.render')
    @mock.patch('tethys_portal.views.user.Token.objects.get_or_create')
    def test_profile_quota(self, mock_token_get_create, mock_render, mock_get_quota,
                           mock_convert_units, mock_has_mfa, _):
        mock_request = mock.MagicMock()
        mock_user = mock.MagicMock()
        mock_request.user = mock_user

        mock_user_token = mock.MagicMock()
        mock_token_created = mock.MagicMock()
        mock_token_get_create.return_value = mock_user_token, mock_token_created
        mock_convert_units.return_value = '0 bytes'
        mock_get_quota.return_value = {'quota': 1, 'units': 0}
        mock_has_mfa.return_value = False

        expected_context = {
            'user_token': mock_user_token.key,
            'current_use': '0 bytes',
            'quota': '0 bytes',
            'has_mfa': False,
            'mfa_required': False,
            'show_user_token_mfa': True  # Show user token b/c mfa is not required
        }

        profile(mock_request)

        mock_render.assert_called_with(mock_request, 'tethys_portal/user/profile.html', expected_context)

        mock_token_get_create.assert_called_with(user=mock_user)

    @override_settings(MFA_REQUIRED=True)
    @mock.patch('tethys_quotas.utilities.log')
    @mock.patch('tethys_portal.views.user.has_mfa')
    @mock.patch('tethys_portal.views.user._convert_storage_units')
    @mock.patch('tethys_portal.views.user.get_quota')
    @mock.patch('tethys_portal.views.user.render')
    @mock.patch('tethys_portal.views.user.Token.objects.get_or_create')
    @mock.patch('tethys_portal.views.user.User.objects.get')
    def test_profile_mfa_required_no_mfa_set(self, mock_get_user, mock_token_get_create, mock_render, mock_get_quota,
                                             mock_convert_units, mock_has_mfa, _):
        mock_request = mock.MagicMock()
        mock_user = mock.MagicMock()
        mock_get_user.return_value = mock_user

        mock_user_token = mock.MagicMock()
        mock_token_created = mock.MagicMock()
        mock_token_get_create.return_value = mock_user_token, mock_token_created
        mock_convert_units.return_value = '0 bytes'
        mock_get_quota.return_value = {'quota': None}
        mock_has_mfa.return_value = False

        expected_context = {
            'user_token': mock_user_token.key,
            'current_use': '0 bytes',
            'quota': None,
            'has_mfa': False,
            'mfa_required': True,
            'show_user_token_mfa': False  # Don't show user token b/c mfa is required but user has not setup mfa
        }

        profile(mock_request)

        mock_render.assert_called_with(mock_request, 'tethys_portal/user/profile.html', expected_context)

    @override_settings(MFA_REQUIRED=True)
    @mock.patch('tethys_quotas.utilities.log')
    @mock.patch('tethys_portal.views.user.has_mfa')
    @mock.patch('tethys_portal.views.user._convert_storage_units')
    @mock.patch('tethys_portal.views.user.get_quota')
    @mock.patch('tethys_portal.views.user.render')
    @mock.patch('tethys_portal.views.user.Token.objects.get_or_create')
    @mock.patch('tethys_portal.views.user.User.objects.get')
    def test_profile_mfa_required_mfa_set(self, mock_get_user, mock_token_get_create, mock_render, mock_get_quota,
                                          mock_convert_units, mock_has_mfa, _):
        mock_request = mock.MagicMock()
        mock_user = mock.MagicMock()
        mock_get_user.return_value = mock_user

        mock_user_token = mock.MagicMock()
        mock_token_created = mock.MagicMock()
        mock_token_get_create.return_value = mock_user_token, mock_token_created
        mock_convert_units.return_value = '0 bytes'
        mock_get_quota.return_value = {'quota': None}
        mock_has_mfa.return_value = True

        expected_context = {
            'user_token': mock_user_token.key,
            'current_use': '0 bytes',
            'quota': None,
            'has_mfa': True,
            'mfa_required': True,
            'show_user_token_mfa': True  # Show user token b/c mfa is required and user has setup mfa
        }

        profile(mock_request)

        mock_render.assert_called_with(mock_request, 'tethys_portal/user/profile.html', expected_context)

    @override_settings(MFA_REQUIRED=False)
    @mock.patch('tethys_quotas.utilities.log')
    @mock.patch('tethys_portal.views.user.has_mfa')
    @mock.patch('tethys_portal.views.user._convert_storage_units')
    @mock.patch('tethys_portal.views.user.get_quota')
    @mock.patch('tethys_portal.views.user.render')
    @mock.patch('tethys_portal.views.user.Token.objects.get_or_create')
    @mock.patch('tethys_portal.views.user.User.objects.get')
    def test_profile_mfa_not_required_mfa_set(self, mock_get_user, mock_token_get_create, mock_render, mock_get_quota,
                                              mock_convert_units, mock_has_mfa, _):
        mock_request = mock.MagicMock()
        mock_user = mock.MagicMock()
        mock_get_user.return_value = mock_user

        mock_user_token = mock.MagicMock()
        mock_token_created = mock.MagicMock()
        mock_token_get_create.return_value = mock_user_token, mock_token_created
        mock_convert_units.return_value = '0 bytes'
        mock_get_quota.return_value = {'quota': None}
        mock_has_mfa.return_value = True

        expected_context = {
            'user_token': mock_user_token.key,
            'current_use': '0 bytes',
            'quota': None,
            'has_mfa': True,
            'mfa_required': False,
            'show_user_token_mfa': True  # Show user token b/c not mfa is required
        }

        profile(mock_request)

        mock_render.assert_called_with(mock_request, 'tethys_portal/user/profile.html', expected_context)

    @mock.patch('tethys_portal.views.user.UserSettingsForm')
    @mock.patch('tethys_portal.views.user.redirect')
    def test_settings_request_post(self, mock_redirect, mock_usf):
        mock_first_name = mock.MagicMock()
        mock_last_name = mock.MagicMock()
        mock_email = mock.MagicMock()

        mock_user = mock.MagicMock()
        mock_user.username = 'foo'
        mock_user.first_name = mock_first_name
        mock_user.last_name = mock_last_name
        mock_user.email = mock_email

        mock_request = mock.MagicMock()
        mock_request.user = mock_user
        mock_request.method = 'POST'
        mock_request.POST = 'user-settings-submit'

        mock_form = mock.MagicMock()
        mock_form.is_valid.return_value = True
        mock_usf.return_value = mock_form

        settings(mock_request)

        mock_user.save.assert_called()

        mock_usf.assert_called_once_with(mock_request.POST)

        mock_redirect.assert_called_once_with('user:profile')

    @mock.patch('tethys_quotas.utilities.log')
    @mock.patch('tethys_portal.views.user.django_settings')
    @mock.patch('tethys_portal.views.user.Token.objects.get_or_create')
    @mock.patch('tethys_portal.views.user.UserSettingsForm')
    @mock.patch('tethys_portal.views.user.render')
    def test_settings_request_get(self, mock_render, mock_usf, mock_token_get_create, mock_django_settings, _):
        mock_request_user = mock.MagicMock()
        mock_request_user.username = 'foo'

        mock_request = mock.MagicMock()
        mock_request.user = mock_request_user
        mock_request.method = 'GET'

        mock_form = mock.MagicMock()
        mock_usf.return_value = mock_form

        mock_user_token = mock.MagicMock()
        mock_token_created = mock.MagicMock()
        mock_token_get_create.return_value = mock_user_token, mock_token_created

        mock_django_settings.MFA_REQUIRED = False

        expected_context = {'form': mock_form,
                            'user_token': mock_user_token.key,
                            'current_use': '0 bytes',
                            'quota': None,
                            'mfa_required': False,
                            'has_mfa': False,
                            'show_user_token_mfa': True
                            }

        settings(mock_request)

        mock_usf.assert_called_once_with(instance=mock_request_user)

        mock_token_get_create.assert_called_once_with(user=mock_request_user)

        mock_render.assert_called_once_with(mock_request, 'tethys_portal/user/settings.html', expected_context)

    @mock.patch('tethys_portal.views.user.UserPasswordChangeForm')
    @mock.patch('tethys_portal.views.user.redirect')
    def test_change_password_post(self, mock_redirect, mock_upf):
        mock_user = mock.MagicMock()
        mock_user.username = 'foo'

        mock_request = mock.MagicMock()
        mock_request.user = mock_user

        mock_request.method = 'POST'
        mock_request.POST = 'change-password-submit'

        mock_form = mock.MagicMock()
        mock_form.is_valid.return_value = True
        mock_upf.return_value = mock_form

        change_password(mock_request)

        mock_redirect.assert_called_once_with('user:settings')

        mock_form.clean_old_password.assert_called()

        mock_form.clean_new_password2.assert_called()

        mock_form.save.assert_called()

        mock_upf.assert_called_once_with(user=mock_request.user, data=mock_request.POST)

    @mock.patch('tethys_portal.views.user.UserPasswordChangeForm')
    @mock.patch('tethys_portal.views.user.render')
    def test_change_password_get(self, mock_render, mock_upf):
        mock_request_user = mock.MagicMock()
        mock_request_user.username = 'foo'

        mock_request = mock.MagicMock()
        mock_request.user = mock_request_user
        mock_request.method = 'GET'

        mock_form = mock.MagicMock()
        mock_upf.return_value = mock_form

        expected_context = {'form': mock_form}

        change_password(mock_request)

        mock_upf.assert_called_once_with(user=mock_request_user)

        mock_render.assert_called_once_with(mock_request, 'tethys_portal/user/change_password.html', expected_context)

    @mock.patch('tethys_portal.views.user.render')
    def test_social_disconnect_valid_user(self, mock_render):
        mock_request_user = mock.MagicMock()
        mock_request_user.username = 'foo'

        mock_request = mock.MagicMock()
        mock_request.user = mock_request_user

        mock_provider = mock.MagicMock()

        mock_association_id = mock.MagicMock()

        expected_context = {'provider': mock_provider,
                            'association_id': mock_association_id}

        social_disconnect(mock_request, mock_provider, mock_association_id)

        mock_render.assert_called_once_with(mock_request, 'tethys_portal/user/disconnect.html', expected_context)

    @mock.patch('tethys_portal.views.user.messages.success')
    @mock.patch('tethys_portal.views.user.logout')
    @mock.patch('tethys_portal.views.user.redirect')
    def test_delete_account_post(self, mock_redirect, mock_logout, mock_messages_success):
        mock_user = mock.MagicMock()
        mock_user.username = 'foo'

        mock_request = mock.MagicMock()
        mock_request.user = mock_user

        mock_request.method = 'POST'
        mock_request.POST = 'delete-account-submit'

        delete_account(mock_request)

        mock_request.user.delete.assert_called()

        mock_logout.assert_called_once_with(mock_request)

        mock_messages_success.assert_called_once_with(mock_request, 'Your account has been successfully deleted.')

        mock_redirect.assert_called_once_with('home')

    @mock.patch('tethys_portal.views.user.render')
    def test_delete_account_not_post(self, mock_render):
        mock_user = mock.MagicMock()
        mock_user.username = 'foo'

        mock_request = mock.MagicMock()
        mock_request.user = mock_user

        mock_request.method = 'GET'

        delete_account(mock_request)

        expected_context = {}

        mock_render.assert_called_once_with(mock_request, 'tethys_portal/user/delete.html', expected_context)

    @mock.patch('tethys_quotas.utilities.log')
    @mock.patch('tethys_portal.views.user._get_user_workspace')
    @mock.patch('tethys_portal.views.user._convert_storage_units')
    @mock.patch('tethys_portal.views.user.User')
    @mock.patch('tethys_portal.views.user.SingletonHarvester')
    @mock.patch('tethys_portal.views.user.render')
    def test_manage_storage_successful(self, mock_render, mock_harvester, mock_user, mock_convert_storage, _, __):
        mock_request = mock.MagicMock()
        mock_request.user.username = 'ThisIsMe'
        app = TethysApp(name="app_name")
        mock_harvester().apps = [app]
        mock_user.objects.get.return_value = mock.MagicMock()
        mock_convert_storage.return_value = '0 bytes'

        expected_context = {'apps': mock_harvester().apps,
                            'current_use': '0 bytes',
                            'quota': None,
                            }

        manage_storage(mock_request)

        mock_render.assert_called_once_with(mock_request, 'tethys_portal/user/manage_storage.html', expected_context)

    @mock.patch('tethys_quotas.utilities.log')
    @mock.patch('tethys_portal.views.user.TethysApp')
    @mock.patch('tethys_portal.views.user.render')
    def test_clear_workspace_display(self, mock_render, mock_TethysApp, _):
        mock_request = mock.MagicMock()
        mock_request.user.username = 'ThisIsMe'

        expected_context = {'app_name': mock_TethysApp.objects.get().name}

        clear_workspace(mock_request, 'root_url')

        mock_render.assert_called_once_with(mock_request, 'tethys_portal/user/clear_workspace.html', expected_context)

    @mock.patch('tethys_portal.views.user.get_app_class')
    @mock.patch('tethys_portal.views.user._get_user_workspace')
    @mock.patch('tethys_portal.views.user.User')
    @mock.patch('tethys_portal.views.user.TethysApp')
    @mock.patch('tethys_portal.views.user.messages.success')
    @mock.patch('tethys_portal.views.user.redirect')
    def test_clear_workspace_successful(self, mock_redirect, mock_message, mock_app, mock_user, mock_guw,
                                        mock_get_app_class):  # noqa: E501
        mock_request = mock.MagicMock(method='POST', POST='clear-workspace-submit')
        mock_request.user.username = 'ThisIsMe'

        mock_user.objects.get.return_value = mock.MagicMock(User(username='ThisIsMe'))
        app = TethysApp(name='app_name')
        mock_app.objects.get.return_value = app
        mock_get_app_class.return_value = app
        app.pre_delete_user_workspace = mock.MagicMock()
        app.post_delete_user_workspace = mock.MagicMock()
        mock_guw.return_value = mock.MagicMock()

        clear_workspace(mock_request, 'root_url')

        mock_message.assert_called_once_with(mock_request, 'Your workspace has been successfully cleared.')
        mock_redirect.assert_called_once_with('user:manage_storage')
