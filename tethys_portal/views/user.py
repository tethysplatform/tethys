from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.contrib import messages

from tethys_portal.forms import UserSettingsForm, UserPasswordChangeForm

@login_required()
def profile(request, username=None):
    """
    Handle the profile view. Profiles could potentially be publicly accessible.
    """
    # The profile should display information about the user that is given in the url.
    # However, the template will hide certain information if the username is not the same
    # as the username of the user that is accessing the page.
    context_user = User.objects.get(username=username)
    context = {'context_user': context_user}
    return render(request, 'tethys_portal/user/profile.html', context)

@login_required()
def settings(request, username=None):
    """
    Handle the settings view. Access to change settings are not publicly accessible
    """
    # Get the user object from model
    request_user = request.user

    # Users are not allowed to make changes to other users settings
    if request_user.username != username:
        messages.warning(request, "You are not allowed to change other users' settings.")
        return redirect('user:profile', username=request_user.username)

    if request.method == 'POST' and 'user-settings-submit' in request.POST:
        # Create a form populated with request data
        form = UserSettingsForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']

            # Update the User Model
            request_user.first_name = first_name
            request_user.last_name = last_name
            request_user.email = email

            # Save changes
            request_user.save()

            # Redirect
            return redirect('user:profile', username=username)
    else:
        # Create a form populated with data from the instance user
        form = UserSettingsForm(instance=request_user)

    # Create template context object
    context = {'form': form,
               'context_user': request.user}

    return render(request, 'tethys_portal/user/settings.html', context)

@login_required()
def change_password(request, username=None):
    # Get the user object from model
    request_user = request.user

    # Users are not allowed to make changes to other users settings
    if request_user.username != username:
        messages.warning(request, "You are not allowed to change other users' settings.")
        return redirect('user:profile', username=request_user.username)

    # Handle form
    if request.method == 'POST' and 'change-password-submit' in request.POST:
        # Create a form populated with request data
        form = UserPasswordChangeForm(user=request.user, data=request.POST)

        if form.is_valid():
            # Validate the old and new passwords
            form.clean_old_password()
            form.clean_new_password2()

            # If no exceptions raised to here, then the old password is valid and the new passwords match.
            # Save the new passwords to the database.
            form.save()

            # Return to the settings page
            return redirect('user:settings', username=username)

        else:
            pass

    else:
        # Create a form populated with data from the instance user
        form = UserPasswordChangeForm(user=request_user)

    # Create template context object
    context = {'form': form}

    return render(request, 'tethys_portal/user/change_password.html', context)