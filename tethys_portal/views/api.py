from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.templatetags.static import static
from django.shortcuts import reverse
from django.views.decorators.csrf import ensure_csrf_cookie


def get_csrf(request):
    if not request.user.is_authenticated:
        return JsonResponse({'isAuthenticated': False})
    response = JsonResponse({'detail': 'CSRF cookie set'})
    response['X-CSRFToken'] = get_token(request)
    return response


@ensure_csrf_cookie
def get_session(request):
    if not request.user.is_authenticated:
        return JsonResponse({'isAuthenticated': False})

    return JsonResponse({'isAuthenticated': True})


def get_whoami(request):
    if not request.user.is_authenticated:
        return JsonResponse({'isAuthenticated': False})

    return JsonResponse({
        'username': request.user.username,
        'firstName': request.user.first_name,
        'lastName': request.user.last_name,
        'email': request.user.email,
        'isAuthenticated': True,
        'isStaff': request.user.is_staff,
    })


def get_app(request, app):
    from tethys_apps.models import TethysApp
    package = app.replace('-', '_')

    try:
        app = TethysApp.objects.get(package=package)
    except:
        return(JsonResponse({'error': f'Could not find app "{app}".'}))

    metadata = {
        'title': app.name,
        'description': app.description,
        'tags': app.tags,
        'package': app.package,
        'urlNamespace': app.url_namespace,
        'color': app.color,
        'icon': static(app.icon),
        'exitUrl': '/apps/',
        'rootUrl': reverse(app.index_url),
        'settingsUrl': f'{reverse("admin:index")}tethys_apps/tethysapp/{ app.id }/change/',
    }
    return(JsonResponse(metadata))
