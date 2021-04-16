.. _whats_new:

**********
What's New
**********

**Last Updated:** April 2021

Refer to this article for information about each new release of Tethys Platform.

Release |version|
==================

Select Input Gizmo
==================

* Add ``id`` attribute to the ``form-group`` of the ``SelectInput`` gizmo to allow it to be selected in custom JavaScript.

See: `Pull Request 616 <https://github.com/tethysplatform/tethys/pull/616>`_

Cesium Map View Gizmo
=====================

* Add support for time-enabled layers for CesiumMapView gizmo via the ``MVLayer`` specification. 
* This is done by listing timesteps corresponding the times of a time-enabled WMD layer via the ``times`` parameter of ``MVLayer``.
* Note: time-enabled layers are not supported in MapView gizmo yet.

See: :ref:`gizmo_mvlayer`

Single Sign On
==============

* Single Sign On / Social Login via ArcGIS Online / Enterprise Portal now supported. See: :ref:`social_auth_arcgis`.
* Add clarification and fix typos in documentation for OneLogin SSO. See: :ref:`social_auth_onelogin`.

See: :ref:`single_sign_on_config`

Multi-Tenant SSO
================

* Implemented Multi-Tenant SSO support for providers that support it.
* Allows Tethys Portals to use authentication from different tenants of the same authentication service.
* When enabled, users are prompted to provide the name of their tenant/organization before being redirected to login page for that provider.
* Supported providers include: OneLogin, Okta, Azure AD, and Microsoft ADFS.

See: :ref:`multi_tenant_sso_config`

User Profile and Settings
=========================

* Removed the username from the URL pattern for User Profile and Settings pages to address security concern.
* Viewing other user's profiles is no longer possible.
* The profile and settings pages only display profile and settings for the logged-in user.

See: :ref:`tethys_user_pages`

Password Reset
==============

* Changes configuration for Password Reset feature of Tethys Portal to be the same as the configuration for MFA email support.
* This allows the emails sent by the Password Reset and MFA features to be sent from the same email address and alias.

See: :ref:`setup_email_capabilities`

Tethys App Settings
===================

* Added ``set_custom_setting method`` to ``TethysAppBase`` to allow setting ``CustomSettings`` programmatically.
* Added a UUID type to ``CustomSetting`` model.
* UUID type can take ``uuid`` instances or strings.

See: :ref:`app_base_class_api`

Tethys App Admin Settings
=========================

* Adds ``color`` parameter to the App Settings admin page to allow portal admins to change app color.

See: `Issue 656 <https://github.com/tethysplatform/tethys/issues/656>`_

Bug Fixes
=========

* Resolves issue with default Gravatar image not displaying for users who haven't defined an email address. See: `Issue 637 <https://github.com/tethysplatform/tethys/issues/637>`_.
* Fixes an issue where renaming an installed app in the admin pages would cause the app throw 500 errors and no longer be accessible. See: `Issue 653 <https://github.com/tethysplatform/tethys/issues/653>`_.
* Removed EXIF, IPTC, and XMP metadata from all Tethys Portal images to address metadata leakage security concern. See: `Issue 630 <https://github.com/tethysplatform/tethys/issues/630>`_.
* Resolves various issues with JobsTable gizmo: dates not being parsed correctly, set job status to error if exception raised during call to ``execute()``, label could not be set when retrieving jobs through job manager. See: `Issue 641 <https://github.com/tethysplatform/tethys/issues/641>`_.
* Fixes issue where a user's API token was not visible when MFA was enabled and `MFA_REQUIRED` was `False`. See: `Issue 626 <https://github.com/tethysplatform/tethys/issues/626>`_
* Move ``TethysJob`` model import out of module scope in ``JobsTable`` gizmo to prevent import issues. See: `Pull Request 618 <https://github.com/tethysplatform/tethys/pull/618>`_.
* Pin Django Channels dependency to 2.* to prevent accidental upgrades to 3.*, which breaks Tethys. See: `Pull Request 680 <https://github.com/tethysplatform/tethys/pull/680>`_

Prior Release Notes
===================

.. toctree::
   :maxdepth: 2

   whats_new/prior_releases
