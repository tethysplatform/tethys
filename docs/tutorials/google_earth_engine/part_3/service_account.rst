***********************************
Google Earth Engine Service Account
***********************************

**Last Updated:** May 2020

Up to this point, you've been using your personal Google account to authenticate with Google Earth Engine (see: :ref:`gee_authentication_step`). However, when you run an app that uses Google Earth Engine in a production environment, you will not want it to be using your personal credentials. Instead you will use a `service account <https://developers.google.com/earth-engine/service_account>`_, which is an account associated with an application instead of a user.

This tutorial requires you to already have a service account registered with Google Earth Engine. If you do not already have a service account, follow the instructions here: `How do I create a service account? <https://developers.google.com/earth-engine/service_account#how-do-i-create-a-service-account>`_. It may take several days for your registration application to be reviewed and approved.

The following topics are covered in this tutorial:

* Create Google Service Account Keys
* Use Service Account for Google Earth Engine Operations

.. figure:: ./resources/service_account_solution.png
    :width: 800px
    :align: center

0. Start From Previous Solution (Optional)
==========================================

If you wish to use the previous solution as a starting point:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine.git
    cd tethysapp-earth_engine
    git checkout -b rest-api-solution rest-api-solution-|version|

.. _service_account_key:

1. Create Service Account Key
=============================

After you have setup your service account, you will need to create a key that the app can use to authenticate with Google Earth Engine.

1. Navigate to `<https://console.developers.google.com/>`_.

2. Open the project that contains your Google Earth Engine Service Account using the drop-down menu located to the right of "Google APIs" in the header of the page.

3. Select **Credentials** from the left-hand navigation menu.

4. Click on the email or edit button of the service account you registered to see the account details.

5. Press the **Create Key** button.

6. Select JSON and press **CREATE**.

7. Locate the file that was downloaded an place it in a secure location.

.. note::

    The only copy of the key you generated is contained in the file that was downloaded. You cannot download it again. If you lose the file, repeat the process to generate a new key and delete the old one.

2. Configure App to Use Service Account
=======================================

The app needs to be configured to use the service account key that you downloaded in the previous step. Fortunately, the code is already in place to handle service accounts. You simply need to add your credentials to the :file:`gee/params.py` file.

1. Open the key file you downloaded in the previous step.

2. Copy the ``client_email`` value from the key file into the ``service_account`` variable of :file:`gee/params.py`.

3. Enter the path to the key file in the ``private_key`` variable of :file:`gee/params.py`.

.. note::

    As mentioned above, the logic is already in place to handle the service account. This is located at the top of :file:`gee/methods.py`:

    .. code-block:: python
        :emphasize-lines: 1-4

        if gee_account.service_account:
            try:
                credentials = ee.ServiceAccountCredentials(gee_account.service_account, gee_account.private_key)
                ee.Initialize(credentials)
            except EEException as e:
                print(str(e))
        else:
            try:
                ee.Initialize()
            except EEException as e:
                from oauth2client.service_account import ServiceAccountCredentials
                credentials = ServiceAccountCredentials.from_p12_keyfile(
                    service_account_email='',
                    filename='',
                    private_key_password='notasecret',
                    scopes=ee.oauth.SCOPE + ' https://www.googleapis.com/auth/drive '
                )
                ee.Initialize(credentials)

    Until now, the app has not had service account credentials, so it has been using the logic in the ``else`` clause of the conditional statement.

3. Test App Functionality with Service Account
==============================================

Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and verify the following:

1. Load several datasets and ensure the imagery is displayed on the map.
2. Test the Plot Area of Interest capability.
3. Upload a boundary shapefile and verify that the imagery is clipped to the extents of that boundary.

    .. note::

        You will not be able to debug or monitor the status of tasks submitted by the service account through the `Google Earth Engine Code Editor <http://localhost:8000/apps/earth-engine/viewer/>`_, because it is a separate account from your account.
