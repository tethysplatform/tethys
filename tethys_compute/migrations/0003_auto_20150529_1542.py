# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tethys_compute.utilities


class Migration(migrations.Migration):

    dependencies = [
        ('tethys_compute', '0002_initialize_settings'),
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
            model_name='condorjob',
            name='tethysjob_ptr',
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
            field=tethys_compute.utilities.DictionaryField(default=b''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='condorjob',
            name='cluster_id',
            field=models.IntegerField(default=0, blank=True),
            preserve_default=True,
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
            model_name='condorjob',
            name='num_jobs',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='condorjob',
            name='remote_id',
            field=models.CharField(max_length=32, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='condorjob',
            name='remote_input_files',
            field=tethys_compute.utilities.ListField(default=b''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='condorjob',
            name='tethys_job',
            field=models.OneToOneField(related_name='child', primary_key=True, default='', serialize=False, to='tethys_compute.TethysJob'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='condorjob',
            name='working_directory',
            field=models.CharField(max_length=512, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tethysjob',
            name='_status',
            field=models.CharField(default=b'PEN', max_length=3, choices=[(b'PEN', b'Pending'), (b'SUB', b'Submitted'), (b'RUN', b'Running'), (b'COM', b'Complete'), (b'ERR', b'Error'), (b'ABT', b'Aborted')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tethysjob',
            name='description',
            field=models.CharField(default=b'', max_length=1024, blank=True),
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
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=True,
        ),
    ]
