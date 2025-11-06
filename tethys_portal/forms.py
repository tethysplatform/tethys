"""
********************************************************************************
* Name: forms.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

from pathlib import Path
from shutil import get_unpack_formats

from django import forms
from django.core.validators import RegexValidator, FileExtensionValidator
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.utils.safestring import mark_safe

from django.conf import settings

from tethys_cli.scaffold_commands import get_random_color, APP_PREFIX


def get_captcha():
    if getattr(settings, "ENABLE_CAPTCHA", False):
        if getattr(settings, "RECAPTCHA_PRIVATE_KEY", "") and getattr(
            settings, "RECAPTCHA_PUBLIC_KEY", ""
        ):
            from django_recaptcha.fields import ReCaptchaField
            from django_recaptcha.widgets import ReCaptchaV2Checkbox

            return ReCaptchaField(label="", widget=ReCaptchaV2Checkbox())
        else:
            from captcha.fields import CaptchaField

            return CaptchaField(label="")
    else:
        return None


class LoginForm(forms.Form):
    username = forms.RegexField(
        label="",
        max_length=150,
        regex=r"^[\w.@+-]+$",
        error_messages={
            "invalid": "This value may contain only letters, numbers and @/./+/-/_ characters."
        },
        widget=forms.TextInput(
            attrs={"placeholder": "Username", "autofocus": "autofocus"}
        ),
    )

    password = forms.CharField(
        label="",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password", "autocomplete": "off"}
        ),
    )

    captcha = get_captcha()


class RegisterForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """

    error_messages = {
        "duplicate_username": "A user with that username already exists.",
        "password_mismatch": "The two password fields didn't match.",
        "duplicate_email": "A user with this email already exists.",
    }

    username = forms.RegexField(
        label="",
        max_length=150,
        regex=r"^[\w.@+-]+$",
        error_messages={
            "invalid": "This value may contain only letters, numbers and @/./+/-/_ characters."
        },
        widget=forms.TextInput(
            attrs={"placeholder": "Username", "autofocus": "autofocus"}
        ),
    )

    email = forms.CharField(
        label="",
        max_length=254,
        widget=forms.EmailInput(attrs={"placeholder": "Email"}),
    )

    password1 = forms.CharField(
        label="",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password", "autocomplete": "off"}
        ),
    )

    password2 = forms.CharField(
        label="",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Confirm Password", "autocomplete": "off"}
        ),
    )

    captcha = get_captcha()

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
            self.error_messages["duplicate_username"],
            code="duplicate_username",
        )

    def clean_email(self):
        # Enforce unique email addresses for password recovery.
        email = self.cleaned_data["email"]

        try:
            User._default_manager.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(
            self.error_messages["duplicate_email"],
            code="duplicate_email",
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        validate_password(password2)
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserSettingsForm(forms.ModelForm):
    """
    A form for modifying user settings.
    """

    first_name = forms.CharField(
        max_length=30,
        label="First Name:",
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "", "class": "form-control", "autofocus": "autofocus"}
        ),
    )

    last_name = forms.CharField(
        max_length=150,
        label="Last Name:",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "", "class": "form-control"}),
    )

    email = forms.EmailField(
        max_length=254,
        label="Email:",
        widget=forms.EmailInput(attrs={"placeholder": "", "class": "form-control"}),
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")


class UserPasswordChangeForm(forms.Form):
    """
    A form that lets a user change their password by entering their old one.
    """

    error_messages = {
        "password_mismatch": "The two password fields didn't match.",
        "password_incorrect": "Your old password was entered incorrectly. Please enter it again.",
    }

    old_password = forms.CharField(
        label="",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Old Password",
                "autofocus": "autofocus",
                "autocomplete": "off",
            }
        ),
    )

    new_password1 = forms.CharField(
        label="",
        widget=forms.PasswordInput(
            attrs={"placeholder": "New Password", "autocomplete": "off"}
        ),
    )

    new_password2 = forms.CharField(
        label="",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Confirm New Password", "autocomplete": "off"}
        ),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                self.error_messages["password_incorrect"],
                code="password_incorrect",
            )
        return old_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages["password_mismatch"],
                    code="password_mismatch",
                )
        validate_password(password2)
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data["new_password1"])
        if commit:
            self.user.save()
        return self.user


class SsoTenantForm(forms.Form):
    tenant = forms.RegexField(
        label="",
        max_length=30,
        required=True,
        regex=getattr(settings, "SSO_TENANT_REGEX", r"^[\w\s_-]+$"),
        error_messages={"invalid": "Invalid characters provided."},
        widget=forms.TextInput(
            attrs={
                "placeholder": getattr(settings, "SSO_TENANT_ALIAS", "Tenant").title(),
                "autofocus": "autofocus",
            }
        ),
    )

    remember = forms.BooleanField(
        label="Remember for next time",
        required=False,
    )


class AppImportForm(forms.Form):
    """
    A form for importing an app from disk or github
    """

    git_url = forms.CharField(
        max_length=500,
        label="Git URL",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "https://github.com/space/tethysapp-example_app.git",
                "class": "form-control",
            }
        ),
        validators=[
            RegexValidator(
                r"^https://github.com/.*\.git$",
                'The URL must start with "https://github.com" and end with ".git"',
            ),
        ],
    )

    zip_file = forms.FileField(
        label="Archive File",
        required=False,
        validators=[
            FileExtensionValidator(
                [
                    x[1:]
                    for x in sum(
                        [extensions for name, extensions, _ in get_unpack_formats()], []
                    )
                ]
            )
        ],
    )

    def clean(self):
        if self.cleaned_data.get("git_url") and self.cleaned_data.get("zip_file"):
            raise forms.ValidationError(
                "Input provided for both Git URL and Archive File. Please only specify one or the other."
            )


class AppScaffoldForm(forms.Form):
    """
    A form for scaffolding an app.
    """

    scaffold_template = forms.ChoiceField(
        choices=[
            ("default", "Standard"),
            ("component", "Component (Beta)"),
            ("reactjs", "ReactJS (Beta)"),
        ]
    )

    project_name = forms.CharField(
        max_length=50,
        label="Project Name:",
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "my_app",
                "class": "form-control",
                "autofocus": "autofocus",
            }
        ),
        validators=[
            RegexValidator(
                r"^\w+$",
                "The project name must contain only letters, numbers, and underscores.",
            ),
            lambda v: (Path.cwd() / f"{APP_PREFIX}-{v}").exists()
            and exec(
                "raise(forms.ValidationError('A project already exists with that name', code='project_exists',))"
            ),
        ],
    )

    app_name = forms.CharField(
        max_length=100,
        label="App Name:",
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "My App", "class": "form-control"}
        ),
        validators=[
            RegexValidator(
                r"^[a-zA-Z0-9\s]+$",
                "The project name must contain only letters, numbers, and spaces.",
            ),
        ],
    )

    description = forms.CharField(
        max_length=500,
        label="App Description:",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "", "class": "form-control"}),
    )

    app_theme_color = forms.CharField(
        max_length=7,
        label="App Theme Color:",
        required=False,
        widget=forms.TextInput(
            attrs={
                "type": "color",
                "value": get_random_color(),
                "class": "form-control",
            }
        ),
    )

    tags = forms.CharField(
        max_length=100,
        label="Tags:",
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "test,app,hydrology", "class": "form-control"}
        ),
        validators=[
            RegexValidator(
                regex="([^,]+,? ?)+",
                message="Tags must be a comma-separated list of strings.",
            ),
        ],
    )

    author = forms.CharField(
        max_length=30,
        label="Author Name:",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "", "class": "form-control"}),
    )

    author_email = forms.EmailField(
        max_length=254,
        label="Author Email:",
        required=False,
        widget=forms.EmailInput(attrs={"placeholder": "", "class": "form-control"}),
    )

    license = forms.CharField(
        max_length=30,
        label=mark_safe(
            "License: (View valid license identifiers <a target='_page' href='https://spdx.org/licenses/'>here</a>)"
        ),
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "", "class": "form-control"}),
    )
