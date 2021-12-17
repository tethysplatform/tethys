.. _azure_vm_config_https:

*****************************
Configure HTTPS (Recommended)
*****************************

**Last Updated:** November 2021

HTTPS is the secure way of serving websites that won't compromise the data of the website or your users. Most web browsers will warn users when they are using a site that is not secured with HTTPS, which can be a deterrent for some users. This method involves configuring Nginx on the VM to manage the SSL certificates required for HTTPS. The good news is that using Certbot, this can be completely automated after some initial set up.

1. Complete the Certbot section of the :ref:`Configure HTTPS <https_config>` tutorial to obtain free SSL certificates and configure Nginx for HTTPS/SSL.

2. Open the HTTPS port for the Azure VM if you did not do so already when creating the VM:

    a. Navigate to the Overview page for the VM Resource.
    b. Click on **Networking** in left navigation panel.
    c. Click on the **Add inbound port rule** button.
    d. Fill out the **Add inbound security rule** form as follows:

        * **Source**: Any
        * **Source port ranges**: *
        * **Destination**: Any
        * **Service**: HTTPS
        * **Action**: Allow
        * **Priority**: <use_default>
        * **Name**: HTTPS
        * **Description**: <leave_blank>

    e. Press the **Add** button.

.. figure:: ../images/configure--https.png
    :width: 800px
    :alt: Add inbound security rule form filled out.

    **Figure 1.** Add inbound security rule form filled out.

3. Visit your portal url using HTTPS to verify that it worked (e.g. "https://myfirsttethys.org"). Look for the indicator in your web browser, usually a lock symbol.

.. figure:: ../images/configure--https-secure.png
    :width: 800px
    :alt: Screenshot of a Tethys Portal showing HTTPS secure symbol

    **Figure 2.** Screenshot of a Tethys Portal showing HTTPS secure symbol.
