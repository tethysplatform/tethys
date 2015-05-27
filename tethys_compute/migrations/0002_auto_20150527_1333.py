# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
import tethys_compute.utilities


class Migration(migrations.Migration):

    dependencies = [
        ('tethys_compute', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tethysjob',
            old_name='group',
            new_name='label',
        ),
        migrations.RemoveField(
            model_name='condorjob',
            name='ami',
        ),
        migrations.RemoveField(
            model_name='condorjob',
            name='scheduler',
        ),
        migrations.RemoveField(
            model_name='tethysjob',
            name='status',
        ),
        migrations.RemoveField(
            model_name='tethysjob',
            name='submission_time',
        ),
        migrations.AddField(
            model_name='condorjob',
            name='attributes',
            field=tethys_compute.utilities.DictionaryField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='condorjob',
            name='condorpy_template_name',
            field=models.CharField(max_length=256, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='condorjob',
            name='executable',
            field=models.CharField(default='', max_length=256),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tethysjob',
            name='_status',
            field=models.CharField(default=b'PEN', max_length=3, choices=[(b'PEN', b'Pending'), (b'SUB', b'Submitted'), (b'RUN', b'Running'), (b'COM', b'Complete'), (b'ERR', b'Error')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tethysjob',
            name='execute_time',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tethysjob',
            name='completion_time',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tethysjob',
            name='creation_time',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 27, 13, 32, 47, 846337, tzinfo=utc)),
            preserve_default=True,
        ),
    ]
