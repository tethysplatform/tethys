from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required()
def profile(request, username=None):
    return render(request, 'tethys_site/user/profile.html', {})

@login_required()
def settings(request, username=None):
    return render(request, 'tethys_site/user/settings.html', {})