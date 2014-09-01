from django.shortcuts import render


def index(request):
    # Get App Definition
    app_definition = {'name': 'My First App',
                      'index': 'my-first-app'}

    app_name = app_definition['name']
    app_index = app_definition['index']

    # Create context
    context = {'app_name', app_name,
               'app_index', app_index}

    return render(request, 'my_first_app/index.html', context)


def form(request):
    # Set default value for username
    username = ''

    # Evaluate form if submitted
    if 'username-submit' in request.POST:
        username = request.POST['username-input']

    context = {'username': username}

    return render(request, 'my_first_app/form.html', context)



