.. _advanced_config_jwt:

****************************
JSON Web Tokens (Optional)
****************************

**Last Updated:** September 2026

Tethys Portal can issue and accept `JSON Web Tokens (JWT) <https://jwt.io/introduction>`_ for authenticating requests to REST endpoints. This capability is provided by the `Simple JWT <https://django-rest-framework-simplejwt.readthedocs.io/en/latest/>`_ add-on for Django REST Framework, which is installed with Tethys Platform. JWT authentication is useful for single-page applications, mobile clients, scripts, and other clients that need to call Tethys APIs without a browser session.

This document describes the JWT endpoints Tethys Portal provides, the default behavior, and how to change the configuration.

How It Works
============

Simple JWT issues a pair of tokens:

* An **access token** that a client sends with each API request in the ``Authorization`` header. It is short-lived.
* A **refresh token** that the client exchanges for a new access token when the old one expires. It is longer-lived and should be stored securely.

Tethys Portal includes ``rest_framework_simplejwt.authentication.JWTAuthentication`` in the default Django REST Framework authentication classes, so any endpoint that uses the default authentication classes will accept a valid access token in addition to session or ``Token`` authentication.

Endpoints
=========

Tethys Portal registers the following endpoints under ``/api/``:

========================= ======== ==========================================================================================================================================
Endpoint                  Method   Description
========================= ======== ==========================================================================================================================================
``/api/token/``           GET      Returns an ``access`` and ``refresh`` token for the user that is logged in to the current browser session. Returns ``null`` values if no user is logged in.
``/api/token/``           POST     Returns an ``access`` and ``refresh`` token for the ``username`` and ``password`` submitted in the request body. Disabled unless ``ALLOW_JWT_BASIC_AUTHENTICATION`` is ``True`` (see below).
``/api/token/refresh/``   POST     Exchanges a ``refresh`` token for a new ``access`` token. With the default configuration, a new ``refresh`` token is also returned and the old one is revoked.
``/api/token/verify/``    POST     Verifies that a ``token`` (access or refresh) is valid and has not expired. Returns an empty ``200`` response if valid and ``401`` otherwise.
``/api/token/blacklist/`` POST     Revokes the given ``refresh`` token so it can no longer be used to obtain access tokens. Use this to implement logout for API clients.
========================= ======== ==========================================================================================================================================

The refresh, verify, and blacklist endpoints are the standard Simple JWT views. See the Simple JWT `Getting Started <https://django-rest-framework-simplejwt.readthedocs.io/en/latest/getting_started.html>`_ guide for details on their request and response formats.

Usage
=====

The sections below show how to use JWT authentication where it is most commonly needed: protecting a REST endpoint in a Tethys app, calling that endpoint from the app's JavaScript front end, authenticating WebSocket connections, and calling the endpoint from an external client such as a Python script.

Protecting an App Endpoint
--------------------------

A REST endpoint in a Tethys app that should accept JWT authentication is a normal controller decorated with the Django REST Framework ``api_view`` decorator (see :ref:`tethys_rest_api`). Two details matter:

* Pass ``login_required=False`` to the ``controller`` decorator. The default ``login_required=True`` check runs before Django REST Framework authenticates the request, so a request that carries only a ``Bearer`` header would be redirected to the login page.
* Authentication is still enforced, because Tethys configures Django REST Framework with ``IsAuthenticated`` as the default permission class and ``JWTAuthentication``, ``SessionAuthentication``, and ``TokenAuthentication`` as the default authentication classes. Unauthenticated requests receive a ``401`` response instead of a redirect. To make an endpoint public, add ``@permission_classes([AllowAny])`` from ``rest_framework.permissions``.

.. code-block:: python

    # controllers.py
    from django.http import JsonResponse
    from rest_framework.decorators import api_view
    from tethys_sdk.routing import controller


    @controller(url='api/get-data', login_required=False)
    @api_view(['GET'])
    def get_data(request):
        """Returns data for the authenticated user."""
        return JsonResponse({
            'user': request.user.username,
            'values': [1, 2, 3],
        })

This endpoint is available at ``/apps/<app>/api/get-data/`` and accepts a valid access token, a logged-in session, or a Django REST Framework ``Token``. To accept JWT only, add ``@authentication_classes([JWTAuthentication])`` from ``rest_framework_simplejwt.authentication``.

Calling from the App Front End
------------------------------

JavaScript running on a page served by the portal already has the user's session cookie, so it can obtain a token pair with a ``GET`` request to ``/api/token/`` and then send the access token as a ``Bearer`` header on subsequent requests. The pattern below is used by apps created with the React scaffold (``tethys scaffold -t react <name>``) and is organized into three small modules. It uses `axios <https://axios-http.com/>`_, but the same approach works with ``fetch``.

**1. Token storage** (``services/api/tokens.js``). Keep the tokens in one place so the rest of the app never touches ``localStorage`` directly:

.. code-block:: javascript

    const ACCESS_TOKEN_KEY = "jwt_access";
    const REFRESH_TOKEN_KEY = "jwt_refresh";

    export function setTokens(access, refresh) {
      localStorage.setItem(ACCESS_TOKEN_KEY, access);
      // With rotation enabled the refresh endpoint returns a new refresh token; store it.
      if (refresh) localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
    }
    export function getAccessToken() {
      return localStorage.getItem(ACCESS_TOKEN_KEY);
    }
    export function getRefreshToken() {
      return localStorage.getItem(REFRESH_TOKEN_KEY);
    }
    export function clearTokens() {
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
    }

**2. API client** (``services/api/client.js``). A shared ``axios`` instance attaches the access token to every request, refreshes it when a request fails with ``401``, and proactively refreshes it shortly before it expires so long-running pages never send an expired token:

.. code-block:: javascript

    import axios from "axios";
    import { getAccessToken, getRefreshToken, setTokens, clearTokens } from "./tokens";

    const PORTAL = window.location.origin;

    const apiClient = axios.create({
      baseURL: PORTAL,
      headers: { Accept: "application/json", "Content-Type": "application/json" },
    });

    // Exchange the refresh token for a new access token (and, by default, a new refresh token).
    async function refreshAccess() {
      const res = await axios.post(`${PORTAL}/api/token/refresh/`, { refresh: getRefreshToken() });
      setTokens(res.data.access, res.data.refresh);
      return res.data.access;
    }

    export function redirectToLogin() {
      window.location.assign(`${PORTAL}/accounts/login?next=${window.location.pathname}`);
    }

    // Read the "exp" claim from the access token without a library.
    function getExpiryMs(token) {
      try {
        const payload = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
        return JSON.parse(atob(payload)).exp * 1000;
      } catch {
        return null;
      }
    }

    // Return a valid access token, refreshing first if it expires within 30 seconds.
    export async function getFreshAccessToken() {
      const access = getAccessToken();
      const expiry = access && getExpiryMs(access);
      if (expiry && expiry - Date.now() > 30_000) return access;
      return refreshAccess();
    }

    // Refresh the access token 60 seconds before it expires, and keep doing so.
    let refreshTimer = null;
    export function scheduleRefresh(access) {
      clearTimeout(refreshTimer);
      const expiry = getExpiryMs(access);
      if (!expiry) return;
      const delay = Math.max(expiry - Date.now() - 60_000, 0);
      refreshTimer = setTimeout(async () => {
        try {
          scheduleRefresh(await refreshAccess());
        } catch {
          redirectToLogin();
        }
      }, delay);
    }

    // Revoke the refresh token, clear local storage, then end the portal session.
    export async function logout() {
      const refresh = getRefreshToken();
      if (refresh) {
        try {
          await axios.post(`${PORTAL}/api/token/blacklist/`, { refresh });
        } catch {
          // Best effort: still clear locally and log out if blacklisting fails.
        }
      }
      clearTokens();
      window.location.assign(`${PORTAL}/accounts/logout/`);
    }

    // Attach the access token to every request.
    apiClient.interceptors.request.use((config) => {
      const access = getAccessToken();
      if (access) config.headers.Authorization = `Bearer ${access}`;
      return config;
    });

    // On 401, refresh once and retry. Never retry the token endpoints themselves.
    apiClient.interceptors.response.use(
      (response) => response.data ?? response,
      async (error) => {
        const res = error.response;
        const original = error.config;
        if (res?.status === 401 && !original._retry && !original.url.includes("/api/token/")) {
          original._retry = true;
          try {
            const access = await refreshAccess();
            original.headers.Authorization = `Bearer ${access}`;
            return apiClient(original);
          } catch {
            redirectToLogin();
            return Promise.reject(error);
          }
        }
        if (res?.status === 401) redirectToLogin();
        return Promise.reject(error);
      }
    );

    export default apiClient;

**3. Portal API helpers** (``services/api/tethys.js``). Obtain the initial token pair from the session and start the refresh timer:

.. code-block:: javascript

    import apiClient, { scheduleRefresh } from "./client";
    import { setTokens } from "./tokens";

    export async function getJWTToken() {
      const { access, refresh } = await apiClient.get("/api/token/");
      setTokens(access, refresh);
      scheduleRefresh(access);
      return { access, refresh };
    }

    export function getUserData() {
      return apiClient.get("/api/whoami/");
    }

Call ``getJWTToken`` once when the app loads, before rendering anything that calls the API. ``/api/token/`` returns ``200`` with ``null`` tokens rather than ``401`` when there is no logged-in session, so check for that case explicitly:

.. code-block:: javascript

    useEffect(() => {
      Promise.all([getUserData(), getJWTToken()])
        .then(([user, jwt]) => {
          if (!jwt.access) {
            redirectToLogin();
            return;
          }
          setAppContext({ user, jwt });
        })
        .catch(setError);
    }, []);

After this, any call made through ``apiClient`` (for example ``apiClient.get("/apps/my-first-app/api/get-data/")``) is authenticated with the access token and transparently refreshed when needed.

**Logging out.** The portal navigation bar renders its "Log Out" link outside of your React tree as a plain anchor to ``/accounts/logout/``. Following it ends the Django session but leaves the refresh token valid until it expires. To revoke the token as well, intercept the click and call the ``logout`` helper, which blacklists the refresh token, clears storage, and then navigates to the portal logout page:

.. code-block:: javascript

    useEffect(() => {
      const links = document.querySelectorAll('a[href*="/accounts/logout"]');
      const handler = (e) => {
        e.preventDefault();
        logout();
      };
      links.forEach((el) => el.addEventListener("click", handler));
      return () => links.forEach((el) => el.removeEventListener("click", handler));
    }, []);

Authenticating WebSockets
-------------------------

Browsers cannot set headers on a WebSocket handshake, so pass the access token as a query parameter instead. On the client, get a fresh token before connecting, and reconnect with a new token if the server closes the socket because the token expired:

.. code-block:: javascript

    import { getFreshAccessToken, redirectToLogin } from "./services/api/client";

    async function connect(wsUrl) {
      const token = await getFreshAccessToken();
      const ws = new WebSocket(`${wsUrl}?token=${encodeURIComponent(token)}`);
      ws.addEventListener("close", async (event) => {
        if (event.code === 4401) {
          // Token expired or was rejected: get a fresh one and reconnect.
          try {
            await getFreshAccessToken();
            connect(wsUrl);
          } catch {
            redirectToLogin();
          }
        }
      });
      return ws;
    }

In the app's consumer (see :ref:`tutorials_websockets`), validate the token with Simple JWT's ``AccessToken`` class, which checks the signature and expiry, and resolve the user from its ``user_id`` claim. Store the expiry so the connection can be closed once the token would have expired:

.. code-block:: python

    import datetime
    from urllib.parse import parse_qs

    from channels.db import database_sync_to_async
    from channels.generic.websocket import AsyncWebsocketConsumer
    from django.contrib.auth import get_user_model
    from rest_framework_simplejwt.exceptions import TokenError
    from rest_framework_simplejwt.tokens import AccessToken
    from tethys_sdk.routing import consumer


    @database_sync_to_async
    def get_user_from_jwt(token_str):
        """Return (user, exp) for a valid access token, or (None, None)."""
        try:
            token = AccessToken(token_str)  # verifies signature and expiry
            user = get_user_model().objects.get(pk=token["user_id"])
        except (TokenError, KeyError, get_user_model().DoesNotExist):
            return None, None
        if not user.is_active:
            return None, None
        return user, token["exp"]


    @consumer(name="my_consumer", url="my-consumer/")
    class MyConsumer(AsyncWebsocketConsumer):
        async def connect(self):
            self.token_exp = None
            query = parse_qs(self.scope.get("query_string", b"").decode())
            token = next(iter(query.get("token", [])), None)
            if token:
                # A JWT takes precedence over the session user so its expiry is honored.
                user, self.token_exp = await get_user_from_jwt(token)
            else:
                user = self.scope.get("user")
            if user is None or not user.is_authenticated:
                await self.close(code=4401)
                return
            self.scope["user"] = user
            await self.accept()

        async def receive(self, text_data=None, bytes_data=None):
            # Close the socket once the token that authenticated it has expired so the
            # client reconnects with a fresh token and re-runs the checks above.
            now = datetime.datetime.now(datetime.timezone.utc).timestamp()
            if self.token_exp is not None and now >= self.token_exp:
                await self.close(code=4401)
                return
            ...

Calling from an External Client
-------------------------------

Clients that run outside the browser, such as scripts, notebooks, or other services, do not have a session cookie. They obtain tokens by posting a username and password to ``/api/token/``. This requires ``ALLOW_JWT_BASIC_AUTHENTICATION`` to be enabled (see :ref:`advanced_config_jwt_configuration`).

.. code-block:: python

    import requests

    PORTAL = 'https://<HOST_Portal>'

    # 1. Obtain tokens
    res = requests.post(
        f'{PORTAL}/api/token/',
        json={'username': '<username>', 'password': '<password>'},
    )
    tokens = res.json()

    # 2. Call an app endpoint with the access token
    res = requests.get(
        f'{PORTAL}/apps/my-first-app/api/get-data/',
        headers={'Authorization': f"Bearer {tokens['access']}"},
    )
    print(res.json())

    # 3. When the access token expires (HTTP 401), refresh it. With the default
    #    configuration the response also includes a new refresh token, and the
    #    old one is revoked, so always store the new pair.
    res = requests.post(f'{PORTAL}/api/token/refresh/', json={'refresh': tokens['refresh']})
    tokens.update(res.json())

    # 4. Revoke the refresh token when finished
    requests.post(f'{PORTAL}/api/token/blacklist/', json={'refresh': tokens['refresh']})

The same calls with ``curl``:

.. code-block:: bash

    # Obtain tokens
    curl -X POST https://<HOST_Portal>/api/token/ \
        -H "Content-Type: application/json" \
        -d '{"username": "<username>", "password": "<password>"}'

    # Call an endpoint
    curl https://<HOST_Portal>/apps/my-first-app/api/get-data/ \
        -H "Authorization: Bearer <access token>"

    # Refresh
    curl -X POST https://<HOST_Portal>/api/token/refresh/ \
        -H "Content-Type: application/json" \
        -d '{"refresh": "<refresh token>"}'

    # Revoke (logout)
    curl -X POST https://<HOST_Portal>/api/token/blacklist/ \
        -H "Content-Type: application/json" \
        -d '{"refresh": "<refresh token>"}'

After a refresh token is revoked it is rejected by ``/api/token/refresh/``. Any access token that was already issued remains valid until it expires, which is why access token lifetimes are kept short.

Default Behavior
================

Tethys Portal uses the Simple JWT defaults except where noted:

* **Access token lifetime:** 5 minutes (Simple JWT default).
* **Refresh token lifetime:** 1 day (Simple JWT default).
* **Refresh token rotation:** enabled. Tethys sets ``ROTATE_REFRESH_TOKENS`` to ``True``, so every call to ``/api/token/refresh/`` returns a new refresh token.
* **Blacklist after rotation:** enabled. Tethys sets ``BLACKLIST_AFTER_ROTATION`` to ``True``, so the previous refresh token is revoked each time a new one is issued. Together with the ``/api/token/blacklist/`` endpoint this ensures a refresh token can only be used once and can be revoked on demand.
* **Basic authentication:** disabled. ``ALLOW_JWT_BASIC_AUTHENTICATION`` defaults to ``False``, so the ``POST /api/token/`` endpoint returns ``405 Method Not Allowed``. Tokens can still be obtained with ``GET`` by clients that have a logged-in session.

The blacklist is stored in the database using the ``rest_framework_simplejwt.token_blacklist`` app, which is included in ``INSTALLED_APPS`` by default.

.. important::

    The token blacklist app adds tables to the Tethys database. If you are upgrading an existing portal, run the database migrations after upgrading:

    .. code-block:: bash

        tethys db migrate

.. tip::

    Blacklisted tokens remain in the database after they expire. Simple JWT provides a management command to remove them, which you may want to run periodically (for example with ``cron``):

    .. code-block:: bash

        tethys manage flushexpiredtokens

    See `Simple JWT: Blacklist app <https://django-rest-framework-simplejwt.readthedocs.io/en/latest/blacklist_app.html>`_ for details.

.. _advanced_config_jwt_configuration:

Configuration
=============

Enabling Basic Authentication
-----------------------------

To let clients obtain tokens by posting a username and password to ``/api/token/``, add the following at the top level of the ``settings`` section of your :file:`portal_config.yml`:

.. code-block:: yaml

    settings:
      ALLOW_JWT_BASIC_AUTHENTICATION: True

.. warning::

    Only enable this option when the portal is served over HTTPS (see :ref:`https_config`). Credentials sent to this endpoint are transmitted in the request body. Consider also enabling :ref:`advanced_config_lockout` to protect the endpoint from brute-force attempts.

Simple JWT Settings
-------------------

The Simple JWT behavior is controlled by the ``SIMPLE_JWT`` setting. Tethys defines it as:

.. code-block:: yaml

    settings:
      SIMPLE_JWT:
        ROTATE_REFRESH_TOKENS: True
        BLACKLIST_AFTER_ROTATION: True

You can override it in your :file:`portal_config.yml`. Note that a ``SIMPLE_JWT`` block in :file:`portal_config.yml` **replaces** the Tethys default rather than merging with it, so include the rotation settings if you want to keep them. For example, to keep the Tethys defaults and also update the user's ``last_login`` field each time tokens are issued:

.. code-block:: yaml

    settings:
      SIMPLE_JWT:
        ROTATE_REFRESH_TOKENS: True
        BLACKLIST_AFTER_ROTATION: True
        UPDATE_LAST_LOGIN: True

Or, to disable rotation so refresh tokens can be reused until they expire:

.. code-block:: yaml

    settings:
      SIMPLE_JWT:
        ROTATE_REFRESH_TOKENS: False
        BLACKLIST_AFTER_ROTATION: False

The full list of options is described in the `Simple JWT settings documentation <https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html>`_.

Changing Token Lifetimes
------------------------

The ``ACCESS_TOKEN_LIFETIME`` and ``REFRESH_TOKEN_LIFETIME`` settings must be Python ``timedelta`` objects, which cannot be expressed in YAML. To change them, put the ``SIMPLE_JWT`` setting in an additional Python settings file and reference it with ``ADDITIONAL_SETTINGS_FILES`` (see :ref:`tethys_configuration`).

Create a file such as :file:`<TETHYS_HOME>/jwt_settings.py`:

.. code-block:: python

    from datetime import timedelta

    SIMPLE_JWT = {
        "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
        "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
        "ROTATE_REFRESH_TOKENS": True,
        "BLACKLIST_AFTER_ROTATION": True,
    }

    __all__ = ["SIMPLE_JWT"]

Then reference it in :file:`portal_config.yml`:

.. code-block:: yaml

    settings:
      TETHYS_PORTAL_CONFIG:
        ADDITIONAL_SETTINGS_FILES:
          - /path/to/tethys_home/jwt_settings.py

Restart the portal after changing any of these settings for them to take effect.
