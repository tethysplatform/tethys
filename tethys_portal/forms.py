"""
********************************************************************************
* Name: forms.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
from django import forms
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.RegexField(label='', max_length=30,
                                regex=r'^[\w.@+-]+$',
                                error_messages={
                                    'invalid': "This value may contain only letters, numbers and @/./+/-/_ characters."},
                                widget=forms.TextInput(attrs={'placeholder': 'Username',
                                                              'autofocus': 'autofocus'}
                                )
    )

    password = forms.CharField(label='',
                               widget=forms.PasswordInput(
                                   attrs={'placeholder': 'Password'}
                               )
    )


class RegisterForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'duplicate_username': "A user with that username already exists.",
        'password_mismatch': "The two password fields didn't match.",
        'duplicate_email': "A user with this email already exists."
    }

    username = forms.RegexField(label='', max_length=30,
                                regex=r'^[\w.@+-]+$',
                                error_messages={
                                    'invalid': "This value may contain only letters, numbers and @/./+/-/_ characters."},
                                widget=forms.TextInput(attrs={'placeholder': 'Username',
                                                              'autofocus': 'autofocus'}
                                )
    )

    email = forms.CharField(label='',
                            max_length=30,
                            widget=forms.EmailInput(attrs={'placeholder': 'Email'}
                            )
    )

    password1 = forms.CharField(label='',
                                widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
    )

    password2 = forms.CharField(label='',
                                widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
    )

    class Meta:
        model = User
        fields = ("username", "email")

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            User._default_manager.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(
            self.error_messages['duplicate_username'],
            code='duplicate_username',
        )

    def clean_email(self):
        # Enforce unique email addresses for password recovery.
        email = self.cleaned_data["email"]

        try:
            User._default_manager.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(
            self.error_messages['duplicate_email'],
            code='duplicate_email',
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserSettingsForm(forms.ModelForm):
    """
    A form for modifying user settings.
    """
    first_name = forms.CharField(max_length=30,
                                 label='',
                                 required=False,
                                 widget=forms.TextInput(
                                     attrs={'placeholder': '',
                                            'class': 'form-control',
                                            'autofocus': 'autofocus'}
                                 )
    )

    last_name = forms.CharField(max_length=30,
                                label='',
                                required=False,
                                widget=forms.TextInput(
                                    attrs={'placeholder': '',
                                           'class': 'form-control'}
                                )
    )

    email = forms.EmailField(max_length=30,
                             label='Email:',
                             widget=forms.EmailInput(
                                 attrs={'placeholder': '',
                                        'class': 'form-control'}
                             )
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")


class UserPasswordChangeForm(forms.Form):
    """
    A form that lets a user change their password by entering their old one.
    """
    error_messages = {
        'password_mismatch': "The two password fields didn't match.",
        'password_incorrect': "Your old password was entered incorrectly. Please enter it again.",
    }

    old_password = forms.CharField(label="",
                                   widget=forms.PasswordInput(
                                       attrs={'placeholder': 'Old Password',
                                              'autofocus': 'autofocus'}
                                   )
    )

    new_password1 = forms.CharField(label="",
                                    widget=forms.PasswordInput(
                                        attrs={'placeholder': 'New Password'}
                                    )
    )

    new_password2 = forms.CharField(label="",
                                    widget=forms.PasswordInput(
                                        attrs={'placeholder': 'Confirm New Password'}
                                    )
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(UserPasswordChangeForm, self).__init__(*args, **kwargs)

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user
