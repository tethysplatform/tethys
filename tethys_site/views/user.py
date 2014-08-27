from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


from django.contrib import messages

from tethys_site.forms import UserSettingsForm

@login_required()
def profile(request, username=None):
    return render(request, 'tethys_site/user/profile.html', {})

@login_required()
def settings(request, username=None):
    # Get the user object from model
    user = User.objects.get(username=username)

    if request.method == 'POST' and 'user-settings-submit' in request.POST:
        # Create a form populated with request data
        form = UserSettingsForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']

            # Update the User Model
            user.first_name = first_name
            user.last_name = last_name
            user.email = email

            # Save changes
            user.save()

            # Redirect
            return redirect('user:profile', username=username)
    else:
        # Create a form populated with data from the instance user
        form = UserSettingsForm(instance=user)

    # Create template context object
    context = {'form': form}

    return render(request, 'tethys_site/user/settings.html', context)