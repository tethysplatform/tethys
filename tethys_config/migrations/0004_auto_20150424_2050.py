# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
from django.db import models, migrations


def settings10to11(apps, schema_editor):
    """
    Update with new settings introduced in 1.1 which include:

    * Apps Library Title
    """
    # Figure out what time it is right now
    now = timezone.now()

    # The settings to add and their default values
    general_setting_defaults = {'Apps Library Title': 'Apps Library'}

    # Assumed values to add
    general_settings_to_add = ['Apps Library Title', ]

    # Get current settings
    Setting = apps.get_model('tethys_config', 'Setting')
    all_settings = Setting.objects.all()

    # Remove any settings that already exist
    for setting in all_settings:
        if setting in general_settings_to_add:
            general_settings_to_add.remove(setting)

    # Add remaining settings to the database
    SettingsCategory = apps.get_model('tethys_config', 'SettingsCategory')
    general_category = SettingsCategory.objects.get(name="General Settings")

    for general_setting_to_add in general_settings_to_add:
        general_category.setting_set.create(name=general_setting_to_add,
                                            content=general_setting_defaults[general_setting_to_add],
                                            date_modified=now)

    general_category.save()


class Migration(migrations.Migration):

    dependencies = [
        ('tethys_config', '0003_auto_20141223_2244'),
    ]

    operations = [
        migrations.RunPython(settings10to11),
    ]
