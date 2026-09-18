.. _secure_map_services_api:

************************
Secure Map Services API
************************

**Last Updated:** August 2026

Secure map services are map services (e.g.: OGC WMS endpoints) that require credentials to access. The Secure Map Services API allows a developer to register the endpoint and credentials of such a service once, and then allows apps to consume that service without ever storing or handling the credentials themselves.

In addition, requests can optionally be routed through a proxy endpoint provided by Tethys Portal so that credentials are never sent to the browser. See :ref:`secure_map_services_proxy` for more details.

.. tip:: 

    For a step-by-step tutorial on using secure map services in your app, see the :ref:`Secure Map Services Tutorial <secure_map_services_tutorial>`.

Two authentication methods are supported:

* **API Key**: a key is stored (encrypted) with the service and added to each request as a query parameter.
* **OAuth2**: an OAuth2 access token is retrieved from the requesting user's linked social auth account and added to each request as a ``Bearer`` token.

.. important::

    API keys assigned to a ``SecureMapService`` are encrypted before they are stored in the database. This requires a ``SALT_KEY`` to be set in your :file:`portal_config.yml`. If you have not already done so, generate one as follows:

    .. code-block:: bash

        tethys gen portal_config
        tethys settings --generate-salt-key

.. _secure_map_service_settings:

Secure Map Service Settings
===========================

Using secure map services in your app is accomplished by adding the ``secure_map_service_settings()`` method to your :term:`app class`, which is located in your :term:`app configuration file` (:file:`app.py`). This method should return a list or tuple of ``SecureMapServiceSetting`` objects. For example:

::

    from tethys_sdk.app_settings import SecureMapServiceSetting

    class App(TethysAppBase):
        """
        Tethys App Class for My First App.
        """
        ...
        def secure_map_service_settings(self):
            """
            Example secure_map_service_settings method.
            """
            secure_map_service_settings = (
                SecureMapServiceSetting(
                    name='primary_secure_map_service',
                    description='Secure map service for app to use.',
                    required=True,
                ),
            )

            return secure_map_service_settings

.. caution::

    The ellipsis in the code block above indicates code that is not shown for brevity. **DO NOT COPY VERBATIM**.

Unlike other Tethys Service settings, a ``SecureMapServiceSetting`` does not specify an engine. The type of service and how it is authenticated are properties of the ``SecureMapService`` that is assigned to the setting, not of the setting itself.

.. _register_secure_map_service:

Register a Secure Map Service
=============================

Before a ``SecureMapService`` can be assigned to a setting, it must be registered in the Admin Interface of Tethys Portal:

1. Access the Admin interface of Tethys Portal by clicking on the drop down menu next to your user name and selecting the "Site Admin" option.

2. Scroll down to the **Tethys Services** section of the Admin Interface and select the link titled **Secure Map Services**.

3. Click on the **Add Secure Map Service** button.

4. Fill in the connection information for the service (see the table below).

5. Press the **Save** button to save the new ``SecureMapService``.

The following fields are available on a ``SecureMapService``:

==========================  ==========================================================================================================================================================================
Field                       Description
==========================  ==========================================================================================================================================================================
**Name**                    Unique name used to identify the service.
**Endpoint**                The URL of the map service.
**Legend Title**            The title to use for the legend when the service is added to a map as a layer.
**Authentication Method**   One of **API Key** or **OAuth2**. The fields that apply to the other method are hidden in the admin form.
**API Key**                 The API key to use when the authentication method is **API Key**. The value is encrypted before it is stored in the database.
**OAuth2 Provider**         The social auth backend to retrieve the access token from when the authentication method is **OAuth2**. The options are populated from the authentication backends that are enabled for the portal (see :ref:`single_sign_on_config`).
**Service Type**            The type of service: **WMS** (``ImageWMS``), **GML**, **GeoJSON**, or **REST/JSON API** (``REST``). For the map service types, the stored value is used as the ``source`` of the ``MVLayer`` that is created when the service is retrieved with ``as_layer=True``. Use **REST/JSON API** for services that are consumed with ``as_response=True`` or with ``as_endpoint=True`` rather than rendered as a map layer.
**Use Proxy for Requests**  When checked, requests are routed through a Tethys Portal proxy endpoint so that credentials are never exposed to the browser. See :ref:`secure_map_services_proxy`.
**Parameters**              A JSON object of additional query parameters to include with each request to the service. See :ref:`secure_map_services_params`.
==========================  ==========================================================================================================================================================================

.. tip::

    You do not need to create a new ``SecureMapService`` for each ``SecureMapServiceSetting`` or each app. Apps and ``SecureMapServiceSettings`` can share ``SecureMapServices``.

.. _assign_secure_map_service:

Assign Secure Map Service
=========================

The ``SecureMapServiceSetting`` can be thought of as a socket for a connection to a ``SecureMapService``. Before we can do anything with the ``SecureMapServiceSetting`` we need to "plug in" or assign a ``SecureMapService`` to the setting. Assigning a ``SecureMapService`` is done through the Admin Interface of Tethys Portal as follows:

1. Navigate to App Settings Page

    a. Return to the Home page of the Admin Interface using the **Home** link in the breadcrumbs.

    b. Scroll to the **Tethys Apps** section of the Admin Interface and select the **Installed Apps** link.

    c. Select the link for your app from the list of installed apps.

2. Assign ``SecureMapService`` to the appropriate ``SecureMapServiceSetting``

    a. Scroll to the **Secure Map Service Settings** section and locate the ``SecureMapServiceSetting``.

    .. note::

        If you don't see the ``SecureMapServiceSetting`` in the list, uninstall the app and reinstall it again.

    b. Assign the appropriate ``SecureMapService`` to your ``SecureMapServiceSetting`` using the drop down menu in the **Secure Map Service** column.

    c. Press the **Save** button at the bottom of the page to save your changes.

.. note::

    During development you will assign the ``SecureMapService`` setting yourself. However, when the app is installed in production, this step is performed by the portal administrator upon installing your app, which may or may not be yourself.

Working with Secure Map Services
================================

After a secure map service has been assigned to a setting, use the ``get_secure_map_service()`` method of the app class to retrieve it. The value that is returned depends on which of the ``as_`` arguments is provided.

Get the Service
---------------

Called with only a name, ``get_secure_map_service()`` returns the ``SecureMapService`` object that is assigned to the setting:

.. code-block:: python

    from .app import App

    service = App.get_secure_map_service('primary_secure_map_service')

Get an Endpoint
---------------

Pass ``as_endpoint=True`` to get the URL of the service with all of its parameters (and the API key, if applicable) applied:

.. code-block:: python

    from .app import App

    endpoint = App.get_secure_map_service('primary_secure_map_service', as_endpoint=True)

.. note::

    A lazy string is returned when ``as_endpoint`` is ``True``. This ensures the endpoint reflects the current state of the service's settings every time it is used, and allows the endpoint to be referenced at import time (e.g.: as a ``MapLayout`` basemap) before the app URLs have been registered.

Get a Map Layer
---------------

Pass ``as_layer=True`` to get an :ref:`MVLayer <gizmo_mvlayer>` for the service that can be added to a ``MapView`` or ``MapLayout``. The ``source`` of the layer is the **Service Type** of the service and the ``legend_title`` is the **Legend Title** of the service:

.. code-block:: python

    from .app import App

    layer = App.get_secure_map_service('primary_secure_map_service', as_layer=True)

If the service uses OAuth2 authentication and is not proxied, the access token must be retrieved from the user making the request, so the ``request_user`` argument is required:

.. code-block:: python

    layer = App.get_secure_map_service(
        'primary_secure_map_service',
        as_layer=True,
        request_user=request.user,
    )

Get a Response
--------------

Pass ``as_response=True`` to perform the request server-side and get the resulting ``requests.Response`` object. This is useful for services that return data to be processed by the app rather than rendered as a map layer:

.. code-block:: python

    from .app import App

    response = App.get_secure_map_service(
        'primary_secure_map_service',
        as_response=True,
        request_user=request.user,
    )
    data = response.json()

.. note::

    As with ``as_layer``, ``request_user`` is required when the service uses OAuth2 authentication. An exception is raised if the request is not successful.

.. _secure_map_services_params:

Service Parameters
==================

The **Parameters** field of a ``SecureMapService`` is a JSON object of query parameters that are added to every request made to the service. For example, the following parameters could be used for a WMS service:

.. code-block:: json

    {
        "service": "WMS",
        "request": "GetMap",
        "layers": "my:layer",
        "format": "image/png",
        "transparent": true
    }

String values may contain placeholders that reference fields of the ``SecureMapService``, using Python's ``string.Template`` syntax. This is most commonly used to place the API key in a parameter with a name other than ``api_key``:

.. code-block:: json

    {
        "connectId": "${api_key}"
    }

.. note::

    If the API key is not referenced by any parameter, it is added automatically as a parameter named ``api_key``.

Overriding Parameters Per Request
---------------------------------

Pass a ``param_overrides`` dictionary to ``get_secure_map_service()`` to add to or replace the parameters of the service for a single request. This does not modify the ``SecureMapService``:

.. code-block:: python

    from .app import App

    response = App.get_secure_map_service(
        'primary_secure_map_service',
        as_response=True,
        param_overrides={'layers': 'my:other_layer'},
        request_user=request.user,
    )

Updating Parameters Permanently
-------------------------------

Use the ``update_secure_map_service_params()`` method of the app class to permanently update the parameters of the ``SecureMapService`` that is assigned to a setting. The given parameters are merged with the existing parameters and saved:

.. code-block:: python

    from .app import App

    App.update_secure_map_service_params(
        'primary_secure_map_service',
        {'layers': 'my:other_layer'},
    )

.. caution::

    ``SecureMapServices`` can be shared by multiple settings and apps, so updating the parameters of a service affects every app that uses it.

.. _secure_map_services_proxy:

Proxying Requests
=================

When the **Use Proxy for Requests** option is enabled on a ``SecureMapService``, the endpoint that is returned by ``get_secure_map_service()`` is not the endpoint of the map service, but rather a URL to a proxy view provided by Tethys Portal (``secure-map-proxy/<id>/``). The browser makes its requests against the proxy, which then adds the credentials and parameters of the service server-side and streams the response back. As a result, the API key or access token is never sent to the browser.

The proxy view requires the user to be logged in, and for OAuth2 services it uses the access token of the logged in user making the request.

.. tip::

    Enable **Use Proxy for Requests** for any service whose credentials should not be visible to end users. Without it, the API key is included in the URL of the tile requests that the browser makes, where it can be read from the browser's developer tools.

.. _secure_map_services_oauth:

Requiring an OAuth2 Provider
===========================

Services that use OAuth2 authentication require the user to have linked the corresponding social auth account to their Tethys Portal account. To require users to link an account before they can access an app, add the app package and provider name to the ``OAUTH2_REQUIREMENTS`` portal setting:

.. code-block:: bash

    tethys settings --set OAUTH2_REQUIREMENTS.my_first_app my_provider

Users who access the app without having linked an account for the given provider are redirected to their user settings page with a message prompting them to link it.

.. note::

    The provider must also be configured as an authentication backend for the portal. See :ref:`single_sign_on_config` for more details.

API Documentation
=================

.. automethod:: tethys_apps.base.TethysAppBase.secure_map_service_settings

.. automethod:: tethys_apps.base.TethysAppBase.get_secure_map_service

.. automethod:: tethys_apps.base.TethysAppBase.update_secure_map_service_params
