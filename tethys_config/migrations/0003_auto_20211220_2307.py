# Generated by Django 2.2.14 on 2021-12-20 23:07

from django.db import migrations

from tethys_config.init import tethys4_site_settings


class Migration(migrations.Migration):

    dependencies = [
        ('tethys_config', '0002_auto_20200410_1731'),
    ]

    operations = [
        migrations.RunPython(tethys4_site_settings, lambda a,s: None)
    ]
