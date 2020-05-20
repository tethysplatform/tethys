.. _production_firewall_config:

**********************
Firewall Configuration
**********************

**Last Updated:** May 2020


16) Open HTTP Port on Firewall (if applicable)

    If your server employs a firewall, open the HTTP port like so:

    .. code-block::

        sudo firewall-cmd --permanent --zone=public --add-service=http
        sudo firewall-cmd --reload

    .. note::

        The commands to manage your firewall may differ. Ensure the HTTP port (80) is open.

SSL

Be sure to update your firewall accordingly if applicable. If you followed the production installation instructions exactly, this means you'll need to run:

::

    sudo firewall-cmd --permanent --zone=public --add-service=https
    sudo firewall-cmd --reload