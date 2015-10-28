# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tethys_services.models


class Migration(migrations.Migration):

    dependencies = [
        ('tethys_services', '0007_spatialdatasetservice_public_endpoint'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasetservice',
            name='public_endpoint',
            field=models.CharField(blank=True, max_length=1024, validators=[tethys_services.models.validate_dataset_service_endpoint]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='webprocessingservice',
            name='public_endpoint',
            field=models.CharField(blank=True, max_length=1024, validators=[tethys_services.models.validate_wps_service_endpoint]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='spatialdatasetservice',
            name='public_endpoint',
            field=models.CharField(blank=True, max_length=1024, validators=[tethys_services.models.validate_spatial_dataset_service_endpoint]),
            preserve_default=True,
        ),
    ]
