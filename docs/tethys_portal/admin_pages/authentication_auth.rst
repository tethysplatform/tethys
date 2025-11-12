.. _admin_pages_authentication_auth:

********************************
Authentication and Authorization
********************************

Permissions and users can be managed from the administrator dashboard using ``Users`` link under the ``AUTHENTICATION AND AUTHORIZATION`` heading. Figure 3 shows an example of the user management page for a user named John.

.. figure:: ../../images/tethys_portal/tethys_portal_user_management.png
    :width: 675px

**Figure 3.** User management for Tethys Portal.

.. _tethys_portal_app_permission_groups:

Assign App Permission Groups
----------------------------

There are two ways to assign an app permission group to a user. The first way is to use the ``Users`` dialog on the ``Change Group`` page:

  1.  Go to the administrator dashboard and select the ``Groups`` link under the ``Authentication and Authorization`` heading. 
  2. Select the group and locate the ``Users`` dialog of the ``Change Group`` page.
  3. All users will appear in the ``Available Users`` list box. Adding a user to the permissions group is done by moving the desired user(s) to the ``Chosen Users`` list box. 

The second way is to use the ``Groups`` dialog on the ``Change User`` page:

  1. Go to the administrator dashboard and select the ``Users`` link under the ``Authentication and Authorization`` heading.
  2. Select the desired user and locate the ``Groups`` dialog under the ``Permissions`` heading of the ``Change User`` page.
  3. All app permission groups will appear in the ``Available Groups`` list box. Assigning the permission group is done by moving the permission group to the ``Chosen Groups`` list box.

.. note:: Although the permissions may also appear in the ``User Permissions`` list box, they cannot be properly assigned in the ``Change User`` dialog.

Assign App Access Permissions
-----------------------------

Administrators of a Tethys Portal can control access to each installed app and/or proxy app in the portal. However, this feature is disabled by default. To enable app access control set the following setting in the ``portal_config.yaml``:

.. code-block:: yaml

    settings:
      TETHYS_PORTAL_CONFIG:
        ENABLE_RESTRICTED_APP_ACCESS: True

.. caution::

    The effect of the ``ENABLE_RESTRICTED_APP_ACCESS`` setting is negated if ``ENABLE_OPEN_PORTAL`` is also set to `True`.

There are two ways to assign app permissions to users and groups. The first method is to use the ``Change Group`` page from the ``Group`` section of the administrator dashboard. The second method is using the ``object permission`` button from the ``Change Tethys App`` or ``Change Proxy App`` page of each individual app. The first method is recommended over the second one when working with app permissions at the group level because it offers a more responsive interface and it facilitates working with multiple permissions from different apps and groups at the same time. Both methods are described below.

Change Group Method (Recommended)
+++++++++++++++++++++++++++++++++

To assign app permissions to a user using the ``Change Group`` method:
  1. Go to the administrator dashboard and select the ``Groups`` link under the ``Authentication and Authorization`` heading.
  2. Select the link with the group name from the list.
  3. On the ``Change Group`` page you can assign a group permission to access a specific proxy app from the ``Proxy Apps`` multiselect field or installed app from the ``Apps`` multiselect field by moving an app from the available app box to the chosen app box (see Figure 4).
  4. When an installed app is added to the chosen apps box, the form will dynamically display all the permissions and groups associated with that app if there are any (see Figure 5). 
  5. Individual permissions can be added to the group by moving the permissions from the available box of the specific app to the chosen box. In addition, all the permissions from another group that are associated with the specific app can also be added by moving the specific group from the available groups box to the chosen groups box. 
  6. The ``Change Group`` form then needs to be saved for changes to take effect.

.. figure:: ../../images/tethys_portal/tethys_portal_assign_perm4.png
   :width: 900px

**Figure 4.** Change Group - Add app access.

.. figure:: ../../images/tethys_portal/tethys_portal_assign_perm5.png
   :width: 900px

**Figure 5.** Change Group - Add permissions from available permissions or groups.

.. note::

    Since assigning the individual app permissions one by one can be a cumbersome process, we highly recommend that you use the ``Change Group`` page when working with multiple app permissions.

Object Permissions Method
+++++++++++++++++++++++++

To assign a singular app permission to a user using the ``Change Tethys App`` page:
  1. Go to the administrator dashboard and scroll down to the ``Installed Apps`` link under the ``Tethys Apps`` heading.
  2. Select the link with the app name from the list.
  3. In the upper right corner of the ``Change Tethys App`` page click the ``Object Permissions`` button (see Figure 6).
  4. On the ``Object Permissions`` page you can assign app-specific permissions to a user by entering the username in the ``User Identification`` field and pressing the ``Manage user`` button (see Figure 7).
  5. The same method can be used to add app permissions to a group using the ``Group`` section of the ``Object Permissions`` page. Previously added App permissions will be listed in the table on this page and can be edited by clicking the ``Edit`` link (see Figure 8).

A similar process can be done for proxy apps.

.. figure:: ../../images/tethys_portal/tethys_portal_assign_perm1.png
   :width: 900px

**Figure 6.** Object Permissions button.

.. figure:: ../../images/tethys_portal/tethys_portal_assign_perm2.png
   :width: 900px

**Figure 7.** Object Permissions page.

.. figure:: ../../images/tethys_portal/tethys_portal_assign_perm3.png
   :width: 900px

**Figure 8.** Link to edit Object Permissions.

Anonymous User
--------------

The ``AnonymousUser`` can be used to assign permissions and permission groups to users who are not logged in. This means that you can define permissions for each feature of your app, but then assign them all to the ``AnonymousUser`` if you want the app to be publicly accessible.