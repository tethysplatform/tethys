from importlib import reload, import_module
import sys
from types import FunctionType
from unittest import mock

from django.conf import settings
from django.test import override_settings
from django.urls import clear_url_caches
import pytest

import tethys_apps.base.handoff as tethys_handoff
from tethys_sdk.testing import TethysTestCase


def test_function(*args):
    if args is not None:
        arg_list = []
        for arg in args:
            arg_list.append(arg)
        return arg_list
    else:
        return ""


def test_handoffmanager_init():
    app = mock.MagicMock()
    handlers = mock.MagicMock(name="handler_name")
    app.handoff_handlers.return_value = handlers
    with mock.patch(
        "tethys_apps.base.handoff.HandoffManager._get_valid_handlers",
        return_value=["valid_handler"],
    ):
        result = tethys_handoff.HandoffManager(app=app)
    assert app == result.app
    assert handlers == result.handlers
    assert ["valid_handler"] == result.valid_handlers


def test_handoffmanager_repr():
    app = mock.MagicMock()
    handlers = mock.MagicMock()
    handlers.name = "test_handler"
    app.handoff_handlers.return_value = [handlers]
    with mock.patch(
        "tethys_apps.base.handoff.HandoffManager._get_valid_handlers",
        return_value=["valid_handler"],
    ):
        result = tethys_handoff.HandoffManager(app=app).__repr__()
    check_string = f"<Handoff Manager: app={app}, handlers=['{handlers.name}']>"
    assert check_string == result


def test_handoffmanager_get_capabilities():
    app = mock.MagicMock()
    manager = mock.MagicMock(valid_handlers="test_handlers")
    with mock.patch(
        "tethys_apps.base.handoff.HandoffManager._get_handoff_manager_for_app",
        return_value=manager,
    ):
        result = tethys_handoff.HandoffManager(app=app).get_capabilities(
            app_name="test_app"
        )
    assert "test_handlers" == result


def test_handoffmanager_get_capabilities_external():
    app = mock.MagicMock()
    handler1 = mock.MagicMock()
    handler1.internal = False
    handler2 = mock.MagicMock()
    handler2.internal = True
    manager = mock.MagicMock(valid_handlers=[handler1, handler2])
    with mock.patch(
        "tethys_apps.base.handoff.HandoffManager._get_handoff_manager_for_app",
        return_value=manager,
    ):
        result = tethys_handoff.HandoffManager(app=app).get_capabilities(
            app_name="test_app", external_only=True
        )
    assert [handler1] == result


@mock.patch("tethys_apps.base.handoff.json")
def test_handoffmanager_get_capabilities_json(mock_json):
    app = mock.MagicMock()
    handler1 = mock.MagicMock(name="test_name")
    manager = mock.MagicMock(valid_handlers=[handler1])
    with mock.patch(
        "tethys_apps.base.handoff.HandoffManager._get_handoff_manager_for_app",
        return_value=manager,
    ):
        tethys_handoff.HandoffManager(app=app).get_capabilities(
            app_name="test_app", jsonify=True
        )
    rts_call_args = mock_json.dumps.call_args_list
    assert "test_name" == rts_call_args[0][0][0][0]["_mock_name"]


def test_handoffmanager_get_handler():
    app = mock.MagicMock()
    handler1 = mock.MagicMock()
    handler1.name = "handler1"
    manager = mock.MagicMock(valid_handlers=[handler1])
    with mock.patch(
        "tethys_apps.base.handoff.HandoffManager._get_handoff_manager_for_app",
        return_value=manager,
    ):
        result = tethys_handoff.HandoffManager(app=app).get_handler(
            handler_name="handler1"
        )
    assert "handler1" == result.name


@mock.patch("tethys_apps.base.handoff.HttpResponseBadRequest")
def test_handoffmanager_handoff_type_error(mock_hrbr):
    from django.http import HttpRequest

    request = HttpRequest()
    app = mock.MagicMock()
    app.name = "test_app_name"
    handler1 = mock.MagicMock()
    handler1().internal = False
    handler1().side_effect = TypeError("test message")
    manager = mock.MagicMock(get_handler=handler1)
    with mock.patch(
        "tethys_apps.base.handoff.HandoffManager._get_handoff_manager_for_app",
        return_value=manager,
    ):
        tethys_handoff.HandoffManager(app=app).handoff(
            request=request, handler_name="test_handler"
        )
    rts_call_args = mock_hrbr.call_args_list
    assert "HTTP 400 Bad Request: test message." in rts_call_args[0][0][0]


@mock.patch("tethys_apps.base.handoff.HttpResponseBadRequest")
def test_handoffmanager_handoff_error(mock_hrbr):
    from django.http import HttpRequest

    request = HttpRequest()
    app = mock.MagicMock()
    app.name = "test_app_name"
    handler1 = mock.MagicMock()
    handler1().internal = True
    handler1().side_effect = TypeError("test message")
    mapp = mock.MagicMock()
    mapp.name = "test manager name"
    manager = mock.MagicMock(get_handler=handler1, app=mapp)
    with mock.patch(
        "tethys_apps.base.handoff.HandoffManager._get_handoff_manager_for_app",
        return_value=manager,
    ):
        tethys_handoff.HandoffManager(app=app).handoff(
            request=request, handler_name="test_handler"
        )
    rts_call_args = mock_hrbr.call_args_list
    check_message = (
        "HTTP 400 Bad Request: No handoff handler '{0}' for app '{1}' found".format(
            "test manager name", "test_handler"
        )
    )
    assert check_message in rts_call_args[0][0][0]


def test_handoffmanager_get_valid_handlers():
    app = mock.MagicMock(package="test_app")
    handler1 = mock.MagicMock(handler="controllers.home", valid=True)
    app.handoff_handlers.return_value = [handler1]
    result = tethys_handoff.HandoffManager(app=app)._get_valid_handlers()
    assert "controllers.home" == result[0].handler


# --- Pytest refactor for HandoffHandler tests ---
def test_handoffhandler_init():
    result = tethys_handoff.HandoffHandler(
        name="test_name", handler="test_app.handoff.csv", internal=True
    )
    assert "test_name" == result.name
    assert "test_app.handoff.csv" == result.handler
    assert result.internal
    assert isinstance(result.function, FunctionType)


def test_handoffhandler_repr():
    result = tethys_handoff.HandoffHandler(
        name="test_name", handler="test_app.handoff.csv", internal=True
    ).__repr__()
    check_string = "<Handoff Handler: name=test_name, handler=test_app.handoff.csv>"
    assert check_string == result


def test_handoffhandler_dict_json_arguments():
    with mock.patch(
        "tethys_apps.base.handoff.HandoffHandler.arguments",
        new_callable=mock.PropertyMock,
        return_value=["test_json", "request"],
    ):
        result = tethys_handoff.HandoffHandler(
            name="test_name", handler="test_app.handoff.csv", internal=True
        ).__dict__()
        check_dict = {"name": "test_name", "arguments": ["test_json"]}
    assert isinstance(result, dict)
    assert check_dict == result


def test_handoffhandler_arguments():
    hh = tethys_handoff.HandoffHandler(
        name="test_name", handler="test_app.handoff.csv", internal=True
    )
    result = hh.arguments
    assert ["request", "csv_url"] == result


# --- Pytest refactor for GetHandoffManagerFroApp tests ---
@pytest.mark.django_db
def test_gethandoffmanagerforapp_not_app_name():
    app = mock.MagicMock()
    result = tethys_handoff.HandoffManager(app=app)._get_handoff_manager_for_app(
        app_name=None
    )
    assert app == result.app


@mock.patch("tethys_apps.base.handoff.tethys_apps")
@pytest.mark.django_db
def test_gethandoffmanagerforapp_with_app(mock_ta):
    app = mock.MagicMock(package="test_app")
    app.get_handoff_manager.return_value = "test_manager"
    mock_ta.harvester.SingletonHarvester().apps = [app]
    result = tethys_handoff.HandoffManager(app=app)._get_handoff_manager_for_app(
        app_name="test_app"
    )
    assert "test_manager" == result


@pytest.fixture()
@pytest.mark.django_db
def test_app_handoff_client():
    class ClientUser(TethysTestCase):
        pass

    c = ClientUser().get_test_client()
    user = ClientUser().create_test_user(
        username="joe", password="secret", email="joe@some_site.com"
    )
    c.force_login(user)
    yield c, user
    user.delete()


def reload_urlconf(urlconf=None):
    clear_url_caches()
    if urlconf is None:
        urlconf = settings.ROOT_URLCONF
    if urlconf in sys.modules:
        reload(sys.modules[urlconf])
    else:
        import_module(urlconf)


@override_settings(PREFIX_URL="/")
@pytest.mark.django_db
def test_app_handoff(test_app_handoff_client, test_app):
    c, user = test_app_handoff_client
    reload_urlconf()
    response = c.get('/handoff/test-app/test_name/?csv_url=""')
    assert response.status_code == 302


@override_settings(PREFIX_URL="test/prefix")
@pytest.mark.django_db
def test_app_handoff_with_prefix(test_app_handoff_client, test_app):
    c, user = test_app_handoff_client
    reload_urlconf()
    response = c.get('/test/prefix/handoff/test-app/test_name/?csv_url=""')
    assert response.status_code == 302
