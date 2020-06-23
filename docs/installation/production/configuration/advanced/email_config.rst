.. _setup_email_capabilities:

********************************************
Enable Forgotten Password Feature (Optional)
********************************************

**Last Updated:** May 2020

Tethys Portal provides a mechanism for resetting forgotten passwords that requires email capabilities, for which we recommend using Postfix. These instructions are for Ubuntu and CentOS systems. For other Linux distributions refer to the `Postfix Documentation <http://www.postfix.org/>`_ or search for a guide for installing on your distribution.

1. Install Postfix:
-------------------

    **Ubuntu**:

        Install the application as follows:

        .. code-block:: bash

            sudo apt install -y postfix libsasl2-modules

        Follow the prompts:

            * Select "Internet Site" as the type
            * Enter the ``SERVER_DOMAIN_NAME`` you identified during the :ref:`production_preparation` step when prompted.

        .. note::

            When installed with apt on Ubuntu, Postfix is started automatically and enabled to start when the server reboots.

    **CentOS**:

        Install the application as follows:

        .. code-block:: bash

            sudo yum install -y postfix cyrus-sasl-plain cyrus-sasl-md5

        Start and enable the Postfix server so that it starts up automatically when the server is restarted.

        .. code-block:: bash

            sudo systemctl start postfix
            sudo systemctl enable postfix


2. Configure Postfix
--------------------

1. Open the Postfix configuration file:

    .. code-block:: bash

        sudo vim /etc/postfix/main.cf

2. Locate the following variables and verify they are set appropriately:

    .. code-block:: bash

        myhostname = <SERVER_DOMAIN_NAME>

    .. note::

        Replace ``<SERVER_DOMAIN_NAME>`` with the value determined during the :ref:`production_preparation` step.

    .. code-block:: bash

        mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128

3. Restart Postfix to Effect Changes
------------------------------------

    .. code-block:: bash

        sudo systemctl restart postfix

4. Configure Tethys Email Settings
----------------------------------

Several email settings in the :file:`portal_config.yml` file need to be configured for the forget password functionality to work properly. Use the ``tethys settings`` command to set them as follows:

    .. code-block:: bash

        tethys settings --set EMAIL_BACKEND "django.core.mail.backends.smtp.EmailBackend" --set EMAIL_HOST localhost --set EMAIL_PORT 25 --set EMAIL_HOST_USER "" --set EMAIL_HOST_PASSWORD "" --set EMAIL_USE_TLS False --set DEFAULT_FROM_EMAIL "<DEFAULT_FROM_EMAIL>"

    .. note::

        Replace ``<DEFAULT_FROM_EMAIL>`` with the value determined during the :ref:`production_preparation` step. It should use the following format (with angle braces):

            .. code-block:: bash

                <Title foo@example.com>

5. Restart Tethys Portal
------------------------

If Tethys is already running, restart it as follows:

.. code-block:: bash

    sudo supervisorctl restart all
