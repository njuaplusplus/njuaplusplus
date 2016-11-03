#!/usr/local/bin/python
# coding=utf-8

from django.db import models
from django.utils.translation import ugettext as _
from imagekit.models import ProcessedImageField, ImageSpecField
from pilkit.processors import ResizeToFit
from django.contrib.auth.models import User


# Create your models here.

class Photo(models.Model):
    """Basic Photo Model"""
    title = models.CharField(
        verbose_name=_('名称'),
        help_text=_('不超过 255 个字符'),
        max_length=255
    )
    width = models.IntegerField(
        verbose_name=_('宽度'),
        help_text=_('占用的栏数, 取值1-4'),
        default=1
    )
    origin_image = models.CharField(
        verbose_name=_('原图的七牛key'),
        help_text=_('不超过 255 个字符'),
        max_length=255
    )
    large_image = models.CharField(
        verbose_name=_('1920x的七牛key'),
        help_text=_('不超过 255 个字符'),
        max_length=255
    )
    small_image = models.CharField(
        verbose_name=_('512x的七牛key'),
        help_text=_('不超过 255 个字符'),
        max_length=255
    )
    uploader = models.ForeignKey(User, verbose_name=_('上传者'))
    date_upload = models.DateTimeField(
        verbose_name=_('上传日期'),
        help_text=_(' ')
    )

    def __str__(self):
        return "t:%s w:%s" % (self.title, self.width)
