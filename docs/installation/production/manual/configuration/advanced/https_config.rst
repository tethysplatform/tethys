.. _https_config:

*****************************
Configure HTTPS (Recommended)
*****************************

**Last Updated:** September 2022

SSL and TLS are the standard technologies for establishing a secured connection between a web server and a browser. In order to create a secured connection, a certificate and key are needed.

.. important::

    You will need to have assigned a domain name to the ``server_name`` field in the NGINX config.

Certbot
=======

`Certbot <https://certbot.eff.org/pages/about>`_ is a tool that automatically administers certificates on websites using `Let's Encrypt <https://letsencrypt.org/about/>`_, a free certificate authority. We recommend using Certbot because it automatically retrieves certificates and updates them regularly. It can also automatically configure NGINX to use the certificates.

1. Install the Snapcraft (CentOS and Ubuntu < 20 only):

    Certbot is distributed with `Snapcraft <https://snapcraft.io/about>`_, a universal Linux package manager. Find instructions for installing the Snapcrafed daemon (snapd) on your distribution here: `Installing snapd <https://snapcraft.io/docs/installing-snapd>`_.

2. Update snapd to make sure you have the latest version:

    .. code-block::

        sudo snap install core
        sudo snap refresh core

3. Install Certbot:

    .. code-block::

        sudo snap install --classic certbot

4. Run the ``certbot`` command using the NGINX plugin:

    .. code-block::

        sudo certbot --nginx

    .. note::

        If the ``certbot`` command is not recognized as a command, you'll need to link it to :file:`/usr/bin`:

        .. code-block::

            sudo ln -s /snap/bin/certbot /usr/bin/certbot

5. Follow the on-screen prompts to complete the process of setting up certbot.

6. Review the :file:`tethys_nginx.conf` to see the changes that ``certbot`` made:

    **Ubuntu**:

    .. code-block::

        cat /etc/nginx/sites-enabled/tethys_nginx.conf

    **Rocky Linux**:

    .. code-block::

        cat /etc/nginx/conf.d/tethys_nginx.conf

7. Verify that auto-renewal works:

    .. code-block::

        sudo certbot renew --dry-run

That's it! Certbot will take care of automatically updating the certificates from now on. You shouldn't need to run the certbot command again. For additional help with installing and setting up Certbot, see: `certbot instructions <https://certbot.eff.org/instructions>`_. Choose **Nginx** for the first field and either **Ubuntu 20** or **CentOS 8** for the second field.

.. important::

    If you are using Single Sign On (e.g. Google, Facebook, LinkedIn), there is an additional configuration step that needs to be performed after setting up HTTPS. See :ref:`https_config_sso`.

Manually
========

Alternatively, you can manually configure HTTPS as follows:

1. Obtain a Certificate

    An SSL certificate can be `self-signed <https://linuxize.com/post/creating-a-self-signed-ssl-certificate/>`_ for testing but should be obtained from a Certificate Authority for a production installation. Search `ssl certificate authorities <https://www.google.com/search?q=ssl+certificate+authorities>`_ for a list of providers. Most certificate authorities charge a fee for their services, however you can obtain free certificates from Let's Encrypt. If your instance of Tethys Portal is part of a larger organization website, contact your IT department to determine if an agreement with one of these authorities already exists.

2. Modify NGINX Configuration

    Once a certificate is obtained, it needs to be referenced in the NGINX configuration. The configuration file can be found at :file:`<TETHYS_HOME>/tethys_nginx.conf`.

    Change the ``listen`` port to 443 and enable SSL with the following options:

    .. code-block::

        server {
            listen   443 ssl;

            ssl_certificate    /<path_to_your_ssl_certs>/your_domain_name.pem; # (or bundle.crt)
            ssl_certificate_key    /<path_to_your_ssl_certs>/your_domain_name.key;
            ...
        }

    .. tip::

        If you need your site to be accessible through both secured (https) and non-secured (http) connections, you will need a server block for each type of connection. Simply copy the the server block and paste it below the original server block. Then modify one as show above.

    .. important::

        HTTPS traffic is expected to go through port 443 instead of port 80. hence the server block above listens on 443 instead of 80. Be sure to update your firewall accordingly if applicable (see: :ref:`production_firewall_config`).

.. _https_config_sso:

Single Sign On and HTTPS
========================

If you are using Single Sign On, there is an additional setting you will need to set for Python Social Auth to allow the redirect after login to work properly:

.. code-block::

    tethys settings --set SOCIAL_AUTH_REDIRECT_IS_HTTPS True
