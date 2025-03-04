.. _production_firewall_config:

**********************
Firewall Configuration
**********************

**Last Updated:** October 2024

If a firewall is enabled on the server on which you are installing Tethys Portal, you may need to configure it to allow connections through the HTTP port(s). This part of the production installation guide will provide instructions for how this is to be done on the default firewall applications installed on Ubuntu (`UWF <https://help.ubuntu.com/community/UFW>`_) and Rocky Linux (`firewalld <https://firewalld.org/documentation/>`_ servers.

Configure Firewall Without SSL (HTTP)
=====================================

Run the following commands to open the HTTP port (80):

    **Ubuntu**:

        Use the ``ufw app list`` command to list the available configurations:

        .. code-block:: bash
        
            sudo ufw app list  # e.g.: ‘Nginx Full’, ‘Nginx HTTPS’, ‘Nginx HTTP’

        Enable the desired configuration:

        .. code-block:: bash

            sudo ufw allow 'Nginx HTTP'

    **Rocky Linux**:

        Install firewalld if not already installed:

        .. code-block:: bash

            sudo dnf install firewalld -y

        Enable and start firewald:

        .. code-block:: bash

            sudo systemctl enable firewalld
            sudo systemctl start firewalld

        Open the HTTP port (80):

        .. code-block:: bash

            sudo firewall-cmd --permanent --zone=public --add-service=http
            sudo firewall-cmd --reload

Configure Firewall With SSL (HTTPS)
===================================

Run the following commands to open the HTTPS port (443):

    **Ubuntu**:

        Use the ``ufw app list`` command to list the available configurations:

        .. code-block:: bash

            sudo ufw app list  # e.g.: ‘Nginx Full’, ‘Nginx HTTPS’, ‘Nginx HTTP’

        Enable the desired configuration:

        .. code-block:: bash

            sudo ufw allow 'Nginx HTTPS'

    **Rocky Linux**:

        Install firewalld if not already installed:

        .. code-block:: bash

            sudo dnf install firewalld -y

        Enable and start firewald:

        .. code-block:: bash

            sudo systemctl enable firewalld
            sudo systemctl start firewalld

        Open the HTTPS port (443):

        .. code-block:: bash

            sudo firewall-cmd --permanent --zone=public --add-service=https
            sudo firewall-cmd --reload

Configure Firewall Both (HTTP and HTTPS)
========================================

Run the following commands to open the HTTPS port (443) and HTTP port (80):

    **Ubuntu**:

        Use the ``ufw app list`` command to list the available configurations:

        .. code-block:: bash

            sudo ufw app list  # e.g.: ‘Nginx Full’, ‘Nginx HTTPS’, ‘Nginx HTTP’

        Enable the desired configuration:

        .. code-block:: bash

            sudo ufw allow 'Nginx Full'

    **Rocky Linux**:

        Install firewalld if not already installed:

        .. code-block:: bash

            sudo dnf install firewalld -y

        Enable and start firewald:

        .. code-block:: bash

            sudo systemctl enable firewalld
            sudo systemctl start firewalld

        Open the HTTP port (80) and HTTPS port (443):

        .. code-block:: bash

            sudo firewall-cmd --permanent --zone=public --add-service=http
            sudo firewall-cmd --permanent --zone=public --add-service=https
            sudo firewall-cmd --reload
