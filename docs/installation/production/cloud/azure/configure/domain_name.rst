.. _azure_vm_config_domain_name:

********************************
Assign Domain Name (Recommended)
********************************

**Last Updated:** November 2021

A domain name is the text that users enter in a web browser to visit a website (e.g. google.com). Behind the scenes, this text is mapped to the IP address of the server, which is the unique numeric address that can be used to locate your website (e.g ``20.109.16.186``). VMs on Azure can be assigned a generic, Azure supplied, domain name (e.g.: ``my-first-tethys.westus2.cloudapp.azure.com``) or a custom domain (e.g. ``myfirsttethys.org``). With either option there are a few configuration steps that need to be performed in Tethys assigning the domain name.

Generic Domain Name
===================

Create a generic, Azure supplied, domain name as follows:

1. Navigate to the Overview page for the VM Resource.
2. Locate the **DNS name** field in the **Essentials** section.
3. Follow the link next to **DNS name**. It will either be "Not configured" or the domain name if previously configured.
4. Enter a **DNS name label**. This is labeled as optional, but it is actually required to enable the generic domain.
5. Press the **Save** button to enable the domain name.

.. figure:: ../images/configure--generic-domain-name.png
    :width: 800px
    :alt: Screenshot of the domain name configuration page for an Azure VM

    **Figure 1.** Screenshot of the domain name configuration page for an Azure VM.

Custom Domain Name
==================

Assigning a custom domain name is a little more involved and depends on how you obtain the domain name.

1. Acquire a domain name if you don't have one to use already: `Google: Domain Name <https://www.google.com/search?q=domain+name>`_
2. Make sure the Public IP address assigned to the Azure VM is static:

    a. Navigate to the Overview page for the VM Resource.
    b. Locate the **Public IP address** field in the **Essentials** section.
    c. Click on the IP address link.
    d. Under **IP address assignment** select the **Static** radio option (see Figure 3).
    e. Click **Save** to save the changes.

3. Create an A-name record that associates the domain name with the public IP address of the Azure VM. The company you bought the domain name from will usually provide a way to do this. If your domain name belongs to your organization, you will need to contact your IT department to find out how this is to be done.

For more information about creating a custom domain name for Azure VMs read the following article: `Add Custom Domain to Azure VM or resource <https://docs.microsoft.com/en-us/azure/virtual-machines/custom-domain>`_.

Tethys Configuration
====================

After assigning a domain name to the Azure VM, generic or custom, add it to the configuration of Tethys Platform in two places:

NGINX Configuration
-------------------

1. Open ``$TETHYS_HOME/config/tethys_nginx.conf`` in your favorite command line text editor (e.g. vim or nano).

2. Set the ``server_name`` parameter to the domain name:

    .. code-block::
        :emphasize-lines: 13

        # tethys_nginx.conf

        # the upstream component nginx needs to connect to
        upstream channels-backend {
            server 127.0.0.1:8000;
        }

        # configuration of the server
        server {
            # the port your site will be served on
            listen      80;
            # the domain name it will serve for
            server_name <domain_name>; # substitute your machine's IP address or FQDN
            ...

3. Restart the NGINX service

    .. code-block::

        sudo systemctl restart nginx.service


Tethys Portal Configuration
---------------------------

1. Open ``$TETHYS_HOME\portal_config.yml`` using your favorite command line text editor (e.g. vim or nano).

2. Add the domain name as another item under the ``ALLOWED_HOSTS`` setting.

3. Remove the ``'*'`` entry if it is still listed in ``ALLOWED_HOSTS`` setting.

4. Restart the Tethys service

    .. code-block::

        sudo systemctl restart tethys.service
