from django.shortcuts import render

def home(request):
    return render(request, 'tethys_site/home.html', {})