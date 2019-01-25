# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-17 13:44
from django.db import migrations, models
import django.db.models.deletion
from ..init import initial_settings, reverse_init


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SettingsCategory',
            options={'verbose_name': 'Settings Category', 'verbose_name_plural': 'Site Settings'},
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=30)),
                ('content', models.TextField(blank=True, max_length=500)),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='date modified')),
                ('category', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='tethys_config.SettingsCategory'
                )),
            ],
        ),
        migrations.RunPython(initial_settings, reverse_init),
    ]
