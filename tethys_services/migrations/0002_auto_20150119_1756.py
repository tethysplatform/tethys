# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tethys_services', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datasetservice',
            name='engine',
            field=models.CharField(default=b'tethys_dataset_services.engines.CkanDatasetEngine', max_length=200, choices=[(b'tethys_dataset_services.engines.CkanDatasetEngine', b'CKAN'), (b'tethys_dataset_services.engines.HydroShareDatasetEngine', b'HydroShare')]),
            preserve_default=True,
        ),
    ]
