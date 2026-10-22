.. _https_development_server_recipe:

*****************************************
Run a Tethys Development Server over HTTPS
*****************************************

**Last Updated:** October 2026

This recipe explains how to run a Tethys development server over HTTPS using Caddy as a reverse proxy.

Running your development portal over HTTPS lets you develop and test features that behave differently, or only work at all, on a secure connection.

The development server started by ``tethys start`` can't provide this on its own: it only speaks plain HTTP and has no way to serve a TLS certificate. Instead, this recipe places `Caddy <https://caddyserver.com/>`_ in front of it as a local reverse proxy. Caddy handles the HTTPS connection with the browser using a locally trusted certificate, then forwards each request to Tethys over plain HTTP on your own machine.

.. note::

    This recipe is for local development only. A production deployment should terminate HTTPS at its web server (e.g. NGINX) with a certificate from a public certificate authority.

1. Install Caddy
================

Install Caddy by following the `Caddy installation instructions <https://caddyserver.com/docs/install>`_ for your operating system.

.. tip::

    Linux Users: The Caddy package in some distribution repositories (e.g. ``apt`` on Ubuntu) is older than the current release, and installing it also enables and starts a system-wide Caddy service. This recipe does not need that service. If it was started, stop and disable it with:

    .. code-block:: bash

        sudo systemctl disable --now caddy

2. Configure Tethys to Trust the Proxy
======================================

Caddy talks to Tethys over plain HTTP, so by default Tethys does not know the browser is using HTTPS. As a result it builds ``http://`` OAuth2 redirect URIs and rejects form submissions with a CSRF error. Caddy tells Tethys the original protocol in the ``X-Forwarded-Proto`` header. :ref:`activate_environment`, then configure Tethys to trust that header:

.. code-block:: bash

    tethys settings --set SECURE_PROXY_SSL_HEADER "['HTTP_X_FORWARDED_PROTO', 'https']"

.. warning::

    Only use this setting when Tethys sits behind a proxy that sets the ``X-Forwarded-Proto`` header. If clients can reach Tethys directly, they could send this header themselves and make a plain HTTP request look secure.

3. Create a Caddyfile
=====================

Create a new directory for the Caddy configuration (e.g. :file:`~/tethysdev/caddy`) and create a file named :file:`Caddyfile` in it with the following contents:

.. code-block:: text

    {
        admin off
        auto_https disable_redirects
    }

    localhost:8443 { 
        reverse_proxy localhost:8000
    }

This tells Caddy to serve HTTPS at ``https://localhost:8443`` and pass every request to Tethys on port 8000.

4. Start Tethys and Caddy
=========================

In one terminal, :ref:`activate_environment` and start the Tethys development server:

.. code-block:: bash

    tethys start

In a second terminal, change into the directory containing your :file:`Caddyfile` and start Caddy:

.. code-block:: bash

    cd ~/tethysdev/caddy
    caddy run

The first time Caddy runs, it installs its local certificate authority in your system's trust store and may prompt for your password. You can also do this step yourself at any time with:

.. code-block:: bash

    caddy trust

.. tip::

    Linux Users: Firefox keeps its own certificate store. If Firefox shows a certificate warning, install the ``libnss3-tools`` package (e.g. ``sudo apt install libnss3-tools``), run ``caddy trust`` again, and restart Firefox.

5. View Tethys over HTTPS
=========================

Open `https://localhost:8443 <https://localhost:8443>`_ in your browser. You should see your Tethys Portal with no certificate warning.

.. important::

    Browse to port **8443**, not 8000. Port 8000 is the Tethys development server itself, which only speaks plain HTTP, so ``https://localhost:8000`` will fail to connect.


To stop serving over HTTPS, press :kbd:`Ctrl+C` in the terminal running Caddy.