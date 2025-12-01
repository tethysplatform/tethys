from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django.templatetags.static import static
from django.shortcuts import reverse
from django.conf import settings

from tethys_apps.exceptions import TethysAppSettingNotAssigned
from tethys_portal.optional_dependencies import optional_import
from rest_framework_simplejwt.tokens import RefreshToken

# Optional dependencies
get_gravatar_url = optional_import(
    "get_gravatar_url", from_module="django_gravatar.helpers"
)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_token(request):
    user = request.user
    if not user.is_authenticated:
        return Response(
            {
                "access": None,
                "refresh": None,
            }
        )

    refresh = RefreshToken.for_user(user)
    return Response(
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
    return Response(response_data)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_app(request, app):
    from tethys_apps.models import TethysApp

    package = app.replace("-", "_")

    try:
        app_obj = TethysApp.objects.get(package=package)
    except TethysApp.DoesNotExist:
        return Response({"error": f'Could not find app "{app}".'})

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

    return Response(metadata)
