from django.shortcuts import render


def home(request):
    # context = {"flash_messages": [
    #     {"category": "success",
    #      "text": "This is a flash message"},
    #     {"category": "warning",
    #      "text": "This is a flash message"},
    #     {"category": "info",
    #      "text": "This is a flash message"},
    #     {"category": "danger",
    #      "text": "This is a flash message"},
    # ]}
    return render(request, 'tethys_site/home.html', {})