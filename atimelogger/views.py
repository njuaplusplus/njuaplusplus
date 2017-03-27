#!/usr/bin/env python
# coding=utf-8

from django.shortcuts import render
from .models import Interval, ATimeLoggerProfile
from django.utils import timezone
import datetime


def intervals_view(request):
    """
    TODO: set the date according to each user's timezone. At present, all use the default timezone.
    """
    today = datetime.date.today()
    # start_time = timezone.make_aware(datetime.datetime(year=today.year, month=today.month, day=today.day))
    intervals = Interval.objects.filter(start_time__date=today).order_by('-start_time')
    user_with_intervals = []
    profiles = ATimeLoggerProfile.objects.all()
    for profile in profiles:
        user_with_intervals.append((profile.user, intervals.filter(profile=profile)))
    return render(
        request,
        'atimelogger/intervals.html',
        {
            'user_with_intervals': user_with_intervals,
        }
    )
