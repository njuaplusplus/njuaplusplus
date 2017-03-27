#!/usr/bin/env python
# coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.utils import timezone
import datetime


class ATimeLoggerProfile(models.Model):
    user = models.OneToOneField(User, related_name='atimelogger_profile')
    username = models.CharField(
        verbose_name=_('atimelogger 的用户名'),
        help_text=_('不超过 255 个字符'),
        max_length=255
    )
    password = models.CharField(
        verbose_name=_('atimelogger 的密码'),
        help_text=_('不超过 255 个字符'),
        max_length=255
    )
    access_token = models.CharField(
        verbose_name=_('atimelogger 的 access token'),
        help_text=_('不超过 255 个字符'),
        max_length=255,
        blank=True
    )
    refresh_token = models.CharField(
        verbose_name=_('atimelogger 的 refresh token'),
        help_text=_('不超过 255 个字符'),
        max_length=255,
        blank=True
    )
    token_time = update_time = models.DateTimeField(
        verbose_name=_('token 更新时间'),
        help_text=_(' '),
        default=timezone.make_aware(datetime.datetime(1970, 1, 1), timezone.utc)
    )
    update_time = models.DateTimeField(
        verbose_name=_('数据更新时间'),
        help_text=_(' '),
        default = timezone.make_aware(datetime.datetime(1970, 1, 1), timezone.utc)
    )

    def __str__(self):
        return '%s: %s' % (self.user, self.username,)


class ActivityType(models.Model):
    profile = models.ForeignKey(
        ATimeLoggerProfile,
        on_delete=models.CASCADE
    )
    guid = models.CharField(
        verbose_name=_('type 的唯一标示符'),
        help_text=_('不超过 255 个字符'),
        max_length=255
    )
    name = models.CharField(
        verbose_name=_('type 的名称'),
        help_text=_('不超过 255 个字符'),
        max_length=255
    )
    color = models.CharField(
        verbose_name=_('type 的颜色'),
        help_text=_('不超过 255 个字符'),
        max_length=255
    )
    image_id = models.CharField(
        verbose_name=_('type 的图像'),
        help_text=_('不超过 255 个字符'),
        max_length=255
    )

    def __str__(self):
        return '%s: %s' % (self.profile, self.name)


class Interval(models.Model):
    profile = models.ForeignKey(
        ATimeLoggerProfile,
        on_delete=models.CASCADE
    )
    type = models.ForeignKey(
        ActivityType,
        on_delete=models.CASCADE
    )
    guid = models.CharField(
        verbose_name=_('interval 的唯一标示符'),
        help_text=_('不超过 255 个字符'),
        max_length=255
    )
    comment = models.CharField(
        verbose_name=_('interval 的备注'),
        help_text=_('不超过 255 个字符'),
        max_length=255
    )
    start_time = models.DateTimeField(
        verbose_name=_('开始时间'),
        help_text=_(' ')
    )
    end_time = models.DateTimeField(
        verbose_name=_('结束时间'),
        help_text=_(' ')
    )

    def __str__(self):
        return '%s: %s-%s' % (self.type, self.start_time, self.end_time)
