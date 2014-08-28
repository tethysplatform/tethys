from django import forms
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(max_length=30,
                               label='',
                               widget=forms.TextInput(
                                   attrs={'placeholder': 'Username'}
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
    }

    username = forms.RegexField(label='', max_length=30,
        regex=r'^[\w.@+-]+$',
        error_messages={'invalid': "This value may contain only letters, numbers and @/./+/-/_ characters."},
        widget=forms.TextInput(attrs={'placeholder': 'Username'}),
    )

    password1 = forms.CharField(label='',
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
    )

    password2 = forms.CharField(label='',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
    )

    class Meta:
        model = User
        fields = ("username",)

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
                                            'class': 'form-control'}
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
                             required=False,
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

    current_password = forms.CharField(required=False,
                                       label='',
                                       widget=forms.PasswordInput(
                                           attrs={'placeholder': 'Old Password'}
                                       ))

    password = forms.CharField(required=False,
                               label='',
                               widget=forms.PasswordInput(
                                   attrs={'placeholder': 'New Password'}
                               ))

    confirm_password = forms.CharField(required=False,
                                       label='',
                                       widget=forms.PasswordInput(
                                           attrs={'placeholder': 'Confirm New Password'}
                                       ))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(UserPasswordChangeForm, self).__init__(*args, **kwargs)

    def clean_current_password(self):
        # If the user entered the current password, make sure it's right
        if self.cleaned_data['current_password'] and not self.user.check_password(self.cleaned_data['current_password']):
            raise forms.ValidationError('This is not your current password. Please try again.')

        # If the user entered the current password, make sure they entered the new passwords as well
        if self.cleaned_data['current_password'] and not (self.cleaned_data['password'] or self.cleaned_data['confirm_password']):
            raise forms.ValidationError('Please enter a new password and a confirmation to update.')

        return self.cleaned_data['current_password']

    def clean_confirm_password(self):
        # Make sure the new password and confirmation match
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('confirm_password')

        if password1 != password2:
            raise forms.ValidationError("Your passwords didn't match. Please try again.")

        return self.cleaned_data.get('confirm_password')

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['password'])
        if commit:
            self.user.save()
        return self.user
