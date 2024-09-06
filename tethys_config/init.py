# -*- coding: utf-8 -*-
"""
********************************************************************************
* Name: init.py
* Author: Nathan Swain
* Created On: 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
from django.utils import timezone
from .models import SettingsCategory, Setting


def initial_settings(apps, schema_editor):
    """
    Load the initial settings
    """

    # Create the general settings category
    general_category = SettingsCategory(name="General Settings")
    general_category.save()

    # Set default values for General Category
    setting_defaults(general_category)

    # Create the home page settings category
    home_category = SettingsCategory(name="Home Page")
    home_category.save()

    # Set default values for Home Page
    setting_defaults(home_category)


def custom_settings(apps, schema_editor):
    """
    Load the custom settings
    """

    # make sure initial settings exist
    categories = SettingsCategory.objects.all()
    if not categories:
        initial_settings(apps, schema_editor)

    # Create the custom styles settings category
    custom_styles_category = SettingsCategory(name="Custom Styles")
    custom_styles_category.save()

    # Set default values for Custom Styles
    setting_defaults(custom_styles_category)

    # Create the custom template settings category
    custom_templates_category = SettingsCategory(name="Custom Templates")
    custom_templates_category.save()

    # Set default values for Custom Templates
    setting_defaults(custom_templates_category)


def reverse_init(apps, schema_editor):
    """
    Reverse the initial settings
    """

    categories = SettingsCategory.objects.all()
    settings = Setting.objects.all()

    for setting in settings:
        setting.delete()

    for category in categories:
        category.delete()


def reverse_custom(apps, schema_editor):
    """
    Reverse the custom settings
    """

    categories = SettingsCategory.objects.all()
    settings = Setting.objects.all()

    for setting in settings:
        if setting.name in [
            "Portal Base CSS",
            "Home Page CSS",
            "Apps Library CSS",
            "Home Page Template",
            "Apps Library Template",
        ]:
            setting.delete()

    for category in categories:
        if category.name in ["Custom Styles", "Custom Templates"]:
            category.delete()


def setting_defaults(category):
    # Figure out what time it is right now
    now = timezone.now()

    if category.name == "General Settings":
        category.setting_set.create(
            name="Site Title", content="Tethys Portal", date_modified=now
        )

        category.setting_set.create(
            name="Favicon",
            content="/tethys_portal/images/default_favicon.png",
            date_modified=now,
        )

        category.setting_set.create(
            name="Brand Text", content="Tethys Portal", date_modified=now
        )

        category.setting_set.create(
            name="Brand Image",
            content="/tethys_portal/images/tethys-on-blue-icon-only.svg",
            date_modified=now,
        )

        category.setting_set.create(
            name="Brand Image Height", content="", date_modified=now
        )

        category.setting_set.create(
            name="Brand Image Width", content="", date_modified=now
        )

        category.setting_set.create(
            name="Brand Image Padding", content="", date_modified=now
        )

        category.setting_set.create(
            name="Apps Library Title", content="Apps", date_modified=now
        )

        category.setting_set.create(
            name="Primary Color", content="#0a62a9", date_modified=now
        )

        category.setting_set.create(
            name="Secondary Color", content="#7ec1f7", date_modified=now
        )

        category.setting_set.create(
            name="Background Color", content="", date_modified=now
        )

        category.setting_set.create(
            name="Primary Text Color", content="", date_modified=now
        )

        category.setting_set.create(
            name="Primary Text Hover Color", content="", date_modified=now
        )

        category.setting_set.create(
            name="Secondary Text Color", content="", date_modified=now
        )

        category.setting_set.create(
            name="Secondary Text Hover Color", content="", date_modified=now
        )

        category.setting_set.create(
            name="Footer Copyright",
            content=f"Copyright © {now:%Y} Your Organization",
            date_modified=now,
        )

    elif category.name == "Home Page":
        category.setting_set.create(
            name="Hero Text",
            content="Welcome to Tethys Portal,\nthe hub for your apps.",
            date_modified=now,
        )

        category.setting_set.create(
            name="Blurb Text",
            content="Tethys Portal is designed to be customizable, so that you can host "
            "apps for your\norganization. You can change everything on this page "
            "from the Home Page settings.",
            date_modified=now,
        )

        category.setting_set.create(
            name="Feature 1 Heading", content="Feature 1", date_modified=now
        )

        category.setting_set.create(
            name="Feature 1 Body",
            content="Use these features to brag about all of the things users can do with "
            "your instance of Tethys Portal.",
            date_modified=now,
        )

        category.setting_set.create(
            name="Feature 1 Image",
            content="/tethys_portal/images/placeholder.gif",
            date_modified=now,
        )

        category.setting_set.create(
            name="Feature 2 Heading", content="Feature 2", date_modified=now
        )

        category.setting_set.create(
            name="Feature 2 Body",
            content="Describe the apps and tools that your Tethys Portal provides and add "
            "custom pictures to each feature as a finishing touch.",
            date_modified=now,
        )

        category.setting_set.create(
            name="Feature 2 Image",
            content="/tethys_portal/images/placeholder.gif",
            date_modified=now,
        )

        category.setting_set.create(
            name="Feature 3 Heading", content="Feature 3", date_modified=now
        )

        category.setting_set.create(
            name="Feature 3 Body",
            content="You can change the color theme and branding of your Tethys Portal in a "
            "jiffy. Visit the Site Admin settings from the user menu and select "
            "General Settings.",
            date_modified=now,
        )

        category.setting_set.create(
            name="Feature 3 Image",
            content="/tethys_portal/images/placeholder.gif",
            date_modified=now,
        )

    elif category.name == "Custom Styles":
        for setting_name in [
            "Portal Base CSS",
            "Home Page CSS",
            "Apps Library CSS",
            "Accounts Base CSS",
            "Login CSS",
            "Register CSS",
            "User Base CSS",
        ]:
            category.setting_set.create(
                name=setting_name, content="", date_modified=now
            )

    elif category.name == "Custom Templates":
        for setting_name in [
            "Home Page Template",
            "Apps Library Template",
            "Login Page Template",
            "Register Page Template",
            "User Page Template",
            "User Settings Page Template",
        ]:
            category.setting_set.create(
                name=setting_name, content="", date_modified=now
            )

    category.save()


def tethys4_site_settings(apps, schema_editor):
    """
    Update the values of Site Settings for a new version of Tethys Platform.

    Args:
        version (str): Semantic version of Tethys Platform to update values for (e.g. '4.0.0').
    """
    # Update the brand image setting if still set at default
    brand_image_setting = Setting.objects.filter(category__name="General Settings").get(
        name="Brand Image"
    )

    if brand_image_setting.content == "/tethys_portal/images/tethys-logo-75.png":
        brand_image_setting.content = "/tethys_portal/images/tethys-logo-25.png"
        brand_image_setting.save()

    # Update the app library title
    app_library_setting = Setting.objects.filter(category__name="General Settings").get(
        name="Apps Library Title"
    )

    if app_library_setting.content == "Apps Library":
        app_library_setting.content = "Apps"
        app_library_setting.save()

    # Update the copyright if default
    copyright_setting = Setting.objects.filter(category__name="General Settings").get(
        name="Footer Copyright"
    )

    now = timezone.now()
    if copyright_setting.content == "Copyright © 2019 Your Organization":
        copyright_setting.content = f"Copyright © {now:%Y} Your Organization"
        copyright_setting.save()
