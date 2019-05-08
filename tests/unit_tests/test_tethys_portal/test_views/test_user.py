import unittest
from unittest import mock
from django.contrib.auth.models import User
from tethys_portal.views.user \
    import profile, settings, change_password, social_disconnect, delete_account, manage_storage, clear_workspace
from tethys_apps.models import TethysApp


class TethysPortalUserTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('tethys_quotas.utilities.log')
    @mock.patch('tethys_portal.views.user._convert_storage_units')
    @mock.patch('tethys_portal.views.user.get_quota')
    @mock.patch('tethys_portal.views.user.render')
    @mock.patch('tethys_portal.views.user.Token.objects.get_or_create')
    @mock.patch('tethys_portal.views.user.User.objects.get')
    def test_profile(self, mock_get_user, mock_token_get_create, mock_render, mock_get_quota, mock_convert_units, _):
        mock_request = mock.MagicMock()
        username = 'foo'

        mock_context_user = mock.MagicMock()
        mock_get_user.return_value = mock_context_user

        mock_user_token = mock.MagicMock()
        mock_token_created = mock.MagicMock()
        mock_token_get_create.return_value = mock_user_token, mock_token_created
        mock_convert_units.return_value = '0 bytes'
        mock_get_quota.return_value = {'quota': None}

        expected_context = {
            'context_user': mock_context_user,
            'user_token': mock_user_token.key,
            'current_use': '0 bytes',
            'quota': None,
        }

        profile(mock_request, username)

        mock_render.assert_called_with(mock_request, 'tethys_portal/user/profile.html', expected_context)

        expected_context = {
            'context_user': mock_context_user,
            'user_token': mock_user_token.key,
            'current_use': '0 bytes',
            'quota': '0 bytes',
        }

        mock_get_quota.return_value = {'quota': 1, 'units': 0}

        profile(mock_request, username)

        mock_render.assert_called_with(mock_request, 'tethys_portal/user/profile.html', expected_context)

        mock_get_user.assert_called_with(username='foo')

        mock_token_get_create.assert_called_with(user=mock_context_user)

    @mock.patch('tethys_portal.views.user.messages.warning')
    @mock.patch('tethys_portal.views.user.redirect')
    def test_settings(self, mock_redirect, mock_message_warn):
        mock_request = mock.MagicMock()
        username = 'foo'
        mock_user = mock.MagicMock()
        mock_user.username = 'sam'
        mock_request.user = mock_user

        settings(mock_request, username)

        mock_message_warn.assert_called_once_with(mock_request, "You are not allowed to change other users' settings.")
        mock_redirect.assert_called_once_with('user:profile', username='sam')

    @mock.patch('tethys_portal.views.user.UserSettingsForm')
    @mock.patch('tethys_portal.views.user.redirect')
    def test_settings_request_post(self, mock_redirect, mock_usf):
        username = 'foo'

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

        settings(mock_request, username)

        mock_user.save.assert_called()

        mock_usf.assert_called_once_with(mock_request.POST)

        mock_redirect.assert_called_once_with('user:profile', username='foo')

    @mock.patch('tethys_quotas.utilities.log')
    @mock.patch('tethys_portal.views.user.Token.objects.get_or_create')
    @mock.patch('tethys_portal.views.user.UserSettingsForm')
    @mock.patch('tethys_portal.views.user.render')
    def test_settings_request_get(self, mock_render, mock_usf, mock_token_get_create, _):
        username = 'foo'

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

        expected_context = {'form': mock_form,
                            'context_user': mock_request.user,
                            'user_token': mock_user_token.key,
                            'current_use': '0 bytes',
                            'quota': None,
                            }

        settings(mock_request, username)

        mock_usf.assert_called_once_with(instance=mock_request_user)

        mock_token_get_create.assert_called_once_with(user=mock_request_user)

        mock_render.assert_called_once_with(mock_request, 'tethys_portal/user/settings.html', expected_context)

    @mock.patch('tethys_portal.views.user.messages.warning')
    @mock.patch('tethys_portal.views.user.redirect')
    def test_change_password(self, mock_redirect, mock_message_warn):
        mock_request = mock.MagicMock()
        username = 'foo'
        mock_user = mock.MagicMock()
        mock_user.username = 'sam'
        mock_request.user = mock_user

        change_password(mock_request, username)

        mock_message_warn.assert_called_once_with(mock_request, "You are not allowed to change other users' settings.")
        mock_redirect.assert_called_once_with('user:profile', username='sam')

    @mock.patch('tethys_portal.views.user.UserPasswordChangeForm')
    @mock.patch('tethys_portal.views.user.redirect')
    def test_change_password_post(self, mock_redirect, mock_upf):
        username = 'foo'

        mock_user = mock.MagicMock()
        mock_user.username = 'foo'

        mock_request = mock.MagicMock()
        mock_request.user = mock_user

        mock_request.method = 'POST'
        mock_request.POST = 'change-password-submit'

        mock_form = mock.MagicMock()
        mock_form.is_valid.return_value = True
        mock_upf.return_value = mock_form

        change_password(mock_request, username)

        mock_redirect.assert_called_once_with('user:settings', username='foo')

        mock_form.clean_old_password.assert_called()

        mock_form.clean_new_password2.assert_called()

        mock_form.save.assert_called()

        mock_upf.assert_called_once_with(user=mock_request.user, data=mock_request.POST)

    @mock.patch('tethys_portal.views.user.UserPasswordChangeForm')
    @mock.patch('tethys_portal.views.user.render')
    def test_change_password_get(self, mock_render, mock_upf):
        username = 'foo'

        mock_request_user = mock.MagicMock()
        mock_request_user.username = 'foo'

        mock_request = mock.MagicMock()
        mock_request.user = mock_request_user
        mock_request.method = 'GET'

        mock_form = mock.MagicMock()
        mock_upf.return_value = mock_form

        expected_context = {'form': mock_form}

        change_password(mock_request, username)

        mock_upf.assert_called_once_with(user=mock_request_user)

        mock_render.assert_called_once_with(mock_request, 'tethys_portal/user/change_password.html', expected_context)

    @mock.patch('tethys_portal.views.user.messages.warning')
    @mock.patch('tethys_portal.views.user.redirect')
    def test_social_disconnect_invalid_user(self, mock_redirect, mock_message_warn):
        username = 'foo'

        mock_request_user = mock.MagicMock()
        mock_request_user.username = 'sam'

        mock_request = mock.MagicMock()
        mock_request.user = mock_request_user

        mock_provider = mock.MagicMock()

        mock_association_id = mock.MagicMock()

        social_disconnect(mock_request, username, mock_provider, mock_association_id)

        mock_message_warn.assert_called_once_with(mock_request, "You are not allowed to change other users' settings.")

        mock_redirect.assert_called_once_with('user:profile', username='sam')

    @mock.patch('tethys_portal.views.user.render')
    def test_social_disconnect_valid_user(self, mock_render):
        username = 'foo'

        mock_request_user = mock.MagicMock()
        mock_request_user.username = 'foo'

        mock_request = mock.MagicMock()
        mock_request.user = mock_request_user

        mock_provider = mock.MagicMock()

        mock_association_id = mock.MagicMock()

        expected_context = {'provider': mock_provider,
                            'association_id': mock_association_id}

        social_disconnect(mock_request, username, mock_provider, mock_association_id)

        mock_render.assert_called_once_with(mock_request, 'tethys_portal/user/disconnect.html', expected_context)

    @mock.patch('tethys_portal.views.user.messages.warning')
    @mock.patch('tethys_portal.views.user.redirect')
    def test_delete_account(self, mock_redirect, mock_message_warn):
        username = 'foo'

        mock_request_user = mock.MagicMock()
        mock_request_user.username = 'sam'

        mock_request = mock.MagicMock()
        mock_request.user = mock_request_user

        delete_account(mock_request, username)

        mock_message_warn.assert_called_once_with(mock_request, "You are not allowed to change other users' settings.")

        mock_redirect.assert_called_once_with('user:profile', username='sam')

    @mock.patch('tethys_portal.views.user.messages.success')
    @mock.patch('tethys_portal.views.user.logout')
    @mock.patch('tethys_portal.views.user.redirect')
    def test_delete_account_post(self, mock_redirect, mock_logout, mock_messages_success):
        username = 'foo'

        mock_user = mock.MagicMock()
        mock_user.username = 'foo'

        mock_request = mock.MagicMock()
        mock_request.user = mock_user

        mock_request.method = 'POST'
        mock_request.POST = 'delete-account-submit'

        delete_account(mock_request, username)

        mock_request.user.delete.assert_called()

        mock_logout.assert_called_once_with(mock_request)

        mock_messages_success.assert_called_once_with(mock_request, 'Your account has been successfully deleted.')

        mock_redirect.assert_called_once_with('home')

    @mock.patch('tethys_portal.views.user.render')
    def test_delete_account_not_post(self, mock_render):
        username = 'foo'

        mock_user = mock.MagicMock()
        mock_user.username = 'foo'

        mock_request = mock.MagicMock()
        mock_request.user = mock_user

        mock_request.method = 'GET'

        delete_account(mock_request, username)

        expected_context = {}

        mock_render.assert_called_once_with(mock_request, 'tethys_portal/user/delete.html', expected_context)

    @mock.patch('tethys_portal.views.user.redirect')
    @mock.patch('tethys_portal.views.user.messages.warning')
    def test_manage_storage_different_user(self, mock_messages, mock_redirect):
        mock_request = mock.MagicMock()
        mock_request.user.username = 'ThisIsNotMe'

        manage_storage(mock_request, 'ThisIsMe')

        mock_messages.assert_called_once_with(mock_request, "You are not allowed to change other users' settings.")
        mock_redirect.assert_called_once_with('user:profile', username=mock_request.user.username)

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
                            'context_user': mock_request.user,
                            'current_use': '0 bytes',
                            'quota': None,
                            }

        manage_storage(mock_request, 'ThisIsMe')

        mock_render.assert_called_once_with(mock_request, 'tethys_portal/user/manage_storage.html', expected_context)

    @mock.patch('tethys_portal.views.user.redirect')
    @mock.patch('tethys_portal.views.user.messages.warning')
    def test_clear_workspace_different_user(self, mock_messages, mock_redirect):
        mock_request = mock.MagicMock()
        mock_request.user.username = 'ThisIsNotMe'

        clear_workspace(mock_request, 'ThisIsMe', 'url')

        mock_messages.assert_called_once_with(mock_request, "You are not allowed to change other users' settings.")
        mock_redirect.assert_called_once_with('user:profile', username=mock_request.user.username)

    @mock.patch('tethys_quotas.utilities.log')
    @mock.patch('tethys_portal.views.user.TethysApp')
    @mock.patch('tethys_portal.views.user.render')
    def test_clear_workspace_display(self, mock_render, mock_TethysApp, _):
        mock_request = mock.MagicMock()
        mock_request.user.username = 'ThisIsMe'

        expected_context = {'app_name': mock_TethysApp.objects.get().name}

        clear_workspace(mock_request, 'ThisIsMe', 'root_url')

        mock_render.assert_called_once_with(mock_request, 'tethys_portal/user/clear_workspace.html', expected_context)

    @mock.patch('tethys_portal.views.user.get_app_class')
    @mock.patch('tethys_portal.views.user._get_user_workspace')
    @mock.patch('tethys_portal.views.user.User')
    @mock.patch('tethys_portal.views.user.TethysApp')
    @mock.patch('tethys_portal.views.user.messages.success')
    @mock.patch('tethys_portal.views.user.redirect')
    def test_clear_workspace_successful(self, mock_redirect, mock_message, mock_app, mock_user, mock_guw, mock_get_app_class):  # noqa: E501
        mock_request = mock.MagicMock(method='POST', POST='clear-workspace-submit')
        mock_request.user.username = 'ThisIsMe'

        mock_user.objects.get.return_value = mock.MagicMock(User(username='ThisIsMe'))
        app = TethysApp(name='app_name')
        mock_app.objects.get.return_value = app
        mock_get_app_class.return_value = app
        app.pre_delete_user_workspace = mock.MagicMock()
        app.post_delete_user_workspace = mock.MagicMock()
        mock_guw.return_value = mock.MagicMock()

        clear_workspace(mock_request, 'ThisIsMe', 'root_url')

        mock_message.assert_called_once_with(mock_request, 'Your workspace has been successfully cleared.')
        mock_redirect.assert_called_once_with('user:manage_storage', username=mock_request.user.username)
