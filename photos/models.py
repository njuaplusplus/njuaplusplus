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
        help_text = _(u' '),
        max_length = 255
    )
    large_image = ProcessedImageField (
        verbose_name = _(u'大图'),
        upload_to='photos/images/%Y/%m/%d',
        processors=[ResizeToFit(1920, 1920, False)],
        format='JPEG',
        options={'quality': 80}
    )
    small_image = ImageSpecField (
        source = 'large_image',
        processors=[ResizeToFit(512, 512, False)],
        format='JPEG'
    )
    uploader = models.ForeignKey(User, verbose_name=_(u'上传者'))

