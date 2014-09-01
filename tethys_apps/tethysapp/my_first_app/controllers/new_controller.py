from django.shortcuts import render


def index(request):
    return render(request, 'my_first_app/new_template.html', {})


def hello(request, name):
    context = {'name': name}
    return render(request, 'my_first_app/hello.html', context)
