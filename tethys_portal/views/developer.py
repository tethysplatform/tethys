from django.shortcuts import HttpResponse, render


def home(request):

    context = {}
    return render(request, 'tethys_site/developer/home.html', context)