# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from ..init import initial_settings, reverse_init


class Migration(migrations.Migration):

    dependencies = [
        ('tethys_config', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(initial_settings, reverse_init),
    ]
