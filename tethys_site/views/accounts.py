from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from tethys_site.forms import LoginForm, RegisterForm


def login_view(request):
    """
    Handle login
    """
    # messages.debug(request, 'Debug')
    # messages.error(request, 'Error')
    # messages.warning(request, 'Warning')
    # messages.success(request, 'Success')
    # messages.info(request, 'Info')

    if request.method == 'POST' and 'login-submit' in request.POST:

        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Authenticate
            user = authenticate(username=username, password=password)

            if user is not None:
                # The password has been verified for the user
                if user.is_active:
                    # The user is valid, active, and authenticated, so login in the user
                    login(request, user)

                    # Redirect to user home
                    return redirect('home')
                else:
                    # The password is valid, but the user account has been disabled
                    # Return a disabled account 'error' message
                    pass
            else:
                # User was not authenticated, return errors
                pass

    else:
        form = LoginForm()

    context = {'form': form}

    return render(request, 'tethys_site/accounts/login.html', context)


def register(request):
    """
    Handle new user registration
    """
    if request.method == 'POST' and 'register-submit' in request.POST:

        form = RegisterForm(request.POST)

        if form.is_valid():
            # Validate username and password using form methods
            username = form.clean_username()
            password = form.clean_password2()

            # If you got here, then the username is unique and the passwords match, commit the new user to database
            form.save()

            # Authenticate the new user
            user = authenticate(username=username, password=password)

            if user is not None:
                # The password has been verified for the user
                if user.is_active:
                    # The user is valid, active, and authenticated, so login in the user
                    login(request, user)

                    # Redirect to user home
                    return redirect('home')
                else:
                    # The password is valid, but the user account has been disabled
                    # Return a disabled account 'error' message
                    pass
            else:
                # User was not authenticated, return errors
                pass

    else:
        form = RegisterForm()

    context = {'form': form}
    return render(request, 'tethys_site/accounts/register.html', context)


def logout_view(request):
    logout(request)
    return redirect('home')