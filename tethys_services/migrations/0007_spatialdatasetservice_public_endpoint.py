# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tethys_services.models


class Migration(migrations.Migration):

    dependencies = [
        ('tethys_services', '0006_auto_20150729_1551'),
    ]

    operations = [
        migrations.AddField(
            model_name='spatialdatasetservice',
            name='public_endpoint',
            field=models.CharField(blank=True, max_length=1024, validators=[tethys_services.models.validate_dataset_service_endpoint]),
            preserve_default=True,
        ),
    ]
