from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from django.http import HttpResponseNotAllowed, HttpResponse, JsonResponse
from django.templatetags.static import static
from django.shortcuts import reverse
from django.conf import settings
from django.contrib.auth import authenticate
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie

from tethys_apps.exceptions import TethysAppSettingNotAssigned
from tethys_portal.optional_dependencies import optional_import
from tethys_portal.utilities import json_serializer

import warnings

# Optional dependencies
get_gravatar_url = optional_import(
    "get_gravatar_url", from_module="django_gravatar.helpers"
)


def get_csrf(request):
    warnings.warn(
        "get_csrf is deprecated and will be removed in a future tethys version. Use the get_jwt_token GET endpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if not request.user.is_authenticated and not settings.ENABLE_OPEN_PORTAL:
        return HttpResponse("Unauthorized", status=401)
    return HttpResponse(headers={"X-CSRFToken": get_token(request)})


@ensure_csrf_cookie
def get_session(request):
    warnings.warn(
        "get_session is deprecated and will be removed in a future tethys version. Use the get_jwt_token GET endpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if not request.user.is_authenticated and not settings.ENABLE_OPEN_PORTAL:
        return HttpResponse("Unauthorized", status=401)
    return JsonResponse({"isAuthenticated": True})


@api_view(["POST", "GET"])
@permission_classes([AllowAny])
def get_jwt_token(request):
    if request.method == "POST":
        if not getattr(settings, "ALLOW_JWT_BASIC_AUTHENTICATION", False):
            return HttpResponseNotAllowed(
                ["GET"], "JWT basic authentication is disabled."
            )
        username = request.data.get("username")
        password = request.data.get("password")
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                return JsonResponse(
                    {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                    }
                )
            else:
                return JsonResponse(
                    {"access": None, "refresh": None, "error": "Invalid credentials."},
                )

        return JsonResponse(
            {
                "access": None,
                "refresh": None,
                "error": "Username and password are required for authentication.",
            },
        )

    # Otherwise, use session user
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"access": None, "refresh": None})
    refresh = RefreshToken.for_user(user)
    return JsonResponse(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def get_whoami(request):
    user = request.user
    response_data = {
        "username": user.username,
        "isAuthenticated": user.is_authenticated,
        "isStaff": user.is_staff,
    }
    if not user.is_anonymous:
        response_data["firstName"] = user.first_name
        response_data["lastName"] = user.last_name
        response_data["email"] = user.email
        try:
            email = user.email if user.email else "tethys@example.com"
            gravatar_url = get_gravatar_url(email, size=80)
            response_data["gravatarUrl"] = gravatar_url
        except Exception:
            pass
    return JsonResponse(response_data)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_app(request, app):
    from tethys_apps.models import TethysApp

    package = app.replace("-", "_")

    try:
        app_obj = TethysApp.objects.get(package=package)
    except TethysApp.DoesNotExist:
        return JsonResponse({"error": f'Could not find app "{app}".'})

    metadata = {
        "title": app_obj.name,
        "description": app_obj.description,
        "tags": app_obj.tags,
        "package": app_obj.package,
        "urlNamespace": app_obj.url_namespace,
        "color": app_obj.color,
        "icon": static(app_obj.icon),
        "exitUrl": (
            reverse("app_library")
            if settings.MULTIPLE_APP_MODE
            else reverse(app_obj.index_url)
        ),
        "rootUrl": reverse(app_obj.index_url),
        "settingsUrl": f'{reverse("admin:index")}tethys_apps/tethysapp/{app_obj.id}/change/',
    }

    if request.user.is_authenticated:
        metadata["customSettings"] = dict()
        for s in app_obj.custom_settings:
            if not s.include_in_api:
                continue
            v = None
            try:
                v = s.get_value()
            except TethysAppSettingNotAssigned:
                pass
            metadata["customSettings"][s.name] = {
                "type": (
                    s.type
                    if s.type_custom_setting == "SIMPLE"
                    else s.type_custom_setting
                ),
                "value": v,
            }

    return JsonResponse(metadata, json_dumps_params={"default": json_serializer})
