# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings
from django.utils.timezone import utc
from . import initialize_settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cluster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_name', models.CharField(default=b'tethys_default', unique=True, max_length=30)),
                ('_size', models.IntegerField(default=1)),
                ('_status', models.CharField(default=b'STR', max_length=3, choices=[(b'STR', b'Starting'), (b'RUN', b'Running'), (b'STP', b'Stopped'), (b'UPD', b'Updating'), (b'DEL', b'Deleting'), (b'ERR', b'Error')])),
                ('_cloud_provider', models.CharField(default=b'AWS', max_length=3, choices=[(b'AWS', b'Amazon Web Services'), (b'AZR', b'Microsoft Azure')])),
                ('_master_image_id', models.CharField(max_length=9, null=True, blank=True)),
                ('_node_image_id', models.CharField(max_length=9, null=True, blank=True)),
                ('_master_instance_type', models.CharField(max_length=20, null=True, blank=True)),
                ('_node_instance_type', models.CharField(max_length=20, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(max_length=30)),
                ('content', models.TextField(max_length=500, blank=True)),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name=b'date modified')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SettingsCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
            ],
            options={
                'verbose_name': 'Settings Category',
                'verbose_name_plural': 'Settings',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TethysJob',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('group', models.CharField(max_length=30)),
                ('creation_time', models.DateTimeField(default=datetime.datetime(2015, 4, 6, 22, 37, 42, 933728, tzinfo=utc))),
                ('submission_time', models.DateTimeField()),
                ('completion_time', models.DateTimeField()),
                ('status', models.CharField(default=b'PEN', max_length=3, choices=[(b'PEN', b'Pending'), (b'SUB', b'Submitted'), (b'RUN', b'Running'), (b'COM', b'Complete'), (b'ERR', b'Error')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CondorJob',
            fields=[
                ('tethysjob_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tethys_compute.TethysJob')),
                ('scheduler', models.CharField(max_length=12)),
                ('ami', models.CharField(max_length=9)),
            ],
            options={
            },
            bases=('tethys_compute.tethysjob',),
        ),
        migrations.AddField(
            model_name='tethysjob',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='setting',
            name='category',
            field=models.ForeignKey(to='tethys_compute.SettingsCategory'),
            preserve_default=True,
        ),
        migrations.RunPython(initialize_settings),
    ]
