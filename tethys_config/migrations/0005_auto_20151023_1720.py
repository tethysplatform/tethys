# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
from django.db import models, migrations


def settings12to13(apps, schema_editor):
    """
    Update with new settings introduced in 1.3 which include:

    * Text Color
    * Hover Text Color
    * Apps Library Background Color
    * Logo Height and Padding Settings
    """
    # Figure out what time it is right now
    now = timezone.now()

    # Get current settings
    Setting = apps.get_model('tethys_config', 'Setting')
    all_settings = Setting.objects.all()

    # Remove any settings that already exist
    SettingsCategory = apps.get_model('tethys_config', 'SettingsCategory')
    general_category = SettingsCategory.objects.get(name="General Settings")

    primary_text_color = False
    primary_hover_color = False
    secondary_text_color = False
    secondary_hover_color = False
    background_color = False
    brand_image_height = False
    brand_image_width = False
    brand_image_padding = False


    for setting in all_settings:
        if setting.name == 'Primary Text Color':
            primary_text_color = True
        if setting.name == 'Primary Text Hover Color':
            primary_hover_color = True
        if setting.name == 'Secondary Text Color':
            secondary_text_color = True
        if setting.name == 'Secondary Text Hover Color':
            secondary_hover_color = True
        if setting.name == 'Background Color':
            background_color = True
        if setting.name == 'Brand Image Height':
            brand_image_height = True
        if setting.name == 'Brand Image Width':
            brand_image_width = True
        if setting.name == 'Brand Image Padding':
            brand_image_padding = True

    if not primary_text_color:
        general_category.setting_set.create(name="Primary Text Color",
                                            content="",
                                            date_modified=now)

    if not primary_hover_color:
        general_category.setting_set.create(name="Primary Text Hover Color",
                                            content="",
                                            date_modified=now)

    if not secondary_text_color:
        general_category.setting_set.create(name="Secondary Text Color",
                                            content="",
                                            date_modified=now)

    if not secondary_hover_color:
        general_category.setting_set.create(name="Secondary Text Hover Color",
                                            content="",
                                            date_modified=now)

    if not background_color:
        general_category.setting_set.create(name="Background Color",
                                            content="",
                                            date_modified=now)

    if not brand_image_height:
        general_category.setting_set.create(name="Brand Image Height",
                                            content="",
                                            date_modified=now)

    if not brand_image_width:
        general_category.setting_set.create(name="Brand Image Width",
                                            content="",
                                            date_modified=now)

    if not brand_image_padding:
        general_category.setting_set.create(name="Brand Image Padding",
                                            content="",
                                            date_modified=now)

    general_category.save()


class Migration(migrations.Migration):

    dependencies = [
        ('tethys_config', '0004_auto_20150424_2050'),
    ]

    operations = [
        migrations.RunPython(settings12to13),
    ]
