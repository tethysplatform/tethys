.. _setup_email_capabilities:

**************************************
Forgotten Password Recovery (Optional)
**************************************

**Last Updated:** May 2020

Tethys Portal provides a mechanism for resetting forgotten passwords that requires email capabilities. This guide discusses two options for enabling email capabilities to support this feature.

Third-Party Email Services
==========================

If your organization doesn't have an existing email service that you can use, we recommend using a third party email relay service to enable email capabilities on your Tethys Portal. There are many regulations regarding email that make it much more difficult to deliver email from your own email server without it going straight to the spam folder. Most email relay services take care of the legal obstacles and many of them provide a free tier. An internet search for "email relay service" will yield many options: `Google: email relay service <https://www.google.com/search?q=email+relay+service>`_.

Example with SendGrid
=====================

Tethys Platform does not endorse one provider over another, however it is helpful to see a concrete example. The following instructions discuss how to setup emailing capabilities with SendGrid as an example. Setting up email capabilities with other services will be similar.

1. Sign up for SendGrid Account
-------------------------------

Go to `SendGrid New Account <https://signup.sendgrid.com/>`_ and signup for an account.

2. Sender Verification
----------------------

You will need to setup a verified email address or domain to be used as the "From" email address. The easiest option is to setup single sender verification with your own email address or another email address you have access to. However, the preferred method is to setup Domain Authentication, but you will need access to the DNS settings for your domain. For more information on this topic, read `Sender Identity <https://www.twilio.com/docs/sendgrid/for-developers/sending-email/sender-identity>`_.

For now, setup up Single Sender Verification by following these instructions: `Single Sender Verification <https://www.twilio.com/docs/sendgrid/ui/sending-email/sender-verification>`_.

3. Create SMTP Relay Key
------------------------

After logging in perform the following steps to create an SMTP relay key:

1. Click on your name in the top left corner of the screen to open the menu.
2. Select **Setup Guide**.
3. Click on the **Start** button in the *"Integrate using our Web API or SMTP relay"* section.
4. Choose **SMTP Relay**.
5. Provide a name for the key.
6. Press **Create Key**.
7. Copy the API key and save it to a safe location.

.. important::

    You will not be able to copy the key later, so don't forget to save it somewhere safe.

4. Set Email Settings in :file:`portal_config.yml`
--------------------------------------------------

Configure the Tethys Portal to use SendGrid as the email relay as follows:

.. code-block::

    tethys settings --set EMAIL_BACKEND "django.core.mail.backends.smtp.EmailBackend" --set EMAIL_HOST "smtp.sendgrid.net" --set EMAIL_PORT 25 --set EMAIL_HOST_USER "apikey" --set EMAIL_HOST_PASSWORD "<SENDGRID_API_KEY>" --set EMAIL_USE_TLS True --set DEFAULT_FROM_EMAIL "<VERIFIED_SENDER_EMAIL_ADDRESS>"

.. note::

    Replace <SENDGRID_API_KEY> with the key that you generated in step 3 and replace <VERIFIED_SENDER_EMAIL_ADDRESS> with the email address that you verified in step 2. Note that the value of EMAIL_HOST_USER should be literally "apikey" as shown in the example above, not the API key you generated. Only replace the variables in angle brackets (<>).


Setup Your Own Email Server
===========================

Alternatively, you can try setting up your own email server using Postfix. We don't recommend this, however, because you will then need to make sure you are meeting any government regulations and obtain a certificate signed by a third-party for your emails to have a chance of making it to the user's inbox.

These instructions are for Ubuntu and Rocky Linux systems. For other Linux distributions refer to the `Postfix Documentation <http://www.postfix.org/>`_ or search for a guide for installing on your distribution.

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

    **Rocky Linux**:

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

        tethys settings --set EMAIL_CONFIG.EMAIL_BACKEND "django.core.mail.backends.smtp.EmailBackend" --set EMAIL_CONFIG.EMAIL_HOST localhost --set EMAIL_CONFIG.EMAIL_PORT 25 --set EMAIL_CONFIG.EMAIL_HOST_USER "" --set EMAIL_CONFIG.EMAIL_HOST_PASSWORD "" --set EMAIL_CONFIG.EMAIL_USE_TLS False --set EMAIL_CONFIG.DEFAULT_FROM_EMAIL "<DEFAULT_FROM_EMAIL>" --set EMAIL_CONFIG.EMAIL_FROM "<EMAIL_FROM>"

    .. note::

        Replace ``<DEFAULT_FROM_EMAIL>`` with the value determined during the :ref:`production_preparation` step. It should use the following format (without angle braces):

            .. code-block:: bash

                <foo@example.com>

        Replace ``<EMAIL_FROM>`` with the "FROM" email alias or name of sender determined during the :ref:`production_preparation` step.

            .. code-block:: bash

                "John Smith"

5. Restart Tethys Portal
------------------------

If Tethys is already running, restart it as follows:

.. code-block:: bash

    sudo supervisorctl restart all
