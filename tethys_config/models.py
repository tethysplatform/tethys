from django.db import models


class SettingsCategory(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        verbose_name = 'Settings Category'
        verbose_name_plural = 'Settings'

    def __unicode__(self):
        return self.name


class Setting(models.Model):
    name = models.CharField(max_length=30)
    content = models.CharField(max_length=500)
    date_modified = models.DateTimeField('date modified', auto_now=True)
    category = models.ForeignKey(SettingsCategory)

    def __unicode__(self):
        return self.name
