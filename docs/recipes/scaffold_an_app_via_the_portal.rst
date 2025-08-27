.. _scaffold_an_app_via_the_portal :



******************************************
Scaffold and Install an App via the Portal
******************************************

.. important::

    This feature is only available to **staff/admin users**.

    This recipe assumes that you have already started your Tethys server (see :ref:`start_tethys`).

Tethys Platform provides an easy way for **staff/admin users** to create new app projects via the Tethys Portal itself, rather than via command line.

.. note::

    See :ref:`scaffold_an_app_via_command_line` if you need to automate an install or otherwise want to use the command line.

Recipe
++++++

1. Browse to your Tethys Portal and Log in as a Staff User
==========================================================

This is just a normal login with staff user credentials. If you are not a staff user, you will need to speak with your Tethys Portal administrator to determine if you can become a staff user.

2. Click the "Create App" Card on the Apps Library page
=======================================================

This will not show up if you are not a staff user.

.. figure:: ../../docs/images/recipes/create_app_via_gui.png
    :width: 800px
    :align: center

    Create App Icon on Apps Library Page as Staff User  

3. Fill Out the Form
====================

.. figure:: ../../docs/images/recipes/create_app_form.png
    :width: 600px
    :align: center

    Create App Form

Field Descriptions:
-------------------

- **Scaffold template:** The development paradigm/environment you want to follow. There are three scaffolds to choose from: Standard, Component (Beta), and ReactJS (Beta).
- **Project Name:** The name of the new Tethys app project to create. This corresponds to the folder name and python package name for your app project. Only lowercase letters, numbers, and underscores allowed.
- **App Name:** The proper name (i.e. title) of the app.
- **App Description:** A brief description of the app.
- **App Theme Color:** Main theme color of the app.
- **Tags:** Tags or keywords for the app that can be used to search for and/or filter the app.
- **Author Name:** Your name. This will be auto populated if you have this information saved to your Tethys Portal account.
- **Author Email:** Your email address. This will be auto populated if you have this information saved to your Tethys Portal account.
- **License:** The license you want to develop/release your app under. Leave blank if unsure.

4. Click Create and Wait for App to Be Created
==============================================

After clicking Create, you will be redirected to a page showing the creation progress.

.. figure:: ../../docs/images/recipes/app_being_created.png
    :width: 800px
    :align: center

    Page Showing Progress of App Being Created

.. important::

    Do not navigate away from this page or the creation of your app could be interrupted and/or corrupted.

4. View Your New App
====================

When the app is done being created in step 3, your browser will automatically redirect to your new app.

.. figure:: ../../docs/images/recipes/scaffold_pic.png
    :width: 800px
    :align: center   

The code that was scaffolded behind the app can be found in the same directory from which you started your Tethys server via command line.

.. tip::
    
    If you are unsure of which directory your Tethys server is/was running in, you can:

    1. Return to the terminal that is/was running the server (via the ``tethys start`` command)
    2. Kill the server with Ctrl + C
    3. Enter the ``pwd`` command, which will print out the location.