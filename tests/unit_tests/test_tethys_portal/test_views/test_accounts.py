import unittest
from unittest import mock

from django.test import override_settings

# Fixes the Cache-Control error in tests. Must appear before view imports.
mock.patch('django.views.decorators.cache.never_cache', lambda x: x).start()

from tethys_portal.views.accounts import login_view, register, logout_view, reset_confirm, reset  # noqa: E402


class TethysPortalViewsAccountsTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('tethys_portal.views.accounts.redirect')
    def test_login_view_not_anonymous_user(self, mock_redirect):
        mock_request = mock.MagicMock()
        mock_request.user.is_anonymous = False
        mock_request.user.username = 'sam'
        login_view(mock_request)
        mock_redirect.assert_called_once_with('user:profile', username='sam')

    @mock.patch('tethys_portal.views.accounts.log_user_in')
    @mock.patch('tethys_portal.views.accounts.authenticate')
    @mock.patch('tethys_portal.views.accounts.LoginForm')
    def test_login_view_post_request(self, mock_login_form, mock_authenticate, mock_login):
        mock_request = mock.MagicMock()
        mock_request.method = 'POST'
        mock_request.POST = 'login-submit'
        mock_request.user.is_anonymous = True
        mock_request.user.username = 'sam'
        mock_request.GET = ''

        mock_form = mock.MagicMock()
        mock_login_form.return_value = mock_form

        # mock validate the form
        mock_form.is_valid.return_value = True

        mock_username = mock.MagicMock()
        mock_password = mock.MagicMock()
        mock_form.cleaned_data('username').return_value = mock_username
        mock_form.cleaned_data('password').return_value = mock_password

        # mock authenticate
        mock_user = mock.MagicMock()
        mock_authenticate.return_value = mock_user

        # mock the password has been verified for the user
        mock_user.is_active = True

        # call the login function with mock args
        login_view(mock_request)

        mock_login_form.assert_called_with(mock_request.POST)

        # mock authenticate call
        mock_authenticate.asset_called_with(username=mock_username, password=mock_password)

        # mock the user is valid, active, and authenticated, so login in the user
        mock_login.assert_called_with(mock_request, mock_user)

    @mock.patch('tethys_portal.views.accounts.log_user_in')
    @mock.patch('tethys_portal.views.accounts.authenticate')
    @mock.patch('tethys_portal.views.accounts.LoginForm')
    def test_login_view_get_method_next(self, mock_login_form, mock_authenticate, mock_login):
        mock_request = mock.MagicMock()
        mock_request.method = 'POST'
        mock_request.POST = 'login-submit'
        mock_request.user.is_anonymous = True
        mock_request.user.username = 'sam'
        mock_request.GET = {'next': 'foo'}

        mock_form = mock.MagicMock()
        mock_login_form.return_value = mock_form

        # mock validate the form
        mock_form.is_valid.return_value = True

        mock_username = mock.MagicMock()
        mock_password = mock.MagicMock()
        mock_form.cleaned_data('username').return_value = mock_username
        mock_form.cleaned_data('password').return_value = mock_password

        # mock authenticate
        mock_user = mock.MagicMock()
        mock_authenticate.return_value = mock_user

        # mock the password has been verified for the user
        mock_user.is_active = True

        # call the login function with mock args
        login_view(mock_request)

        mock_login_form.assert_called_with(mock_request.POST)

        # mock authenticate call
        mock_authenticate.asset_called_with(username=mock_username, password=mock_password)

        # mock the user is valid, active, and authenticated, so login in the user
        mock_login.assert_called_with(mock_request, mock_user)

    @mock.patch('tethys_portal.views.accounts.has_mfa')
    @mock.patch('tethys_portal.views.accounts.authenticate')
    @mock.patch('tethys_portal.views.accounts.LoginForm')
    def test_login_view_post_request_with_mfa(self, mock_login_form, mock_authenticate, mock_mfa):
        mock_request = mock.MagicMock()
        mock_request.method = 'POST'
        mock_request.POST = 'login-submit'
        mock_request.user.is_anonymous = True
        mock_request.user.username = 'sam'
        mock_request.GET = ''

        mock_mfa.return_value = True

        mock_form = mock.MagicMock()
        mock_login_form.return_value = mock_form

        # mock validate the form
        mock_form.is_valid.return_value = True

        mock_username = mock.MagicMock()
        mock_password = mock.MagicMock()
        mock_form.cleaned_data('username').return_value = mock_username
        mock_form.cleaned_data('password').return_value = mock_password

        # mock authenticate
        mock_user = mock.MagicMock()
        mock_user.username = 'testname'
        mock_authenticate.return_value = mock_user

        # mock the password has been verified for the user
        mock_user.is_active = True

        # call the login function with mock args
        login_view(mock_request)

        mock_login_form.assert_called_with(mock_request.POST)

        # mock authenticate call
        mock_authenticate.asset_called_with(username=mock_username, password=mock_password)

        # mock the user is valid, active, and authenticated, so login in the user
        mock_mfa.assert_called_with(mock_request, mock_user.username)

    @override_settings(ENABLE_OPEN_SIGNUP=False)
    @mock.patch('tethys_portal.views.accounts.render')
    @mock.patch('tethys_portal.views.accounts.messages')
    @mock.patch('tethys_portal.views.accounts.login')
    @mock.patch('tethys_portal.views.accounts.authenticate')
    @mock.patch('tethys_portal.views.accounts.LoginForm')
    @mock.patch('tethys_portal.views.accounts.redirect')
    def test_login_view_get_method_not_active_user(self, mock_redirect, mock_login_form, mock_authenticate, mock_login,
                                                   mock_messages, mock_render):
        mock_request = mock.MagicMock()
        mock_request.method = 'POST'
        mock_request.POST = 'login-submit'
        mock_request.user.is_anonymous = True
        mock_request.user.username = 'sam'
        mock_request.GET = {'next': 'foo'}

        mock_form = mock.MagicMock()
        mock_login_form.return_value = mock_form

        # mock validate the form
        mock_form.is_valid.return_value = True

        mock_username = mock.MagicMock()
        mock_password = mock.MagicMock()
        mock_form.cleaned_data('username').return_value = mock_username
        mock_form.cleaned_data('password').return_value = mock_password

        # mock authenticate
        mock_user = mock.MagicMock()
        mock_authenticate.return_value = mock_user

        # mock the password has been verified for the user
        mock_user.is_active = False

        # call the login function with mock args
        login_view(mock_request)

        mock_login_form.assert_called_with(mock_request.POST)

        # mock authenticate call
        mock_authenticate.asset_called_with(username=mock_username, password=mock_password)

        # mock the user is valid, active, and authenticated, so login in the user
        mock_login.assert_not_called()

        # mock redirect after logged in using next parameter or default to user profile
        mock_redirect.assert_not_called()

        mock_messages.error.assert_called_once_with(mock_request, "Sorry, but your account has been disabled. "
                                                                  "Please contact the site "
                                                                  "administrator for more details.")

        context = {'form': mock_login_form(),
                   'signup_enabled': False}

        mock_render.assert_called_once_with(mock_request, 'tethys_portal/accounts/login.html', context)

    @override_settings(ENABLE_OPEN_SIGNUP=False)
    @mock.patch('tethys_portal.views.accounts.render')
    @mock.patch('tethys_portal.views.accounts.messages')
    @mock.patch('tethys_portal.views.accounts.login')
    @mock.patch('tethys_portal.views.accounts.authenticate')
    @mock.patch('tethys_portal.views.accounts.LoginForm')
    @mock.patch('tethys_portal.views.accounts.redirect')
    def test_login_view_get_method_user_none(self, mock_redirect, mock_login_form, mock_authenticate, mock_login,
                                             mock_messages, mock_render):
        mock_request = mock.MagicMock()
        mock_request.method = 'POST'
        mock_request.POST = 'login-submit'
        mock_request.user.is_anonymous = True
        mock_request.user.username = 'sam'
        mock_request.GET = {'next': 'foo'}

        mock_form = mock.MagicMock()
        mock_login_form.return_value = mock_form

        # mock validate the form
        mock_form.is_valid.return_value = True

        mock_username = mock.MagicMock()
        mock_password = mock.MagicMock()
        mock_form.cleaned_data('username').return_value = mock_username
        mock_form.cleaned_data('password').return_value = mock_password

        # mock authenticate
        mock_user = mock.MagicMock()
        mock_authenticate.return_value = None

        # mock the password has been verified for the user
        mock_user.is_active = False

        # call the login function with mock args
        login_view(mock_request)

        mock_login_form.assert_called_with(mock_request.POST)

        # mock authenticate call
        mock_authenticate.asset_called_with(username=mock_username, password=mock_password)

        # mock the user is valid, active, and authenticated, so login in the user
        mock_login.assert_not_called()

        # mock redirect after logged in using next parameter or default to user profile
        mock_redirect.assert_not_called()

        mock_messages.warning.assert_called_once_with(mock_request, "Whoops! We were not able to log you in. "
                                                                    "Please check your username and "
                                                                    "password and try again.")

        context = {'form': mock_login_form(),
                   'signup_enabled': False}

        mock_render.assert_called_once_with(mock_request, 'tethys_portal/accounts/login.html', context)

    @override_settings(ENABLE_OPEN_SIGNUP=False)
    @mock.patch('tethys_portal.views.accounts.render')
    @mock.patch('tethys_portal.views.accounts.login')
    @mock.patch('tethys_portal.views.accounts.LoginForm')
    @mock.patch('tethys_portal.views.accounts.redirect')
    def test_login_view_wrong_method(self, mock_redirect, mock_login_form, mock_login, mock_render):
        mock_request = mock.MagicMock()
        mock_request.method = 'foo'

        mock_form = mock.MagicMock()
        mock_login_form.return_value = mock_form

        # call the login function with mock args
        login_view(mock_request)

        mock_login_form.assert_called_with()

        # mock the user is valid, active, and authenticated, so login in the user
        mock_login.assert_not_called()

        # mock redirect after logged in using next parameter or default to user profile
        mock_redirect.assert_not_called()

        context = {'form': mock_login_form(),
                   'signup_enabled': False}

        mock_render.assert_called_once_with(mock_request, 'tethys_portal/accounts/login.html', context)

    @mock.patch('tethys_portal.views.accounts.redirect')
    def test_register_not_anonymous_user(self, mock_redirect):
        mock_request = mock.MagicMock()
        mock_request.user.is_anonymous = False
        mock_request.user.username = 'sam'
        register(mock_request)
        mock_redirect.assert_called_once_with('user:profile', username='sam')

    @override_settings(ENABLE_OPEN_SIGNUP=False)
    @mock.patch('tethys_portal.views.accounts.redirect')
    def test_register_not_enable_open_signup(self, mock_redirect):
        mock_request = mock.MagicMock()
        mock_request.user.is_anonymous = True
        mock_request.user.username = 'sam'
        register(mock_request)
        mock_redirect.assert_called_once_with('accounts:login')

    @override_settings(ENABLE_OPEN_SIGNUP=True)
    @mock.patch('tethys_portal.views.accounts.login')
    @mock.patch('tethys_portal.views.accounts.authenticate')
    @mock.patch('tethys_portal.views.accounts.RegisterForm')
    @mock.patch('tethys_portal.views.accounts.redirect')
    def test_register_post_request(self, mock_redirect, mock_register_form, mock_authenticate, mock_login):
        mock_request = mock.MagicMock()
        mock_request.method = 'POST'
        mock_request.POST = 'register-submit'
        mock_request.user.is_anonymous = True
        mock_request.user.username = 'sam'
        mock_request.GET = ''

        mock_form = mock.MagicMock()
        mock_register_form.return_value = mock_form

        # mock validate the form
        mock_form.is_valid.return_value = True

        mock_username = mock.MagicMock()
        mock_email = mock.MagicMock()
        mock_password = mock.MagicMock()
        mock_form.clean_username.return_value = mock_username
        mock_form.clean_email.return_value = mock_email
        mock_form.clean_password2.return_value = mock_password

        # mock authenticate
        mock_user = mock.MagicMock()
        mock_authenticate.return_value = mock_user

        # mock the password has been verified for the user
        mock_user.is_active = True

        # call the login function with mock args
        register(mock_request)

        mock_form.save.assert_called_once()

        mock_register_form.assert_called_with(mock_request.POST)

        # mock authenticate call
        mock_authenticate.asset_called_with(username=mock_username, password=mock_password)

        # mock the user is valid, active, and authenticated, so login in the user
        mock_login.assert_called_with(mock_request, mock_user)

        # mock redirect after logged in using next parameter or default to user profile
        mock_redirect.assert_called_once_with('user:profile', username=mock_user.username)

    @override_settings(ENABLE_OPEN_SIGNUP=True)
    @mock.patch('tethys_portal.views.accounts.login')
    @mock.patch('tethys_portal.views.accounts.authenticate')
    @mock.patch('tethys_portal.views.accounts.RegisterForm')
    @mock.patch('tethys_portal.views.accounts.redirect')
    def test_register_post_request_next(self, mock_redirect, mock_register_form, mock_authenticate, mock_login):
        mock_request = mock.MagicMock()
        mock_request.method = 'POST'
        mock_request.POST = 'register-submit'
        mock_request.user.is_anonymous = True
        mock_request.user.username = 'sam'
        mock_request.GET = {'next': 'foo'}

        mock_form = mock.MagicMock()
        mock_register_form.return_value = mock_form

        # mock validate the form
        mock_form.is_valid.return_value = True

        mock_username = mock.MagicMock()
        mock_email = mock.MagicMock()
        mock_password = mock.MagicMock()
        mock_form.clean_username.return_value = mock_username
        mock_form.clean_email.return_value = mock_email
        mock_form.clean_password2.return_value = mock_password

        # mock authenticate
        mock_user = mock.MagicMock()
        mock_authenticate.return_value = mock_user

        # mock the password has been verified for the user
        mock_user.is_active = True

        # call the login function with mock args
        register(mock_request)

        mock_form.save.assert_called_once()

        mock_register_form.assert_called_with(mock_request.POST)

        # mock authenticate call
        mock_authenticate.asset_called_with(username=mock_username, password=mock_password)

        # mock the user is valid, active, and authenticated, so login in the user
        mock_login.assert_called_with(mock_request, mock_user)

        # mock redirect after logged in using next parameter or default to user profile
        mock_redirect.assert_called_once_with(mock_request.GET['next'])

    @override_settings(ENABLE_OPEN_SIGNUP=True)
    @mock.patch('tethys_portal.views.accounts.messages')
    @mock.patch('tethys_portal.views.accounts.login')
    @mock.patch('tethys_portal.views.accounts.authenticate')
    @mock.patch('tethys_portal.views.accounts.RegisterForm')
    @mock.patch('tethys_portal.views.accounts.render')
    def test_register_post_request_not_active_user(self, mock_render, mock_register_form, mock_authenticate,
                                                   mock_login, mock_messages):
        mock_request = mock.MagicMock()
        mock_request.method = 'POST'
        mock_request.POST = 'register-submit'
        mock_request.user.is_anonymous = True
        mock_request.user.username = 'sam'
        mock_request.GET = ''

        mock_form = mock.MagicMock()
        mock_register_form.return_value = mock_form

        # mock validate the form
        mock_form.is_valid.return_value = True

        mock_username = mock.MagicMock()
        mock_email = mock.MagicMock()
        mock_password = mock.MagicMock()
        mock_form.clean_username.return_value = mock_username
        mock_form.clean_email.return_value = mock_email
        mock_form.clean_password2.return_value = mock_password

        # mock authenticate
        mock_user = mock.MagicMock()
        mock_authenticate.return_value = mock_user

        # mock the password has been verified for the user
        mock_user.is_active = False

        # call the login function with mock args
        register(mock_request)

        mock_form.save.assert_called_once()

        mock_register_form.assert_called_with(mock_request.POST)

        # mock authenticate call
        mock_authenticate.asset_called_with(username=mock_username, password=mock_password)

        # mock the user is valid, active, and authenticated, so login in the user
        mock_login.assert_not_called()

        mock_messages.error.assert_called_once_with(mock_request, "Sorry, but your account has been disabled. "
                                                                  "Please contact the site "
                                                                  "administrator for more details.")

        context = {'form': mock_form}

        # mock redirect after logged in using next parameter or default to user profile
        mock_render.assert_called_once_with(mock_request, 'tethys_portal/accounts/register.html', context)

    @override_settings(ENABLE_OPEN_SIGNUP=True)
    @mock.patch('tethys_portal.views.accounts.messages')
    @mock.patch('tethys_portal.views.accounts.login')
    @mock.patch('tethys_portal.views.accounts.authenticate')
    @mock.patch('tethys_portal.views.accounts.RegisterForm')
    @mock.patch('tethys_portal.views.accounts.render')
    def test_register_post_request_user_none(self, mock_render, mock_register_form, mock_authenticate,
                                             mock_login, mock_messages):
        mock_request = mock.MagicMock()
        mock_request.method = 'POST'
        mock_request.POST = 'register-submit'
        mock_request.user.is_anonymous = True
        mock_request.user.username = 'sam'
        mock_request.GET = ''

        mock_form = mock.MagicMock()
        mock_register_form.return_value = mock_form

        # mock validate the form
        mock_form.is_valid.return_value = True

        mock_username = mock.MagicMock()
        mock_email = mock.MagicMock()
        mock_password = mock.MagicMock()
        mock_form.clean_username.return_value = mock_username
        mock_form.clean_email.return_value = mock_email
        mock_form.clean_password2.return_value = mock_password

        # mock authenticate
        mock_user = mock.MagicMock()
        mock_authenticate.return_value = None

        # mock the password has been verified for the user
        mock_user.is_active = False

        # call the login function with mock args
        register(mock_request)

        mock_form.save.assert_called_once()

        mock_register_form.assert_called_with(mock_request.POST)

        # mock authenticate call
        mock_authenticate.asset_called_with(username=mock_username, password=mock_password)

        # mock the user is valid, active, and authenticated, so login in the user
        mock_login.assert_not_called()

        mock_messages.warning.assert_called_once_with(mock_request, "Whoops! We were not able to log you in. "
                                                                    "Please check your username and "
                                                                    "password and try again.")

        context = {'form': mock_form}

        # mock redirect after logged in using next parameter or default to user profile
        mock_render.assert_called_once_with(mock_request, 'tethys_portal/accounts/register.html', context)

    @override_settings(ENABLE_OPEN_SIGNUP=True)
    @mock.patch('tethys_portal.views.accounts.RegisterForm')
    @mock.patch('tethys_portal.views.accounts.render')
    def test_register_bad_request(self, mock_render, mock_register_form):
        mock_request = mock.MagicMock()
        mock_request.method = 'FOO'

        mock_form = mock.MagicMock()

        mock_register_form.return_value = mock_form

        # mock validate the form
        mock_form.is_valid.return_value = True

        # call the login function with mock args
        register(mock_request)

        mock_form.save.assert_not_called()

        mock_register_form.assert_called_with()

        context = {'form': mock_form}

        # mock redirect after logged in using next parameter or default to user profile
        mock_render.assert_called_once_with(mock_request, 'tethys_portal/accounts/register.html', context)

    @mock.patch('tethys_portal.views.accounts.messages')
    @mock.patch('tethys_portal.views.accounts.logout')
    @mock.patch('tethys_portal.views.accounts.redirect')
    def test_logout_view(self, mock_redirect, mock_logout, mock_messages):
        mock_request = mock.MagicMock()
        mock_request.user.is_anonymous = False
        mock_request.user.first_name = 'foo'
        mock_request.user.username = 'bar'

        mock_redirect.return_value = 'home'

        ret = logout_view(mock_request)

        self.assertEqual('home', ret)

        mock_logout.assert_called_once_with(mock_request)

        mock_messages.success.assert_called_once_with(mock_request, 'Goodbye, {0}. Come back soon!'.
                                                      format(mock_request.user.first_name))

        mock_redirect.assert_called_once_with('home')

    @mock.patch('tethys_portal.views.accounts.reverse')
    @mock.patch('tethys_portal.views.accounts.PasswordResetConfirmView')
    def test_reset_confirm(self, mock_prc, mock_reverse):
        mock_request = mock.MagicMock()
        mock_reverse.return_value = 'accounts:login'
        mock_prc.return_value = True
        ret = reset_confirm(mock_request)
        self.assertTrue(ret)
        mock_prc.assert_called_once_with(mock_request,
                                         template_name='tethys_portal/accounts/password_reset/reset_confirm.html',
                                         uidb64=None,
                                         token=None,
                                         success_url='accounts:login')

    @mock.patch('tethys_portal.views.accounts.reverse')
    @mock.patch('tethys_portal.views.accounts.PasswordResetView')
    def test_reset(self, mock_pr, mock_reverse):
        mock_request = mock.MagicMock()
        mock_reverse.return_value = 'accounts:login'
        mock_pr.return_value = True
        ret = reset(mock_request)
        self.assertTrue(ret)
        mock_pr.assert_called_once_with(mock_request,
                                        template_name='tethys_portal/accounts/password_reset/reset_request.html',
                                        email_template_name='tethys_portal/accounts/password_reset/reset_email.html',
                                        subject_template_name='tethys_portal/accounts/password_reset/reset_subject.txt',
                                        success_url='accounts:login')
