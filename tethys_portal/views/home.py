from django.shortcuts import render


def home(request):
    return render(request, 'tethys_portal/home.html', {})