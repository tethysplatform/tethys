.. _https_config:

*****************************
Configure HTTPS (Recommended)
*****************************

**Last Updated:** May 2020

SSL and TLS are the standard technologies for establishing a secured connection between a web server and a browser. In order to create a secured connection, a certificate and key are needed.

1. Obtain a Certificate

    An SSL certificate can be `self-signed <https://linuxize.com/post/creating-a-self-signed-ssl-certificate/>`_ for testing but should be purchased from a Certificate Authority for a production installation. Some of the top certificate authorities include: Digicert, VertiSign, GeoTrust, Comodo, Thawte, GoDaddy, and Nework Solutions. If your instance of Tethys Portal is part of a larger organization, contact your IT department to determine if an agreement with one of these authorities already exists.

2. Modify NGINX Configuration

    Once a certificate is obtained, it needs to be referenced in the NGINX configuration. The configuration file can be found at :file:`<TETHYS_HOME>/tethys_nginx.conf`.

    Change the ``listen`` port to 443 and enable SSL with the following options:

    .. code-block::

        server {
            listen   443;

            ssl    on;
            ssl_certificate    /<path_to_your_ssl_certs>/your_domain_name.pem; (or bundle.crt)
            ssl_certificate_key    /<path_to_your_ssl_certs>/your_domain_name.key;
            ...
        }

    .. tip::

        If you need your site to be accessible through both secured (https) and non-secured (http) connections, you will need a server block for each type of connection. Simply copy the the server block and paste it below the original server block. Then modify one as show above.

    .. important::

        HTTPS traffic is expected to go through port 443 instead of port 80. hence the server block above listens on 443 instead of 80. Be sure to update your firewall accordingly if applicable (see: :ref:`production_firewall_config`).