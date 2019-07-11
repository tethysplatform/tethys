from django.test import TestCase
from captcha.models import CaptchaStore
from tethys_portal.forms import LoginForm, RegisterForm, UserSettingsForm, UserPasswordChangeForm
from django.contrib.auth.models import User
from django import forms
from unittest import mock


class TethysPortalFormsTests(TestCase):

    def setUp(self):
        CaptchaStore.generate_key()
        self.hashkey = CaptchaStore.objects.all()[0].hashkey
        self.response = CaptchaStore.objects.all()[0].response
        self.user = User.objects.create_user(username='user_exist',
                                             email='foo_exist@aquaveo.com',
                                             password='glass_onion')

    def tearDown(self):
        pass
    # Login Form

    def test_LoginForm(self):
        login_data = {'username': 'admin', 'password': 'test1231', 'captcha_0': self.hashkey,
                      'captcha_1': self.response}
        login_form = LoginForm(login_data)
        self.assertTrue(login_form.is_valid())

    def test_LoginForm_invalid_username(self):
        login_data = {'username': '$!admin', 'password': 'test1231', 'captcha_0': self.hashkey,
                      'captcha_1': self.response}
        login_form = LoginForm(login_data)
        err_msg = "This value may contain only letters, numbers and @/./+/-/_ characters."
        self.assertEqual(login_form.errors['username'], [err_msg])
        self.assertFalse(login_form.is_valid())

    def test_LoginForm_invalid_password(self):
        login_data = {'username': 'admin', 'password': '', 'captcha_0': self.hashkey,
                      'captcha_1': self.response}
        login_form = LoginForm(login_data)
        self.assertFalse(login_form.is_valid())

    def test_LoginForm_invalid(self):
        login_invalid_data = {'username': 'admin', 'password': 'test1231', 'captcha_0': self.hashkey,
                              'captcha_1': ''}
        login_form = LoginForm(login_invalid_data)
        self.assertFalse(login_form.is_valid())

    # Register Form

    def test_RegisterForm(self):
        register_data = {'username': 'user1', 'email': 'foo@aquaveo.com', 'password1': 'abc123',
                         'password2': 'abc123', 'captcha_0': self.hashkey, 'captcha_1': self.response}
        register_form = RegisterForm(data=register_data)
        self.assertTrue(register_form.is_valid())

    def test_RegisterForm_invalid_user(self):
        register_data = {'username': 'user1&!$', 'email': 'foo@aquaveo.com', 'password1': 'abc123',
                         'password2': 'abc123', 'captcha_0': self.hashkey, 'captcha_1': self.response}
        register_form = RegisterForm(data=register_data)
        err_msg = "This value may contain only letters, numbers and @/./+/-/_ characters."
        self.assertEqual(register_form.errors['username'], [err_msg])
        self.assertFalse(register_form.is_valid())

    def test_RegisterForm_clean_username(self):
        register_data = {'username': 'user', 'email': 'foo@aquaveo.com', 'password1': 'abc123',
                         'password2': 'abc123', 'captcha_0': self.hashkey, 'captcha_1': self.response}

        register_form = RegisterForm(data=register_data)

        self.assertTrue(register_form.is_valid())

        ret = register_form.clean_username()

        self.assertEqual('user', ret)

    def test_RegisterForm_clean_username_dup(self):
        register_data = {'username': 'user_exist', 'email': 'foo@aquaveo.com', 'password1': 'abc123',
                         'password2': 'abc123', 'captcha_0': self.hashkey, 'captcha_1': self.response}

        register_form = RegisterForm(data=register_data)

        # validate form, false because duplicated user
        self.assertFalse(register_form.is_valid())

        # user is duplicated so is_valid removed from cleaned_data, we add it back to test
        register_form.cleaned_data['username'] = 'user_exist'

        self.assertRaises(forms.ValidationError, register_form.clean_username)

    def test_RegisterForm_clean_email(self):
        register_data = {'username': 'user1', 'email': 'foo@aquaveo.com', 'password1': 'abc123',
                         'password2': 'abc123', 'captcha_0': self.hashkey, 'captcha_1': self.response}

        register_form = RegisterForm(data=register_data)

        self.assertTrue(register_form.is_valid())

        ret = register_form.clean_email()

        self.assertEqual('foo@aquaveo.com', ret)

    def test_RegisterForm_clean_email_dup(self):
        register_data = {'username': 'user12', 'email': 'foo_exist@aquaveo.com', 'password1': 'abc123',
                         'password2': 'abc123', 'captcha_0': self.hashkey, 'captcha_1': self.response}

        register_form = RegisterForm(data=register_data)

        register_form.is_valid()

        # is_valid is removing duplicated email
        self.assertNotIn('email', register_form.cleaned_data)

        # To test raise error, we need to put it back in to test
        register_form.cleaned_data['email'] = 'foo_exist@aquaveo.com'

        self.assertRaises(forms.ValidationError, register_form.clean_email)

    @mock.patch('tethys_portal.forms.validate_password')
    def test_RegisterForm_clean_password2(self, mock_vp):
        register_data = {'username': 'user1', 'email': 'foo@aquaveo.com', 'password1': 'abc123',
                         'password2': 'abc123', 'captcha_0': self.hashkey, 'captcha_1': self.response}

        register_form = RegisterForm(data=register_data)

        # Check if form is valid and to generate cleaned_data
        self.assertTrue(register_form.is_valid())

        ret = register_form.clean_password2()

        mock_vp.assert_called_with('abc123')

        self.assertEqual('abc123', ret)

    def test_RegisterForm_clean_password2_diff(self):
        register_data = {'username': 'user1', 'email': 'foo@aquaveo.com', 'password1': 'abcd123',
                         'password2': 'abc123', 'captcha_0': self.hashkey, 'captcha_1': self.response}

        register_form = RegisterForm(data=register_data)

        # use is_valid to get cleaned_data attributes
        self.assertFalse(register_form.is_valid())

        # is_valid removed cleaned_data password2, need to update
        register_form.cleaned_data['password2'] = 'abc123'

        self.assertRaises(forms.ValidationError, register_form.clean_password2)

    def test_RegisterForm_save(self):
        register_data = {'username': 'user1', 'email': 'foo@aquaveo.com', 'password1': 'abc123',
                         'password2': 'abc123', 'captcha_0': self.hashkey, 'captcha_1': self.response}

        register_form = RegisterForm(data=register_data)

        ret = register_form.save()

        # Also try to get from database after it's saved
        ret_database = User.objects.get(username='user1')

        # Check result
        self.assertIsInstance(ret, User)
        self.assertIsInstance(ret_database, User)
        self.assertEqual('user1', ret.username)
        self.assertEqual('user1', ret_database.username)

    def test_UserSettingsForm(self):
        user_settings_data = {'first_name': 'fname', 'last_name': 'lname', 'email': 'user@aquaveo.com'}
        user_settings_form = UserSettingsForm(data=user_settings_data)
        self.assertTrue(user_settings_form.is_valid())

    # UserPasswordChange Form

    def test_UserPasswordChangeForm_valid(self):
        user_password_change_data = {'old_password': 'glass_onion', 'new_password1': 'pass2', 'new_password2': 'pass2'}
        user_password_change_form = UserPasswordChangeForm(self.user, data=user_password_change_data)
        self.assertTrue(user_password_change_form.is_valid())

    def test_UserPasswordChangeForm_clean_old_password(self):
        user_password_change_data = {'old_password': 'glass_onion', 'new_password1': 'pass2', 'new_password2': 'pass2'}
        user_password_change_form = UserPasswordChangeForm(self.user, data=user_password_change_data)

        self.assertTrue(user_password_change_form.is_valid())

        ret = user_password_change_form.clean_old_password()

        self.assertEqual('glass_onion', ret)

    def test_UserPasswordChangeForm_clean_old_password_invalid(self):
        user_password_change_data = {'old_password': 'abc123', 'new_password1': 'pass2', 'new_password2': 'pass2'}
        user_password_change_form = UserPasswordChangeForm(self.user, data=user_password_change_data)

        # is_valid to get cleaned_data
        self.assertFalse(user_password_change_form.is_valid())

        # is_valid removes old_password, add it back for testing
        user_password_change_form.cleaned_data['old_password'] = 'abc123'

        self.assertRaises(forms.ValidationError,  user_password_change_form.clean_old_password)

    @mock.patch('tethys_portal.forms.validate_password')
    def test_UserPasswordChangeForm_clean_new_password2(self, mock_vp):
        user_password_change_data = {'old_password': 'glass_onion', 'new_password1': 'pass2', 'new_password2': 'pass2'}
        user_password_change_form = UserPasswordChangeForm(self.user, data=user_password_change_data)

        self.assertTrue(user_password_change_form.is_valid())

        ret = user_password_change_form.clean_new_password2()
        self.assertEqual('pass2', ret)

        mock_vp.assert_called_with('pass2')

    def test_UserPasswordChangeForm_clean_new_password2_diff(self):
        user_password_change_data = {'old_password': 'glass_onion', 'new_password1': 'pass1', 'new_password2': 'pass2'}
        user_password_change_form = UserPasswordChangeForm(self.user, data=user_password_change_data)

        # run is_valid to get cleaned_data
        self.assertFalse(user_password_change_form.is_valid())

        # is_valid removes new_password2 because it's different from pass1, we update here to run the test
        user_password_change_form.cleaned_data['new_password2'] = 'pass2'

        self.assertRaises(forms.ValidationError, user_password_change_form.clean_new_password2)

    def test_UserPasswordChangeForm_save(self):
        # password hash before save
        ret_old = User.objects.get(username='user_exist')
        old_pass = ret_old.password

        # Update new password
        user_password_change_data = {'old_password': 'glass_onion', 'new_password1': 'pass2', 'new_password2': 'pass2'}
        user_password_change_form = UserPasswordChangeForm(self.user, data=user_password_change_data)

        # run is_valid to get cleaned_data attributes.
        self.assertTrue(user_password_change_form.is_valid())

        user_password_change_form.save()

        # Also try to get from database after it's saved
        ret_new = User.objects.get(username='user_exist')
        new_pass = ret_new.password

        # Check result
        self.assertIsInstance(ret_new, User)
        self.assertNotEqual(old_pass, new_pass)
