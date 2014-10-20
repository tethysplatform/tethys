from django.shortcuts import HttpResponse, render


def home(request):

    context = {}
    return render(request, 'tethys_portal/developer/home.html', context)