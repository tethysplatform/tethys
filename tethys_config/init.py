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
    # Figure out what time it is right now
    now = timezone.now()

    # Create the general settings category
    general_category = SettingsCategory(name="General Settings")
    general_category.save()

    general_category.setting_set.create(name="Site Title",
                                        content="Tethys Portal",
                                        date_modified=now)

    general_category.setting_set.create(name="Favicon",
                                        content="/static/tethys_portal/images/default_favicon.png",
                                        date_modified=now)

    general_category.setting_set.create(name="Brand Text",
                                        content="Tethys Portal",
                                        date_modified=now)

    general_category.setting_set.create(name="Brand Image",
                                        content="/static/tethys_portal/images/tethys-logo-75.png",
                                        date_modified=now)

    general_category.setting_set.create(name="Brand Image Height",
                                        content="60px",
                                        date_modified=now)

    general_category.setting_set.create(name="Brand Image Width",
                                        content="",
                                        date_modified=now)

    general_category.setting_set.create(name="Brand Image Padding",
                                        content="",
                                        date_modified=now)

    general_category.setting_set.create(name="Apps Library Title",
                                        content="Apps Library",
                                        date_modified=now)

    general_category.setting_set.create(name="Primary Color",
                                        content="#0a62a9",
                                        date_modified=now)

    general_category.setting_set.create(name="Secondary Color",
                                        content="#1b95dc",
                                        date_modified=now)

    general_category.setting_set.create(name="Primary Text Color",
                                        content="#dddddd",
                                        date_modified=now)

    general_category.setting_set.create(name="Primary Text Hover Color",
                                        content="#ffffff",
                                        date_modified=now)

    general_category.setting_set.create(name="Secondary Text Color",
                                        content="#dddddd",
                                        date_modified=now)

    general_category.setting_set.create(name="Secondary Text Hover Color",
                                        content="#ffffff",
                                        date_modified=now)

    general_category.setting_set.create(name="Background Color",
                                        content="#efefef",
                                        date_modified=now)

    general_category.setting_set.create(name="Footer Copyright",
                                        content="Copyright © 2015 Your Organization",
                                        date_modified=now)

    general_category.save()

    # Create the home page settings category
    home_category = SettingsCategory(name="Home Page")
    home_category.save()

    home_category.setting_set.create(name="Hero Text",
                                     content="Welcome to Tethys Portal,\nthe hub for your apps.",
                                     date_modified=now)

    home_category.setting_set.create(name="Blurb Text",
                                     content="Tethys Portal is designed to be customizable, so that you can host "
                                             "apps for your\norganization. You can change everything on this page "
                                             "from the Home Page settings.",
                                     date_modified=now)

    home_category.setting_set.create(name="Feature 1 Heading",
                                     content="Feature 1",
                                     date_modified=now)

    home_category.setting_set.create(name="Feature 1 Body",
                                     content="Use these features to brag about all of the things users can do with "
                                             "your instance of Tethys Portal.",
                                     date_modified=now)

    home_category.setting_set.create(name="Feature 1 Image",
                                     content="/static/tethys_portal/images/placeholder.gif",
                                     date_modified=now)

    home_category.setting_set.create(name="Feature 2 Heading",
                                     content="Feature 2",
                                     date_modified=now)

    home_category.setting_set.create(name="Feature 2 Body",
                                     content="Describe the apps and tools that your Tethys Portal provides and add"
                                             "custom pictures to each feature as a finishing touch.",
                                     date_modified=now)

    home_category.setting_set.create(name="Feature 2 Image",
                                     content="/static/tethys_portal/images/placeholder.gif",
                                     date_modified=now)

    home_category.setting_set.create(name="Feature 3 Heading",
                                     content="Feature 3",
                                     date_modified=now)

    home_category.setting_set.create(name="Feature 3 Body",
                                     content="You can change the color theme and branding of your Tethys Portal in a "
                                             "jiffy. Visit the Site Admin settings from the user menu and select "
                                             "General Settings.",
                                     date_modified=now)

    home_category.setting_set.create(name="Feature 3 Image",
                                     content="/static/tethys_portal/images/placeholder.gif",
                                     date_modified=now)

    home_category.setting_set.create(name="Call to Action",
                                     content="Ready to get started?",
                                     date_modified=now)

    home_category.setting_set.create(name="Call to Action Button",
                                     content="Start Using Tethys!",
                                     date_modified=now)

    home_category.save()


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



