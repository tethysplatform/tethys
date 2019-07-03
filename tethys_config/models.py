"""
********************************************************************************
* Name: models.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
from django.db import models
from tethys_services.models import validate_url


class SettingsCategory(models.Model):
    name = models.TextField(max_length=30)

    class Meta:
        verbose_name = 'Settings Category'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.name


class Setting(models.Model):
    name = models.TextField(max_length=30)
    content = models.TextField(max_length=500, blank=True)
    date_modified = models.DateTimeField('date modified', auto_now=True)
    category = models.ForeignKey(SettingsCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @classmethod
    def as_dict(cls):
        all_settings = cls.objects.all()

        settings_dict = dict()

        for setting in all_settings:
            code_name = setting.name.lower().replace(' ', '_')
            settings_dict[code_name] = setting.content

        return settings_dict


class AppProxyInstance(models.Model):
    """
    ORM for App Proxy which allows you to redirect an app to another host
    """

    name = models.CharField(max_length=100, unique=True)
    endpoint = models.CharField(max_length=1024, validators=[validate_url])
    logo_url = models.CharField(max_length=100, validators=[validate_url], blank=True)
    description = models.TextField(max_length=2048, blank=True)

    class Meta:
        verbose_name = 'App Proxy Instance'
        verbose_name_plural = 'App Proxy Instances'

    def __str__(self):
        return self.name
