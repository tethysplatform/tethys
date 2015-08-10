# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tethys_services.models


class Migration(migrations.Migration):

    dependencies = [
        ('tethys_services', '0005_auto_20150424_2126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datasetservice',
            name='endpoint',
            field=models.CharField(max_length=1024, validators=[tethys_services.models.validate_dataset_service_endpoint]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='spatialdatasetservice',
            name='endpoint',
            field=models.CharField(max_length=1024, validators=[tethys_services.models.validate_spatial_dataset_service_endpoint]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='webprocessingservice',
            name='endpoint',
            field=models.CharField(max_length=1024, validators=[tethys_services.models.validate_wps_service_endpoint]),
            preserve_default=True,
        ),
    ]
