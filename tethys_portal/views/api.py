from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.templatetags.static import static
from django.shortcuts import reverse
from django.views.decorators.csrf import ensure_csrf_cookie

from tethys_apps.exceptions import TethysAppSettingNotAssigned
from tethys_portal.utilities import json_serializer


def get_csrf(request):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    return HttpResponse(headers={"X-CSRFToken": get_token(request)})


@ensure_csrf_cookie
def get_session(request):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    return JsonResponse({"isAuthenticated": True})


def get_whoami(request):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)

    return JsonResponse(
        {
            "username": request.user.username,
            "firstName": request.user.first_name,
            "lastName": request.user.last_name,
            "email": request.user.email,
            "isAuthenticated": request.user.is_authenticated,
            "isStaff": request.user.is_staff,
        }
    )


def get_app(request, app):
    from tethys_apps.models import TethysApp

    package = app.replace("-", "_")

    try:
        app = TethysApp.objects.get(package=package)
    except TethysApp.DoesNotExist:
        return JsonResponse({"error": f'Could not find app "{app}".'})

    metadata = {
        "title": app.name,
        "description": app.description,
        "tags": app.tags,
        "package": app.package,
        "urlNamespace": app.url_namespace,
        "color": app.color,
        "icon": static(app.icon),
        "exitUrl": reverse("app_library"),
        "rootUrl": reverse(app.index_url),
        "settingsUrl": f'{reverse("admin:index")}tethys_apps/tethysapp/{ app.id }/change/',
    }

    if request.user.is_authenticated:
        metadata["customSettings"] = dict()
        for s in app.custom_settings:
            if s.type_custom_setting != "SIMPLE":
                continue

            v = None
            try:
                v = s.get_value()
            except TethysAppSettingNotAssigned:
                pass

            metadata["customSettings"][s.name] = {
                "type": s.type,
                "value": v,
            }

    return JsonResponse(
        metadata,
        json_dumps_params={"default": json_serializer}
    )
