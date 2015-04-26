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

    # Get current settings
    Setting = apps.get_model('tethys_config', 'Setting')
    all_settings = Setting.objects.all()

    # Remove any settings that already exist
    SettingsCategory = apps.get_model('tethys_config', 'SettingsCategory')
    general_category = SettingsCategory.objects.get(name="General Settings")

    for setting in all_settings:
        if setting == 'Apps Library Title':
            general_category.setting_set.create(name='Apps Library Title',
                                                content='Apps Library',
                                                date_modified=now)

    general_category.save()


class Migration(migrations.Migration):

    dependencies = [
        ('tethys_config', '0003_auto_20141223_2244'),
    ]

    operations = [
        migrations.RunPython(settings10to11),
    ]
