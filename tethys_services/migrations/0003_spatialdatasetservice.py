# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tethys_services', '0002_auto_20150119_1756'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpatialDatasetService',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30)),
                ('engine', models.CharField(default=b'tethys_dataset_services.engines.GeoServerSpatialDatasetEngine', max_length=200, choices=[(b'tethys_dataset_services.engines.GeoServerSpatialDatasetEngine', b'GeoServer')])),
                ('endpoint', models.CharField(max_length=1024)),
                ('apikey', models.CharField(max_length=100, blank=True)),
                ('username', models.CharField(max_length=100, blank=True)),
                ('password', models.CharField(max_length=100, blank=True)),
            ],
            options={
                'verbose_name': 'Spatial Dataset Service',
                'verbose_name_plural': 'Spatial Dataset Services',
            },
            bases=(models.Model,),
        ),
    ]
