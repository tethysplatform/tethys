# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tethys_compute', '0004_auto_20150812_1915'),
    ]

    operations = [
        migrations.AlterField(
            model_name='condorjob',
            name='scheduler',
            field=models.ForeignKey(blank=True, to='tethys_compute.Scheduler', null=True),
            preserve_default=True,
        ),
    ]
