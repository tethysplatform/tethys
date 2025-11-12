.. _portal_admin_proxy_apps:

Proxy Apps
----------

Proxy apps are links to external web applications or websites. They are represented in the App Library page with an app tile just like native Tethys Apps. To manage the Proxy Apps in a Tethys Portal, click on the ``Proxy Apps`` link under the ``TETHYS APPS`` heading. Click on the ``ADD PROXY APP`` button to create a new Proxy App. Proxy Apps have many of the same configuration options as normal Tethys Apps including ``Name``, ``Description``, ``Tags``, ``Enabled``, ``Show in apps library`` and ``Order``, but there are a few options that are specific to Proxy apps (see Figure 16). A brief description of each option is provided below:

* **Name**: The name of the app that will appear on the app tile on the Apps Library page (e.g.: "My Proxy App").
* **Endpoint**: The URL that will be opened when the user clicks on the app tile of the proxy app (e.g.: ``https://my.proxy.app/foo/``).
* **Icon**: Override the icon/logo of the proxy app with a different icon. Accepts a relative path to a static file (e.g.: ``my-first-app/images/other-logo.png``) or a URL to an externally hosted image (e.g.: ``https://some.other-site.org/static/other-logo.png``).
* **Back url**: A URL to suggest as the back URL; usually points to the referring portal. If the Proxy App is a Tethys App on another Tethys Portal (>4.0.0), the Exit button for the app will be set to this URL (e.g.: ``https://this.portal.org/apps/``).
* **Description**: A description of the app that will be displayed when the user clicks on the info icon on the app tile.
* **Tags**: One or more tags for an app. Wrap each tag in double quotes and separate by commas (e.g.: ``"Hydrology","Grided Data","THREDDS"``).
* **Enabled**: Enable or disable the app. Disabled apps are not accessible to non-admin users.
* **Show in apps library**: Display the app on the Apps Library page. The app is still accessible by URL, but no app tile will be shown in the apps library.
* **Open in new tab**: Open the proxy app link in a new tab or window when on. Open it the same tab or window when off.
* **Order**: Force the order that apps are listed on the Apps Library page. Default order is alphabetical.
* **Display External Icon**: By default, this feature is turned off. When enabled, it adds an icon to the app tile to distinguish the proxy app from regular apps, indicating that it is an external link.

.. figure:: ../../images/site_admin/new_proxy_app.png
    :width: 675px

**Figure 16.** The Add Proxy App dialog.