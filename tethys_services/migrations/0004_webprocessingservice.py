# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tethys_services', '0003_spatialdatasetservice'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebProcessingService',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30)),
                ('endpoint', models.CharField(max_length=1024)),
                ('username', models.CharField(max_length=100, blank=True)),
                ('password', models.CharField(max_length=100, blank=True)),
            ],
            options={
                'verbose_name': 'Web Processing Service',
                'verbose_name_plural': 'Web Processing Services',
            },
            bases=(models.Model,),
        ),
    ]
