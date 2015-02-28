#!/usr/local/bin/python
# coding=utf-8

from django.db import models
from django.utils.translation import ugettext as _
from imagekit.models import ProcessedImageField, ImageSpecField
from pilkit.processors import ResizeToFit
from django.contrib.auth.models import User

# Create your models here.

class Photo(models.Model):
    '''Basic Photo Model'''
    title = models.CharField (
        verbose_name = _(u'名称'),
        help_text = _(u'不超过 255 个字符'),
        max_length = 255
    )
    width = models.IntegerField (
        verbose_name = _(u'宽度'),
        help_text = _(u'占用的栏数, 取值1-4'),
        default=1
    )
    xlarge_image = ProcessedImageField (
        verbose_name = _(u'大图'),
        help_text = _(u'长宽都要大于 2880'),
        upload_to='photos/images/%Y/%m/%d',
        processors=[ResizeToFit(2880, 2880, False)],
        format='JPEG',
        options={'quality': 80}
    )
    large_image = ImageSpecField (
        source = 'xlarge_image',
        processors=[ResizeToFit(1920, 1920, False)],
        format='JPEG'
    )
    medium_image = ImageSpecField (
        source = 'xlarge_image',
        processors=[ResizeToFit(1024, 1024, False)],
        format='JPEG'
    )
    small_image = ImageSpecField (
        source = 'xlarge_image',
        processors=[ResizeToFit(512, 512, False)],
        format='JPEG'
    )
    uploader = models.ForeignKey(User, verbose_name=_(u'上传者'))

    def __unicode__(self):
        return u"t:%s w:%s" % (self.title, self.width)

