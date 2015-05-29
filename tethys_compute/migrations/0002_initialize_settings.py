# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from . import initialize_settings, clear_settings

class Migration(migrations.Migration):

    dependencies = [
        ('tethys_compute', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(clear_settings),
        migrations.RunPython(initialize_settings, reverse_code=clear_settings),
    ]