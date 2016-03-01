# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tethys_compute.utilities


class Migration(migrations.Migration):

    dependencies = [
        ('tethys_compute', '0005_auto_20150914_1712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tethysjob',
            name='extended_properties',
            field=tethys_compute.utilities.DictionaryField(default=b'', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tethysjob',
            name='workspace',
            field=models.CharField(default=b'', max_length=1024),
            preserve_default=True,
        ),
    ]
