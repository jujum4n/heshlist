from __future__ import unicode_literals
from django.db import models


class YtChannel(models.Model):
    name = models.CharField(max_length=512, unique=True)
    channel_id = models.CharField(max_length=256, unique=True)
    
    def __unicode__(self):
        return self.name


class YtVideo(models.Model):
    ytchannel = models.ForeignKey(YtChannel)
    title = models.CharField(max_length=1024)
    video_id = models.CharField(max_length=128, unique=True)
    url = models.URLField()
    duration = models.CharField(max_length=128)
    posted_date = models.CharField(max_length=128)
    
    def __unicode__(self):
        return self.title