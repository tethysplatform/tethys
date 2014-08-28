from django.db import models


class HomePageContent(models.Model):
    name = models.CharField(max_length=30)
    content = models.CharField(max_length=500)
    date_modified = models.DateTimeField('date modified')

    def __unicode__(self):
        return self.content