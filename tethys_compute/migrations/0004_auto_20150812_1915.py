# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tethys_compute.utilities


class Migration(migrations.Migration):

    dependencies = [
        ('tethys_compute', '0003_auto_20150529_1651'),
    ]

    operations = [
        migrations.CreateModel(
            name='BasicJob',
            fields=[
                ('tethysjob_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tethys_compute.TethysJob')),
            ],
            options={
            },
            bases=('tethys_compute.tethysjob',),
        ),
        migrations.CreateModel(
            name='Scheduler',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=1024)),
                ('host', models.CharField(max_length=1024)),
                ('username', models.CharField(max_length=1024, null=True, blank=True)),
                ('password', models.CharField(max_length=1024, null=True, blank=True)),
                ('private_key_path', models.CharField(max_length=1024, null=True, blank=True)),
                ('private_key_pass', models.CharField(max_length=1024, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='condorjob',
            name='working_directory',
        ),
        migrations.AddField(
            model_name='condorjob',
            name='scheduler',
            field=models.ForeignKey(default=1, to='tethys_compute.Scheduler'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tethysjob',
            name='_subclass',
            field=models.CharField(default=b'basicjob', max_length=30),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tethysjob',
            name='extended_properties',
            field=tethys_compute.utilities.DictionaryField(default=b''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tethysjob',
            name='workspace',
            field=models.CharField(default=b'/Users/sdc50/.tethyscluster/workspace', max_length=1024),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='condorjob',
            name='condorpy_template_name',
            field=models.CharField(max_length=1024, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='condorjob',
            name='executable',
            field=models.CharField(max_length=1024),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='condorjob',
            name='tethys_job',
            field=models.OneToOneField(primary_key=True, serialize=False, to='tethys_compute.TethysJob'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tethysjob',
            name='_status',
            field=models.CharField(default=b'PEN', max_length=3, choices=[(b'PEN', b'Pending'), (b'SUB', b'Submitted'), (b'RUN', b'Running'), (b'COM', b'Complete'), (b'ERR', b'Error'), (b'ABT', b'Aborted'), (b'VAR', b'Various'), (b'VCP', b'Various-Complete')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tethysjob',
            name='description',
            field=models.CharField(default=b'', max_length=2048, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tethysjob',
            name='label',
            field=models.CharField(max_length=1024),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tethysjob',
            name='name',
            field=models.CharField(max_length=1024),
            preserve_default=True,
        ),
    ]
