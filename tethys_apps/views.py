from django.shortcuts import render, HttpResponse


def index(request):
    context = {}
    return HttpResponse("Hello World")
