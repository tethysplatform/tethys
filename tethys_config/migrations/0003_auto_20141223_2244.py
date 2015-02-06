# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tethys_config', '0002_auto_20141029_1848'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='settingscategory',
            options={'verbose_name': 'Settings Category', 'verbose_name_plural': 'Site Settings'},
        ),
        migrations.AlterField(
            model_name='setting',
            name='content',
            field=models.TextField(max_length=500, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='setting',
            name='date_modified',
            field=models.DateTimeField(auto_now=True, verbose_name=b'date modified'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='setting',
            name='name',
            field=models.TextField(max_length=30),
            preserve_default=True,
        ),
    ]
