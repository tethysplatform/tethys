import re
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.test import override_settings
import warnings

from unittest.mock import patch, MagicMock
import pytest


@pytest.fixture
def user(db):
    user = User.objects.create_user(username="foo")
    yield user
    user.delete()


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_get_csrf_not_authenticated(client):
    """Test get_csrf API endpoint not authenticated and check deprecation warning."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        response = client.get(reverse("api:get_csrf"))
        assert response.status_code == 401
        assert any(item.category == DeprecationWarning for item in w)
        assert any(
            "get_csrf is deprecated and will be removed in a future tethys version"
            in str(item.message)
            for item in w
        )


@override_settings(ENABLE_OPEN_PORTAL=True, SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_get_csrf_not_authenticated_but_open_portal(client, user):
    """Test get_csrf API endpoint not authenticated and check deprecation warning."""
    client.force_login(user)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        response = client.get(reverse("api:get_csrf"))
        assert response.status_code == 200
        assert isinstance(response, HttpResponse)
        assert "X-CSRFToken" in response.headers
        assert any(item.category == DeprecationWarning for item in w)
        assert any(
            "get_csrf is deprecated and will be removed in a future tethys version"
            in str(item.message)
            for item in w
        )


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
def test_get_csrf_authenticated(client, user):
    """Test get_csrf API endpoint authenticated and check deprecation warning."""
    client.force_login(user)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        response = client.get(reverse("api:get_csrf"))
        assert response.status_code == 200
        assert isinstance(response, HttpResponse)
        assert "X-CSRFToken" in response.headers
        assert any(item.category == DeprecationWarning for item in w)
        assert any(
            "get_csrf is deprecated and will be removed in a future tethys version"
            in str(item.message)
            for item in w
        )


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_get_session_not_authenticated(client):
    """Test get_session API endpoint not authenticated and check deprecation warning."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        response = client.get(reverse("api:get_session"))
        assert response.status_code == 401
        assert any(item.category == DeprecationWarning for item in w)
        assert any(
            "get_session is deprecated and will be removed in a future tethys version"
            in str(item.message)
            for item in w
        )


@override_settings(ENABLE_OPEN_PORTAL=True, SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_get_session_not_authenticated_but_open_portal(client):
    """Test get_session API endpoint not authenticated and check deprecation warning."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        response = client.get(reverse("api:get_session"))
        assert response.status_code == 200
        assert isinstance(response, JsonResponse)
        json = response.json()
        assert "isAuthenticated" in json
        assert json["isAuthenticated"]
        assert any(item.category == DeprecationWarning for item in w)
        assert any(
            "get_session is deprecated and will be removed in a future tethys version"
            in str(item.message)
            for item in w
        )


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
def test_get_session_authenticated(client, user):
    """Test get_session API endpoint authenticated and check deprecation warning."""
    client.force_login(user)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        response = client.get(reverse("api:get_session"))
        assert response.status_code == 200
        assert isinstance(response, JsonResponse)
        json = response.json()
        assert "isAuthenticated" in json
        assert json["isAuthenticated"]
        assert any(item.category == DeprecationWarning for item in w)
        assert any(
            "get_session is deprecated and will be removed in a future tethys version"
            in str(item.message)
            for item in w
        )


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_get_whoami_not_authenticated(client):
    """Test get_whoami API endpoint not authenticated."""
    response = client.get(reverse("api:get_whoami"))
    assert response.status_code == 200
    assert isinstance(response, JsonResponse)
    json = response.json()
    assert json == {"username": "", "isAuthenticated": False, "isStaff": False}


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
def test_get_whoami_authenticated(client, user):
    """Test get_whoami API endpoint authenticated."""
    client.force_login(user)
    response = client.get(reverse("api:get_whoami"))
    assert response.status_code == 200
    assert isinstance(response, JsonResponse)
    json = response.json()
    assert "username" in json
    assert "firstName" in json
    assert "lastName" in json
    assert "email" in json
    assert "isAuthenticated" in json
    assert "isStaff" in json
    assert "gravatarUrl" in json
    assert "foo" == json["username"]
    assert json["isAuthenticated"]


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
def test_get_whoami_authenticated_gravatar_exception(client, user):
    """Test get_whoami API endpoint when gravatar fails."""
    from unittest.mock import patch

    client.force_login(user)
    with patch(
        "tethys_portal.views.api.get_gravatar_url",
        side_effect=Exception("Gravatar error"),
    ):
        response = client.get(reverse("api:get_whoami"))
        assert response.status_code == 200
        assert isinstance(response, JsonResponse)
        json = response.json()
        assert "username" in json
        assert "firstName" in json
        assert "lastName" in json
        assert "email" in json
        assert "isAuthenticated" in json
        assert "isStaff" in json
        assert "gravatarUrl" not in json
        assert "foo" == json["username"]
        assert json["isAuthenticated"]


@override_settings(MULTIPLE_APP_MODE=True)
@override_settings(STATIC_URL="/static")
@override_settings(LOGIN_URL="/accounts/slogin/")
@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_get_app_valid_id(client, test_app, user):
    """Test get_app API endpoint with valid app id."""
    response = client.get(reverse("api:get_app", kwargs={"app": "test-app"}))
    assert response.status_code == 200
    assert isinstance(response, JsonResponse)
    json = response.json()
    assert "title" in json
    assert "description" in json
    assert "tags" in json
    assert "package" in json
    assert "urlNamespace" in json
    assert "color" in json
    assert "icon" in json
    assert "exitUrl" in json
    assert "rootUrl" in json
    assert "settingsUrl" in json
    assert "Test App" == json["title"]
    assert "Place a brief description of your app here." == json["description"]
    assert "" == json["tags"]
    assert "test_app" == json["package"]
    assert "test_app" == json["urlNamespace"]
    assert "#2c3e50" == json["color"]
    assert "/static/test_app/images/icon.gif" == json["icon"]
    assert "/apps/" == json["exitUrl"]
    assert "/apps/test-app/" == json["rootUrl"]
    assert re.search(
        r"^/admin/tethys_apps/tethysapp/[0-9]+/change/$", json["settingsUrl"]
    )


@override_settings(MULTIPLE_APP_MODE=True)
@override_settings(PREFIX_URL="test/prefix")
@override_settings(LOGIN_URL="/test/prefix/test/login/")
@override_settings(STATIC_URL="/test/prefix/test/static/")
@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_get_app_valid_id_with_prefix(client, test_app, reload_urls):
    """Test get_app API endpoint with valid app id."""
    reload_urls()
    response = client.get(reverse("api:get_app", kwargs={"app": "test-app"}))
    assert response.status_code == 200
    assert isinstance(response, JsonResponse)
    json = response.json()
    assert "title" in json
    assert "description" in json
    assert "tags" in json
    assert "package" in json
    assert "urlNamespace" in json
    assert "color" in json
    assert "icon" in json
    assert "exitUrl" in json
    assert "rootUrl" in json
    assert "settingsUrl" in json
    assert "Test App" == json["title"]
    assert json["description"] == "Place a brief description of your app here."
    assert "" == json["tags"]
    assert "test_app" == json["package"]
    assert "test_app" == json["urlNamespace"]
    assert "#2c3e50" == json["color"]
    assert json["icon"] == "/test/prefix/test/static/test_app/images/icon.gif"
    assert "/test/prefix/apps/" == json["exitUrl"]
    assert "/test/prefix/apps/test-app/" == json["rootUrl"]
    assert re.search(
        r"^/test/prefix/admin/tethys_apps/tethysapp/[0-9]+/change/$",
        json["settingsUrl"],
    )


@override_settings(MULTIPLE_APP_MODE=True)
@override_settings(STATIC_URL="/static")
@override_settings(LOGIN_URL="/accounts/login/")
@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
def test_get_app_authenticated(client, user, test_app):
    """Test get_app API endpoint with valid app id."""
    client.force_login(user)
    response = client.get(reverse("api:get_app", kwargs={"app": "test-app"}))
    assert response.status_code == 200
    assert isinstance(response, JsonResponse)
    json = response.json()
    assert "title" in json
    assert "description" in json
    assert "tags" in json
    assert "package" in json
    assert "urlNamespace" in json
    assert "color" in json
    assert "icon" in json
    assert "exitUrl" in json
    assert "rootUrl" in json
    assert "settingsUrl" in json
    assert "Test App" == json["title"]
    assert json["description"] == "Place a brief description of your app here."
    assert "" == json["tags"]
    assert "test_app" == json["package"]
    assert "test_app" == json["urlNamespace"]
    assert "#2c3e50" == json["color"]
    assert "/static/test_app/images/icon.gif" == json["icon"]
    assert "/apps/" == json["exitUrl"]
    assert "/apps/test-app/" == json["rootUrl"]
    assert re.search(
        r"^/admin/tethys_apps/tethysapp/[0-9]+/change/$", json["settingsUrl"]
    )
    assert json["customSettings"] == {
        "JSON_setting_default_value_required": {
            "type": "JSON",
            "value": {"Test": "JSON test String"},
        },
        "Secret_Test_required": {"type": "SECRET", "value": None},
        "default_name": {"type": "STRING", "value": None},
        "enable_feature": {"type": "BOOLEAN", "value": None},
    }


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_get_app_invalid_id(client, test_app):
    """Test get_app API endpoint with invalid app id."""
    response = client.get(reverse("api:get_app", kwargs={"app": "foo-bar"}))
    assert response.status_code == 200
    assert isinstance(response, JsonResponse)
    json = response.json()
    assert "error" in json
    assert 'Could not find app "foo-bar".' == json["error"]


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True, PREFIX_URL="/")
@pytest.mark.django_db
def test_get_jwt_token_GET_not_authenticated(client):
    """Test get_jwt_token API endpoint with GET method."""
    response = client.get(reverse("api:token_obtain_pair"))
    assert response.status_code == 200
    assert isinstance(response, JsonResponse)
    assert response.json() == {"access": None, "refresh": None}


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True, PREFIX_URL="/")
def test_get_jwt_token_GET_authenticated(client, user):
    """Test get_jwt_token API endpoint with GET method."""

    client.force_login(user)
    with patch("tethys_portal.views.api.RefreshToken") as mock_refresh_token:
        mock_refresh = MagicMock()
        mock_refresh.access_token = "mock_access"
        mock_refresh.__str__.return_value = "mock_refresh"
        mock_refresh_token.for_user.return_value = mock_refresh

        response = client.get(reverse("api:token_obtain_pair"))
        assert response.status_code == 200
        assert isinstance(response, JsonResponse)
        assert response.json() == {"access": "mock_access", "refresh": "mock_refresh"}


@override_settings(
    ALLOW_JWT_BASIC_AUTHENTICATION=False,
    SHOW_PUBLIC_IF_NO_TENANT_FOUND=True,
    PREFIX_URL="/",
)
@pytest.mark.django_db
def test_get_jwt_token_POST_not_allowed(client):
    """Test get_jwt_token API endpoint with POST method when POST is not allowed."""
    response = client.post(reverse("api:token_obtain_pair"))
    assert response.status_code == 405
    assert response.reason_phrase == "Method Not Allowed"
    assert "JWT basic authentication is disabled." in response.content.decode()


@override_settings(
    ALLOW_JWT_BASIC_AUTHENTICATION=True,
    SHOW_PUBLIC_IF_NO_TENANT_FOUND=True,
    PREFIX_URL="/",
)
@pytest.mark.django_db
def test_get_jwt_token_POST_not_authenticated(client):
    """Test get_jwt_token API endpoint with POST method."""
    response = client.post(reverse("api:token_obtain_pair"))
    assert response.status_code == 200
    assert isinstance(response, JsonResponse)
    assert response.json() == {
        "access": None,
        "refresh": None,
        "error": "Username and password are required for authentication.",
    }


@override_settings(
    ALLOW_JWT_BASIC_AUTHENTICATION=True,
    SHOW_PUBLIC_IF_NO_TENANT_FOUND=True,
    PREFIX_URL="/",
)
@pytest.mark.django_db
def test_get_jwt_token_POST_invalid_user(client):
    """Test get_jwt_token API endpoint with POST method and invalid credentials."""
    data = {"username": "invalid_user", "password": "wrong_password"}
    response = client.post(reverse("api:token_obtain_pair"), data)
    assert response.status_code == 200
    assert isinstance(response, JsonResponse)
    assert response.json() == {
        "access": None,
        "refresh": None,
        "error": "Invalid credentials.",
    }


@override_settings(
    ALLOW_JWT_BASIC_AUTHENTICATION=True,
    SHOW_PUBLIC_IF_NO_TENANT_FOUND=True,
    PREFIX_URL="/",
)
def test_get_jwt_token_POST_valid_user(client, user):
    """Test get_jwt_token API endpoint with POST method and valid credentials."""
    data = {"username": user.username, "password": "password"}
    user.set_password("password")
    user.save()
    with patch("tethys_portal.views.api.RefreshToken") as mock_refresh_token:
        mock_refresh = MagicMock()
        mock_refresh.access_token = "mock_access"
        mock_refresh.__str__.return_value = "mock_refresh"
        mock_refresh_token.for_user.return_value = mock_refresh

        response = client.post(reverse("api:token_obtain_pair"), data)
        assert response.status_code == 200
        assert isinstance(response, JsonResponse)
        assert response.json() == {
            "access": "mock_access",
            "refresh": "mock_refresh",
        }, response.json()
